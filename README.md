stanford_pipeline
=================

Program to run scraped news stories through Stanford's CoreNLP program.

The program pulls stories added to the database within the past day and that
aren't currently parsed using CoreNLP. Once parsed, the parsetrees are placed
back into the database. The program is currently set to proccess the first six
sentences of a story.

This program makes extensive use of Brendan O'Connor's
[wrapper](https://github.com/brendano/stanford-corepywrapper) for CoreNLP. The
current install comes from my (John Beieler)
[fork](https://github.com/johnb30/stanford-corepywrapper). The config file for
CoreNLP makes use of the shift-reduce parser introduced in CoreNLP 3.4.

CoreNLP Setup
--------

This pipeline depends on having CoreNLP 3.4 with the shift-reduce parser.
Download the models like this:

```
wget http://nlp.stanford.edu/software/stanford-corenlp-full-2014-06-16.zip
unzip stanford-corenlp-full-2014-06-16.zip
mv stanford-corenlp-full-2014-06-16 stanford-corenlp
cd stanford-corenlp
wget http://nlp.stanford.edu/software/stanford-srparser-2014-07-01-models.jar
```

If errors persist, try changing the path in `default_config.ini` from the
relative path `~/stanford-corenlp` to the full path (e.g.)
`/home/ahalterman/stanford-corenlp`.

Configuration
-----------

The `default_config.ini` file has several options that can be changed,
including the MongoDB database and collection of stories to process and whether
all unparsed stories should be processed or just the stories added in the last
day.

Usage
-----

`python process.py`

Up to a minute of `[Errno 111] Connection refused` messages are normal during
startup.
