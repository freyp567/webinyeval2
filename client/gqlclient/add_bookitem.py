"""
add a new bookitem using graphql mutation
"""

import datetime
import requests 
import uuid

API_URL = "https://dzl9t7sk9bsqh.cloudfront.net"
MANAGE_URL = API_URL + "/cms/manage/de-DE"
API_KEY = "a3b3604d9599f4da0a0e7abe2fbcbc8d9ae2e4badaa8411a"


"""
# https://stackoverflow.com/questions/48693825/making-a-graphql-mutation-from-my-python-code-getting-error
# https://stackoverflow.com/a/50514619/4007374

"""

def addBookItem(bookItem):
    url = MANAGE_URL
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + API_KEY,
        "Connection": "keep-alive",
        #User-Agent': 'add_bookitem',
        "Origin": API_URL
    }

    if 0:
        dateReadVal = bookItem['dateRead'] and f'''"{bookItem['dateRead']}"''' or 'null'
        badmutation = f"""mutation {{
            createBookItem(
                bookId: "{bookItem['bookId']}", 
                bookTitle: "{bookItem['bookTitle']}",
                dateRead: {dateReadVal}
            ) 
            {{
                bookId
            }}
        }}"""
        # Field "createBookitem" argument "data" of type "BookitemInput!" is required, but it was not provided.

    mutation = """mutation CreateBookItem($data:BookitemInput!){
        createBookitem(data:$data)
        {
            data { bookId }
            error { code message data }
        }
    }"""
    vars = {'data': bookItem}

    request = requests.post(url, json={'query': mutation, 'variables': vars}, headers=headers)
    if request.status_code == 200:
        result = request.json()
        errors = result.get('errors')
        if errors:
            print(f"Update failed - {errors}")
            raise ValueError(f"Update failed")
        return result
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def main():
    now = datetime.datetime.now()
    addBookItem({
        "bookId": str(uuid.uuid4()),
        "bookTitle": "Test " + now.isoformat(sep='T'),
        "dateRead": None
    })
main()
