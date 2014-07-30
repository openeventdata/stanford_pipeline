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

Usage
-----

`python process.py`
