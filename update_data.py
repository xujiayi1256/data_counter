import requests
import json
import os

urls = os.environ['API_URLS'].split(',')
names = os.environ['API_NAMES'].split(',')

data = []
for url, name in zip(urls, names):
    try:
        response = requests.get(url.strip())
        response.raise_for_status()
        json_data = response.json()
        json_data['name'] = name.strip()
        data.append(json_data)
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")

with open('bandwidth_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Data saved to bandwidth_data.json: {data}")