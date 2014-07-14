stanford_pipeline
=================

Program to run scraped news stories through Stanford's CoreNLP program.

The program pulls stories added to the database within the past day and that
aren't currently parsed using CoreNLP. Once parsed, the parsetrees are placed
back into the database. The program is currently set to proccess the first six
sentences of a story.

Usage
-----

`python process.py`
