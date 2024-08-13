import requests
import json


def get_ip_related_details(ip_address):
    try:
        url = f"http://127.0.0.1:8000/api/ip-details"
        print(url)
        payload = json.dumps({
          "ip_address": ip_address
        })
        headers = {
          'Authorization': 'token 3f84daf5b39bf8fb52b061952b1b44a9dc88e22a',
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
        url = "http://127.0.0.1:8000/api/session-details"

        payload = json.dumps({
            "session_id": session_id
        })
        headers = {
            'Authorization': 'token 3f84daf5b39bf8fb52b061952b1b44a9dc88e22a',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        json_response = response.json()[0]
        return json_response

    except Exception as e:
        print(f"Exception {e} occurred")

# ip_address = '74.225.252.130'
# print(get_ip_related_details(ip_address))
# session_id = 'l1314czkjv6xly41rk81z5g5n4o6oe44'
# print(get_session_details(session_id))