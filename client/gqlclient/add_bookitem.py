"""
add a new bookitem using graphql mutation
"""

import os
import datetime
import requests 
import uuid

API_URL = os.environ.get("API_URL")
MANAGE_URL = API_URL + "/cms/manage/de-DE"
API_KEY = os.environ.get("API_KEY")


"""
# https://stackoverflow.com/questions/48693825/making-a-graphql-mutation-from-my-python-code-getting-error
# https://stackoverflow.com/a/50514619/4007374

"""


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


def addBookItem(bookItem):
    url = MANAGE_URL

    mutation = """mutation CreateBookItem($data:BookitemInput!){
        createBookitem(data:$data)
        {
            data { id meta { status }}
            error { code message data }
        }
    }"""
    vars = {'data': bookItem}

    request = requests.post(url, json={'query': mutation, 'variables': vars}, headers=getHeaders())
    if request.status_code == 200:
        result = request.json()
        errors = result.get('errors')
        if errors:
            print(f"Update failed - {errors}")
            raise ValueError(f"Update failed")

        return result
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def publishBookItem(id):
    url = MANAGE_URL
    query = """
mutation {
  publishBookitem(revision: "%s") {
    data { id entryId }
    error {code message data}
  }
}    
    """ % (id)
    request = requests.post(url, json={'query': query}, headers=getHeaders())
    if request.status_code == 200:
        result = request.json()
        errors = result.get('errors')
        if errors:
            print(f"Publish failed - {errors}")
            raise ValueError(f"Publish failed")

        return result
    else:
        raise Exception("Publish failed with status_code={}. {}".format(request.status_code, query))


def main():
    now = datetime.datetime.now()
    result = addBookItem({
        "bookId": str(uuid.uuid4()),
        "bookTitle": "Test " + now.isoformat(sep='T'),
        "dateRead": None
    })

    itemStatus = result['data']['createBookitem']['data']['meta']['status']
    id = result['data']['createBookitem']['data']['id']
    if itemStatus == 'draft':
        publishBookItem(id)
    else:
        print(f"item {id} status is {itemStatus}")
    return

main()
