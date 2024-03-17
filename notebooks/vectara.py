import json
import requests

def index_document(customer_id, corpus_id, api_key, document):
    """
    Index a document (by uploading it to the Vectara corpus) from the document dictionary
    """
    api_endpoint = f"https://api.vectara.io/v1/index"
    request = {
        'customer_id': customer_id,
        'corpus_id': corpus_id,
        'document': document,
    }
    post_headers = { 
        'x-api-key': api_key,
        'customer-id': customer_id,
    }
    try:
        data = json.dumps(request)
    except Exception as e:
        print(f"Can't serialize request {request}, skipping, e={e}")   
        return False
    
    try:
        response = requests.post(api_endpoint, data=data, verify=True, headers=post_headers)
    except Exception as e:
        print(f"Exception {e} while indexing document {document['documentId']}")
        return False
    if response.status_code != 200:
        print("REST upload failed with code %d, reason %s, text %s",
              response.status_code,
              response.reason,
              response.text)
        return False
    result = response.json()
    if "status" in result and result["status"] and "OK" in result["status"]["code"]:
        return True
    else:
        return False

