import os
import time
import requests
from requests.auth import HTTPBasicAuth

kibana_username = "elastic"
kibana_password = os.getenv("KIBANA_SYSTEM_PASSWORD")
# consider rabbitmq has the same host as kibana
host = os.getenv("RABBITMQ_HOST")
url = f"http://{host}:16601/api"
print("kibana_username: ", kibana_username)
print("kibana_password: ", kibana_password)
print("host: ", host)
print("url: ", url)

# create a connection
session = requests.Session()

url2 = f"{url}/status"

print(f"Waiting for kibana API to be up at {url2}...")
while True:
    try:
        # until we don't crash & get status OK aka 200
        resp = session.request("GET", url2)
        if resp.status_code == 200:
            break
    except Exception as e:
        print(f"Waiting for kibana, got: {e}")
    # sleep to not be timed out
    time.sleep(2)

# load saved objects
files = {"file": open("./export.ndjson", "rb")}
url3 = f"{url}/saved_objects/_import?overwrite=true"
print("sending:", files)

# upload the saved objects to kibana api
headers = {"kbn-xsrf": "true"}
resp = requests.post(url3, auth=HTTPBasicAuth(kibana_username, kibana_password), files=files, headers=headers)

print("got:")
print(resp)
print(resp.text)
