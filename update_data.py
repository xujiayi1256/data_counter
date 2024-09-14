import requests
import json
import os

urls = os.environ['API_URLS'].split(',')

data = [requests.get(url.strip()).json() for url in urls]

with open('bandwidth_data.json', 'w') as f:
    json.dump(data, f)