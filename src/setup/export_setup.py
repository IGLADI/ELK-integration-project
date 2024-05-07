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

session = requests.Session()

url2 = f"{url}/status"

print(f"Waiting for kibana API to be up at {url2}...")
while True:
    try:
        resp = session.request("GET", url2)
        if resp.status_code == 200:
            break
    except Exception as e:
        print(f"Waiting for kibana, got: {e}")
    time.sleep(2)

url3 = f"{url}/saved_objects/_import?overwrite=true"
files = {"file": open("./export.ndjson", "rb")}
print("sending:", files)

headers = {"kbn-xsrf": "true"}

resp = requests.post(url3, auth=HTTPBasicAuth(kibana_username, kibana_password), files=files, headers=headers)

print("got:")
print(resp)
print(resp.text)
