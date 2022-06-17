"""
import authors
from csv format defined / used by BookCatalogue
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
PREVIEW_URL = API_URL + "/cms/preview/de-DE"
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
    #return logging.getLogger('import_authors')
    LOG = logger


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


def import_authors_from_csv(csv_path, args):
    with csv_path.open(mode='r') as csv_f:
        reader = csv.DictReader(csv_f, dialect="excel", delimiter=",")
        for row in reader:
            # _id, author_details, title, isbn, publisher, date_published, rating, bookshelf_id, bookshelf, read, series_details, pages, notes, list_price, anthology, location, read_start, read_end, format, signed, loaned_to, anthology_titles, description, genre, language, date_added, goodreads_book_id, last_goodreads_sync_date, last_update_date, book_uuid, 
            for author_name in row['author_details'].split('|'):
                author_name = author_name.strip()
                assert author_name, "must have author name"
                # author_id? not exported, but author names are not fully unique
                #FIXTHIS - but for time beeing and simplicity assume author names are unique
                author_info = lookup_author(author_name)
                if not author_info:
                    # new so add author info
                    author_info = add_author(author_name)
                    LOG.info(f"created authorInfo for {author_name}")
    return


def lookup_author(author_name):
    url = PREVIEW_URL
    query = """\
{ getAuthorInfo(where:{authorName:"%s"}) { data { authorId } }}""" % (author_name,)
    response = requests.post(url = url, json=query, headers = getHeaders())
    if response.status_code != 200:
        LOG.error(f"failed to lookup author {author_name}")
        return None
    data = response.json()
    if data.get('errors'):
        assert not data['errors'][0]
    print(query, '\n=>\n', data)
    return None


def add_author(author_name):
    author_info = {
        "authorId": str(uuid.uuid4().hex),
        "authorName": author_name
    }
    url = MANAGE_URL
    mutation = """\
mutation CreateAuthorInfo($data:AuthorInfoInput!){
        createAuthorInfo(data:$data)
        {
            data { id entryId meta { status }}
            error { code message data }
        }
    }
    """
    vars = {'data': author_info}

    response = requests.post(url = url, json={'query': mutation, 'variables': vars}, headers = getHeaders())
    if response.status_code != 200:
        LOG.error(f"failed to create author {author_name}")
        return None
    data = response.json()
    if data.get('errors'):
        # not successful
        LOG.error(f"failed to create authorinfo - {data['errors']}")
        raise ValueError("failed to create authorinfo")
    info = data['data']['createAuthorInfo']['data']
    author_info['id'] = info['id']
    author_info['ehtryId'] = info['entryId']
    pub_info = publishAuthorInfo(info['id'])
    return author_info


def publishAuthorInfo(id):
    url = MANAGE_URL
    query = """
mutation {
  publishAuthorInfo(revision: "%s") {
    data { id entryId }
    error {code message data}
  }
}    
    """ % (id)
    request = requests.post(url, json={'query': query}, headers=getHeaders())
    if request.status_code == 200:
        result = request.json()
        errors = result.get('errors')
        if errors and errors[0]:
            for error_info in errors:
                LOG.error(f"publish authorInfo {id} failed - {error_info}")
            raise ValueError(f"Publish failed")
        info = result['data']['publishAuthorInfo']['data']
        return info
    else:
        raise Exception("Publish failed with status_code={}. {}".format(request.status_code, query))



def getArgParser():
    parser = argparse.ArgumentParser(description='parse commandline arguments for import_authors.py')
    parser.add_argument(
            "--csv",
            type=Path,
            default=Path(__file__).absolute().parent / "data" / "export.csv",
            help="Path to the data directory",
        )
    return parser


def main():
    args = getArgParser().parse_args()
    csv_path = args.csv.resolve()
    assert csv_path.is_file(), f"missing csv, not found: {args.csv}"
    print(f"importing authors from {args.csv} ...")

    now = datetime.now()
    setupLogging(csv_path.with_suffix('.log'))
    LOG.info(f"import authors from {csv_path}")
    
    LOG.info(f"start import {now.isoformat()}")

    try:
        import_authors_from_csv(csv_path, args)
    except Exception:
        LOG.exception('import_authors failed')
    LOG.info('\n')
    print("result see {log_path}")
    print("done.")


main()
