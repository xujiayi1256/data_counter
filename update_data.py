import requests
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

urls = os.environ['API_URLS'].split(',')
names = os.environ['API_NAMES'].split(',')
pushover_user_key = os.environ.get('PUSHOVER_USER_KEY')
pushover_api_token = os.environ.get('PUSHOVER_API_TOKEN')

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

def send_pushover_notification(user_key, api_token, message, url=None):
    pushover_url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": api_token,
        "user": user_key,
        "message": message
    }
    if url:
        data["url"] = url
        data["url_title"] = "Check Usage Online"
    
    req = Request(pushover_url, urlencode(data).encode())
    try:
        urlopen(req).read()
    except Exception as e:
        print(f"Error sending Pushover notification: {e}")

def check_usage_and_notify(data, user_key, api_token, dashboard_url, threshold=0.9):
    for item in data:
        usage = item['bw_counter_b']
        limit = item['monthly_bw_limit_b']
        name = item['name']
        usage_percentage = usage / limit
        if usage_percentage >= threshold:
            message = f"Warning: {name} bandwidth usage is at {usage_percentage:.1%} of the limit!"
            send_pushover_notification(user_key, api_token, message, dashboard_url)

dashboard_url = 'https://github.xujiayi.me/data_counter/'

if pushover_user_key and pushover_api_token:
    check_usage_and_notify(data, pushover_user_key, pushover_api_token, dashboard_url)
else:
    print("Pushover credentials not set. Skipping notifications.")