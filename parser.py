# -*- encoding=utf-8 -*-

import re
import logging
from stanford_corenlp_pywrapper import sockwrap


def stanford_parse(coll, stories, stanford):
    """
    Runs stories pulled from the MongoDB instance through CoreNLP. Updates
    the database entry with the parsed sentences. Currently set to run the
    first 6 sentences.

    Parameters
    ----------

    coll: pymongo.collection.Collection.
            Collection within MongoDB that holds the scraped news stories.

    stories: pymongo.cursor.Cursor.
                Stories pulled from the MongoDB instance.

    stanford: String.
                Directory path for Stanford CoreNLP.
    """
    logger = logging.getLogger('stanford')

    logger.info('Setting up CoreNLP.')
    print "\nSetting up StanfordNLP. The program isn't dead. Promise."
    stanford_parser = sockwrap.SockWrap(mode='justparse',
                                        configfile='stanford_config.ini',
                                        corenlp_libdir=stanford)

    total = stories.count()
    print "Stanford setup complete. Starting parse of {} stories...".format(total)
    logger.info('Finished CoreNLP setup.')

    for story in stories:
        print 'Processing story {}'.format(story['_id'])
        logger.info('\tProcessing story {}'.format(story['_id']))

        if story['stanford'] == 1:
            print '\tStory {} already parsed.'.format(story['_id'])
            logger.info('\tStory {} already parsed.'.format(story['_id']))
            pass
        else:
            content = _sentence_segmenter(story['content'])[:7]

            parsed = []
            for sent in content:
                try:
                    stanford_result = stanford_parser.parse_doc(sent)
                    parsed.append(stanford_result['sentences'][0]['parse'])

                except Exception as e:
                    print 'Error on story {}. ¯\_(ツ)_/¯. {}'.format(story['_id'],
                                                                        e)
                    logger.warning('\tError on story {}. {}'.format(story['_id'],
                                                                    e))

            coll.update({"_id": story['_id']}, {"$set": {'parsed_sents': parsed,
                                                         'stanford': 1}})

    print 'Done with StanfordNLP parse...\n\n'
    logger.info('Done with CoreNLP parse.')


def _sentence_segmenter(paragr):
    """
    Function to break a string 'paragraph' into a list of sentences based on
    the following rules:

    1. Look for terminal [.,?,!] followed by a space and [A-Z]
    2. If ., check against abbreviation list ABBREV_LIST: Get the string
    between the . and the previous blank, lower-case it, and see if it is in
    the list. Also check for single-letter initials. If true, continue search
    for terminal punctuation
    3. Extend selection to balance (...) and "...". Reapply termination rules
    4. Add to sentlist if the length of the string is between MIN_SENTLENGTH
    and MAX_SENTLENGTH
    5. Returns sentlist

    Parameters
    ----------

    paragr: String.
            Content that will be split into constituent sentences.

    Returns
    -------

    sentlist: List.
                List of sentences.

    """
    # this is relatively high because we are only looking for sentences that
    # will have subject and object
    MIN_SENTLENGTH = 100
    MAX_SENTLENGTH = 512

    # sentence termination pattern used in sentence_segmenter(paragr)
    terpat = re.compile('[\.\?!]\s+[A-Z\"]')

    # source: LbjNerTagger1.11.release/Data/KnownLists/known_title.lst from
    # University of Illinois with editing
    ABBREV_LIST = ['mrs.', 'ms.', 'mr.', 'dr.', 'gov.', 'sr.', 'rev.', 'r.n.',
                   'pres.', 'treas.', 'sect.', 'maj.', 'ph.d.', 'ed. psy.',
                   'proc.', 'fr.', 'asst.', 'p.f.c.', 'prof.', 'admr.',
                   'engr.', 'mgr.', 'supt.', 'admin.', 'assoc.', 'voc.',
                   'hon.', 'm.d.', 'dpty.',  'sec.', 'capt.', 'c.e.o.',
                   'c.f.o.', 'c.i.o.', 'c.o.o.', 'c.p.a.', 'c.n.a.', 'acct.',
                   'llc.', 'inc.', 'dir.', 'esq.', 'lt.', 'd.d.', 'ed.',
                   'revd.', 'psy.d.', 'v.p.',  'senr.', 'gen.', 'prov.',
                   'cmdr.', 'sgt.', 'sen.', 'col.', 'lieut.', 'cpl.', 'pfc.',
                   'k.p.h.', 'cent.', 'deg.', 'doz.', 'Fahr.', 'Cel.', 'F.',
                   'C.', 'K.', 'ft.', 'fur.',  'gal.', 'gr.', 'in.', 'kg.',
                   'km.', 'kw.', 'l.', 'lat.', 'lb.', 'lb per sq in.', 'long.',
                   'mg.', 'mm.,, m.p.g.', 'm.p.h.', 'cc.', 'qr.', 'qt.', 'sq.',
                   't.', 'vol.',  'w.', 'wt.']

    sentlist = []
    # controls skipping over non-terminal conditions
    searchstart = 0
    terloc = terpat.search(paragr)
    while terloc:
        isok = True
        if paragr[terloc.start()] == '.':
            if (paragr[terloc.start() - 1].isupper() and
                    paragr[terloc.start() - 2] == ' '):
                        isok = False      # single initials
            else:
                # check abbreviations
                loc = paragr.rfind(' ', 0, terloc.start() - 1)
                if loc > 0:
                    if paragr[loc + 1:terloc.start() + 1].lower() in ABBREV_LIST:
                        isok = False
        if paragr[:terloc.start()].count('(') != paragr[:terloc.start()].count(')'):
            isok = False
        if paragr[:terloc.start()].count('"') % 2 != 0:
            isok = False
        if isok:
            if (len(paragr[:terloc.start()]) > MIN_SENTLENGTH and
                    len(paragr[:terloc.start()]) < MAX_SENTLENGTH):
                sentlist.append(paragr[:terloc.start() + 2])
            paragr = paragr[terloc.end() - 1:]
            searchstart = 0
        else:
            searchstart = terloc.start() + 2

        terloc = terpat.search(paragr, searchstart)

    # add final sentence
    if (len(paragr) > MIN_SENTLENGTH and len(paragr) < MAX_SENTLENGTH):
        sentlist.append(paragr)

    return sentlist
