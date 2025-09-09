import requests
import logging
import json
from decouple import config

def verify_tax_using_post_request(tin_no, assessment_year):
    try:
        url = f"{config('tax_web_url')}/{tin_no}/{assessment_year}"
        
        payload = {}
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload,verify=False)

        print(response.text)
        logging.info(f"{response.text=}")
        response_dict = json.loads(response.text) # converting to python dict
        return response_dict, response.status_code
    except Exception as e:
        # Log error response
        raise Exception(f"Exception from psr site: {e}")