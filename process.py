# -*- encoding=utf-8 -*-

import os
import glob
import parser
import logging
import datetime
from pymongo import MongoClient
from ConfigParser import ConfigParser


def make_conn(db_auth, db_user, db_pass, db_host=None):
    """
    Function to establish a connection to a local MonoDB instance.

    Parameters
    ----------

    db_auth: String.
                MongoDB database that should be used for user authentication.

    db_user: String.
                Username for MongoDB authentication.

    db_user: String.
                Password for MongoDB authentication.


    Returns
    -------

    collection: pymongo.collection.Collection.
                Collection within MongoDB that holds the scraped news stories.

    """
    if db_host:
        client = MongoClient(db_host)
    else:
        client = MongoClient()
    if db_auth:
        client[db_auth].authenticate(db_user, db_pass)
    database = client.event_scrape
    collection = database['stories']
    return collection


def query_today(collection, date):
    """
    Function to query the MongoDB instance and obtain results for the desired
    date range. Pulls stories that aren't Stanford parsed yet
    (``"stanford: 0"``) and that were added within the last day.

    Parameters
    ----------

    collection: pymongo.collection.Collection.
                Collection within MongoDB that holds the scraped news stories.

    date: String.
            Current date that the program is running.

    Returns
    -------

    posts: pymongo.cursor.Cursor.
            Results from the MongoDB query.

    """

    logger = logging.getLogger('stanford')
    gt_date = date - datetime.timedelta(days=1)
    posts = collection.find({"$and": [{"date_added": {"$lte": date}},
                                      {"date_added": {"$gt": gt_date}},
                                      {"stanford": 0}]})
    logger.info('Returning {} total stories.'.format(posts.count()))
    return posts


def _parse_config(cparser):
    try:
        stanford_dir = cparser.get('StanfordNLP', 'stanford_dir')
        if 'Logging' in cparser.sections():
            log_dir = cparser.get('Logging', 'log_file')
        else:
            log_dir = ''
        if 'Auth' in cparser.sections():
            auth_db = cparser.get('Auth', 'auth_db')
            auth_user = cparser.get('Auth', 'auth_user')
            auth_pass = cparser.get('Auth', 'auth_pass')
            db_host = cparser.get('Auth', 'db_host')
        else:
            auth_db = ''
            auth_user = ''
            auth_pass = ''
            db_host = os.getenv('MONGO_HOST')
        return stanford_dir, log_dir, auth_db, auth_user, auth_pass, db_host
    except Exception, e:
        print 'There was an error parsing the config file. {}'.format(e)
        raise


def parse_config():
    """Function to parse the config file."""
    config_file = glob.glob('config.ini')
    cparser = ConfigParser()
    if config_file:
        cparser.read(config_file)
    else:
        cwd = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(cwd, 'default_config.ini')
        cparser.read(config_file)
    return _parse_config(cparser)


def run():
    stanford_dir, log_dir, db_auth, db_user, db_pass, db_host = parse_config()
    # Setup the logging
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
    coll = make_conn(db_auth, db_user, db_pass)
    stories = query_today(coll, now)
    parser.stanford_parse(coll, stories, stanford_dir)


if __name__ == '__main__':
    run()
