import requests
import json
import os

urls = os.environ['API_URLS'].split(',')

data = []
for url in urls:
    try:
        response = requests.get(url.strip())
        response.raise_for_status()
        data.append(response.json())
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")

with open('bandwidth_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Data saved to bandwidth_data.json: {data}")