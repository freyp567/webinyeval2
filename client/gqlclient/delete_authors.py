"""
delete authors
missing GraphQL feature to truncate table - so use this script to drop all AuthorInfo items
"""

import os
from datetime import datetime
import requests
import csv
import uuid
import argparse
from pathlib import Path

import logging 
LOG_FORMAT = "%(asctime)-15s %(levelname)-8s %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"
LOGLEVEL = os.environ.get('LOGLEVEL') or logging.INFO
LOG = None

API_URL = os.environ["API_URL"]
MANAGE_URL = API_URL + "/cms/manage/de-DE"
READ_URL = API_URL + "/cms/read/de-DE"
PREVIEW_URL = API_URL + "/cms/preview/de-DE/"
API_KEY = os.environ["API_KEY"]


def setupLogging(log_path):
    global LOG
    #logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    logger = logging.getLogger()
    handler = logging.FileHandler(log_path.as_posix())
    handler.setLevel(LOGLEVEL)    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOGLEVEL)
    LOG = logging.getLogger('delete_authors')


def getHeaders():
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + API_KEY,
        "Connection": "keep-alive",
        #User-Agent': 'add_bookitem',
        "Origin": API_URL
    }
    return headers


def delete_authors():
    url = PREVIEW_URL
    query = "{ listAuthorInfos {data { id } }}"
    response = requests.post(url, json={'query': query}, headers=getHeaders())
    if response.status_code == 200:
        result = response.json()
        errors = result.get('errors')
        if errors and errors[0]:
            for error_info in errors:
                LOG.error(f"publish authorInfo {id} failed - {error_info}")
            raise ValueError(f"delete failed")

        deleted = 0
        items = result['data']['listAuthorInfos']['data']
        for authorInfoItem in items:
            delete_author_item(authorInfoItem['id'])
            deleted += 1
        LOG.info(f"deleted totally {deleted} AuthorInfo items")
        return deleted

    else:
        raise ValueError(f"delete failed, status_code={response.status_code}")


def delete_author_item(idAuthor):
    url = MANAGE_URL
    mutation = """\
mutation DeleteAuthorInfo {
  deleteAuthorInfo(revision:"%s") { 
    error { code message data }
  }
} """ % idAuthor
    response = requests.post(url, json={'query': mutation}, headers=getHeaders())
    if response.status_code == 200:
        result = response.json()
        error = result['data']['deleteAuthorInfo']['error']
        if error:
            LOG.error(f"delete authorInfo {id} failed - {error}")
            raise ValueError(f"delete item failed")

    else:
        raise ValueError(f"delete item failed, status_code={response.status_code}")



def main():
    now = datetime.now()
    logPath = Path(__file__).with_suffix('.log')
    setupLogging(logPath)
    LOG.info(f"delete authors ...")
    
    LOG.info(f"start delete {now.isoformat()}")

    # batching of 10 items by default?
    # so repeat until no more AuthorInfo items found
    loop_count = 0
    total_deleted = 0
    while True:
        loop_count += 1
        assert loop_count < 200, "reached loop_count"  # avoid endless loop (and AWS costs)
        # assuming no more than 2000 AuthorItems this should be enough (for batches of 10)
        try:
            deleted = delete_authors()
            if deleted > 0:
                total_deleted += deleted
            else:
                # all done
                break
        except Exception:
            LOG.exception('delete_authors failed')
            break
    LOG.info(f"deleted totally {total_deleted} AuthorInfo items")
    LOG.info('\n')
    print("result see {log_path}")
    print("done.")


main()

