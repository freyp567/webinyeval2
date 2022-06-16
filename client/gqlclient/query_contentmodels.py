# graphql query to list content models

import json
import requests 

API_URL = os.environ.get("API_URL")
READ_URL = API_URL + "/cms/read/de-DE"
API_KEY = os.environ.get("API_KEY")



def main():
    url = READ_URL

    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + API_KEY,
        "Connection": "keep-alive",
        #User-Agent': 'query_contentmodels',
        "Origin": API_URL
    }
    query = {
        "query": "{listContentModels {data {name  modelId} }}"
    }
    query2 = {
        "query": "{listBookitems {data {bookId bookTitle}}}"
    }
    #  error {code message}

    session = requests.Session()
    # need to enforce TLSv1.2 ? have TLSv1.3

    response = session.post(
        url = url,
        headers = headers,
        json = query2
    )
    if response.status_code != 200:
        # We can't connect to the server for this app or website at this time.
        print(f"request failed with status_code={response.status_code}\ndetails:\n\n")
        print(response.text)
        print("\n")
        raise RuntimeError("request failed")

    result = response.json()
    print("\nquery result:\n\n")
    print(json.dumps(result, indent=4))
    print("done")

main()
