import requests
import backoff

import json
import re

from typing import Any, Mapping

def user_error(e: Exception) -> bool:
    """
    Return True if this exception is caused by user error, False otherwise.
    """
    if not isinstance(e, requests.exceptions.RequestException):
        return False
    return bool(e.response and 400 <= e.response.status_code < 500)

class VectaraClient():
    BASE_URL = "https://api.vectara.io/v1"
    START_TAG = "%START_SNIPPET%"
    END_TAG = "%END_SNIPPET%"

    def __init__(self, api_key: str, customer_id: str, corpus_id: str):
        self.customer_id = customer_id
        self.corpus_id = corpus_id
        self.api_key = api_key

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5, giveup=user_error)
    def _request(self, endpoint: str, http_method: str = "POST", params: Mapping[str, Any] = None, data: Mapping[str, Any] = None):
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "customer-id": self.customer_id,
            "x-api-key": self.api_key,
            "grpc-timeout": "60S",
            "X-source": "vectara-ragas"
        }
        response = requests.request(method=http_method, url=url, headers=headers, params=params, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    
    def remove_tags(self, text):
        return text.replace(self.START_TAG, '').replace(self.END_TAG, '')

    def query(self, query_str: str, cfg: dict):
        mmr_flag = cfg['mmr']
        mmr_diversity_bias = 0.3
        mmr_top_k = 50
        top_k = 10

        corpora_key_list = [{
              'customer_id': self.customer_id, 'corpus_id': self.corpus_id, 'lexical_interpolation_config': {'lambda': cfg['lambda']}
        }]

        endpoint = f"https://api.vectara.io/v1/query"
        body = {
            'query': [
                { 
                    'query': query_str,
                    'start': 0,
                    'numResults': mmr_top_k if mmr_flag else top_k,
                    'corpusKey': corpora_key_list,
                    'context_config': {
                        'sentences_before': 2,
                        'sentences_after': 2,
                        'start_tag': self.START_TAG,
                        'end_tag': self.END_TAG,
                    },
                    'summary': [
                        {
                            'responseLang': 'eng',
                            'maxSummarizedResults': cfg['max_summary_result'],
                            'summarizerPromptName': cfg['prompt_name'],
                        }
                    ]
                } 
            ]
        }
        if mmr_flag:
            body['query'][0]['rerankingConfig'] = {
                'rerankerId': 272725718,
                'mmrConfig': {
                    'diversityBias': mmr_diversity_bias
                }
            }

        res = self._request(endpoint="query", data=body)                
        summary = res['responseSet'][0]['summary'][0]['text']
        summary = re.sub("\[\d+(,\s*\d+)*\]", "", str(summary)).replace(' .', '.')
        contexts = [self.remove_tags(r['text']) for r in res['responseSet'][0]['response'][:cfg['max_summary_result']]]
        
        return summary, contexts

    def get_all_doc_urls(self) -> list[str]:
        
        page_key = None  # Initialize page_key as None
        docs = []
    
        # Loop until there's no next page
        while True:
            body = {"corpusId": self.corpus_id, "numResults": 100}
            if page_key:  # Add page_key to the request if it's not None
                body["pageKey"] = page_key
            res = self._request(endpoint="list-documents", data=body)    

            # Extract URLs from documents
            for doc in res['document']:
                url = next((md['value'] for md in doc['metadata'] if md['name'] == 'url'), None)
                if url:
                    docs.append(url)

            # Check if we need to go further
            page_key = res.get('nextPageKey', None)    
            if not page_key:  # Break the loop if there's no next page
                break
    
        return docs

    def index_document(self, document):
        """
        Index a document (by uploading it to the Vectara corpus) from the document dictionary
        """
        api_endpoint = f"https://api.vectara.io/v1/index"
        request = {
            'customer_id': self.customer_id,
            'corpus_id': self.corpus_id,
            'document': document,
        }
        post_headers = { 
            'x-api-key': self.api_key,
            'customer-id': self.customer_id,
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


