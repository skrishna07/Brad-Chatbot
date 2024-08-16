import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def get_ip_related_details(ip_address):
    try:
        url = f"http://{os.environ.get('local_link')}/api/ip-details"
        print(url)
        payload = json.dumps({
          "ip_address": ip_address
        })
        headers = {
          'Authorization': f'{os.environ.get("chat_access_token")}',
          'Content-Type': 'application/json'
}

        response = requests.request("POST", url, headers=headers, data=payload)

        json_response = response.json()

        # for output_response in json_response:
        #     session_responses = output_response['responses'][0]['query']
        #     print(session_responses)
        if len(json_response) >= 10:
            output = json_response[-1:-11:-1]
        else:
            output = json_response
        return output
    except Exception as e:
          print(f"Exception {e} occurred")


def get_session_details(session_id):
    try:
        url = f"http://{os.environ.get('local_link')}/api/session-details"

        payload = json.dumps({
            "session_id": session_id
        })
        headers = {
          'Authorization': f'{os.environ.get("chat_access_token")}',
          'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)

        json_response = response.json()[0]
        return json_response

    except Exception as e:
        print(f"Exception {e} occurred")