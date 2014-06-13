# -*- encoding=utf-8 -*-

import os
import glob
import parser
import logging
import datetime
from pymongo import MongoClient
from ConfigParser import ConfigParser


def make_conn():
    """
    Function to establish a connection to a local MonoDB instance.

    Returns
    -------

    collection: pymongo.collection.Collection.
                Collection within MongoDB that holds the scraped news stories.

    """
    client = MongoClient()
    database = client.event_scrape
    collection = database['stories']
    return collection


def query_today(collection, date):
    """
    Function to query the MongoDB instance and obtain results for the desired
    date range. The query constructed is: greater_than_date > results
    < less_than_date.

    Parameters
    ----------

    collection: pymongo.collection.Collection.
                Collection within MongoDB that holds the scraped news stories.

    less_than_date: Datetime object.
                    Date for which results should be older than. For example,
                    if the date running is the 25th, and the desired date is
                    the 24th, then the `less_than_date` is the 25th.

    greater_than_date: Datetime object.
                        Date for which results should be older than. For
                        example, if the date running is the 25th, and the
                        desired date is the 24th, then the `greater_than_date`
                        is the 23rd.

    write_file: Boolean.
                Option indicating whether to write the results from the web
                scraper to an intermediate file. Defaults to false.

    Returns
    -------

    posts: List.
            List of dictionaries of results from the MongoDB query.


    final_out: String.
                If `write_file` is True, this contains a string representation
                of the query results. Otherwise, contains an empty string.

    """

    logger = logging.getLogger('stanford')
    gt_date = date - datetime.timedelta(days=1)
    posts = collection.find({"$and": [{"date_added": {"$lte": date}},
                                      {"date_added": {"$gt": gt_date}},
                                      {"stanford": 0}]})
    logger.info('Returning {} total stories.'.format(posts.count()))
    return posts


def parse_config():
    """Function to parse the config file."""
    config_file = glob.glob('config.ini')
    cparser = ConfigParser()
    if config_file:
        cparser.read(config_file)
        try:
            stanford_dir = cparser.get('StanfordNLP', 'stanford_dir')
            if 'Logging' in cparser.sections():
                log_dir = cparser.get('Logging', 'log_file')
            else:
                log_dir = ''
            return stanford_dir, log_dir
        except Exception, e:
            print 'There was an error parsing the config file. {}'.format(e)
    else:
        cwd = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(cwd, 'default_config.ini')
        cparser.read(config_file)
        try:
            stanford_dir = cparser.get('StanfordNLP', 'stanford_dir')
            if 'Logging' in cparser.sections():
                log_dir = cparser.get('Logging', 'log_file')
            else:
                log_dir = ''
            return stanford_dir, log_dir
        except Exception, e:
            print 'There was an error parsing the config file. {}'.format(e)


def main():
    stanford_dir, log_dir = parse_config()
    #Setup the logging
    logger = logging.getLogger('stanford')
    logger.setLevel(logging.INFO)

    if log_dir:
        fh = logging.FileHandler(log_dir, 'a')
    else:
        fh = logging.FileHandler('stanford.log', 'a')
    formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.info('Running.')

    now = datetime.datetime.utcnow()
    coll = make_conn()
    stories = query_today(coll, now)
    parser.stanford_parse(coll, stories)


if __name__ == '__main__':
    main()
