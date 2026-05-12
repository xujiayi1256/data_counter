import requests
import json
import os

urls = [u.strip() for u in os.environ['API_URLS'].split(',') if u.strip()]
names = [n.strip() for n in os.environ['API_NAMES'].split(',') if n.strip()]
if len(urls) != len(names):
    print(
        "WARNING: API_URLS has {} entries and API_NAMES has {} — they are paired in order; "
        "fix your secrets so the counts match.".format(len(urls), len(names))
    )

bark_device_key = os.environ.get('BARK_DEVICE_KEY')
_bark_server_env = (os.environ.get('BARK_SERVER') or '').strip()
bark_server = (_bark_server_env or 'https://api.day.app').rstrip('/')
ntfy_url = os.environ.get('NTFY_URL')

data = []
for url, name in zip(urls, names):
    try:
        response = requests.get(url.strip())
        response.raise_for_status()
        json_data = response.json()
        json_data['name'] = name.strip()
        data.append(json_data)
    except requests.RequestException as e:
        print("Error fetching data from {}: {}".format(url, e))

with open('bandwidth_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Data saved to bandwidth_data.json: {}".format(data))


def write_widgy_pie_csv(path, used_gb, remaining_gb):
    """Two-column CSV for Widgy-style pie charts: label + numeric value."""
    with open(path, 'w') as f:
        f.write('Label,Value\n')
        f.write('Used,{:.6f}\n'.format(used_gb))
        f.write('Remaining,{:.6f}\n'.format(remaining_gb))


_widgy_primary_written = False
for idx, item in enumerate(data):
    try:
        used_b = float(item['bw_counter_b'])
        lim_b = float(item['monthly_bw_limit_b'])
    except (KeyError, TypeError, ValueError):
        print('Skipping Widgy CSV for index {}: missing or invalid counters'.format(idx))
        continue
    used_gb = used_b / 1e9
    remaining_gb = max(0.0, (lim_b - used_b) / 1e9)
    write_widgy_pie_csv('widgy_bandwidth_{}.csv'.format(idx), used_gb, remaining_gb)
    if not _widgy_primary_written:
        write_widgy_pie_csv('widgy_bandwidth.csv', used_gb, remaining_gb)
        _widgy_primary_written = True


def send_bark_notification(device_key, server_base, message, click_url=None):
    """Bark JSON API: POST {server}/push with device_key, title, body, optional url."""
    push_url = '{}/push'.format(server_base)
    payload = {
        'device_key': device_key.strip(),
        'title': 'Bandwidth alert',
        'body': message,
    }
    if click_url:
        payload['url'] = click_url
    try:
        r = requests.post(push_url, json=payload, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print("Error sending Bark notification: {}".format(e))


def send_ntfy_notification(topic_url, message, click_url=None):
    """POST body = message. topic_url is e.g. https://ntfy.sh/your-secret-topic"""
    headers = {'Title': 'Bandwidth alert'}
    if click_url:
        headers['Click'] = click_url
    try:
        r = requests.post(
            topic_url.strip(),
            data=message.encode('utf-8'),
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print("Error sending ntfy notification: {}".format(e))


def send_bandwidth_alert(message, dashboard_url=None):
    # Order: Bark first, then ntfy
    if bark_device_key:
        send_bark_notification(bark_device_key, bark_server, message, dashboard_url)
    if ntfy_url:
        send_ntfy_notification(ntfy_url, message, dashboard_url)


def any_notification_configured():
    return bool(bark_device_key or ntfy_url)


def check_usage_and_notify(data, dashboard_url, threshold=0.9):
    for item in data:
        usage = item['bw_counter_b']
        limit = item['monthly_bw_limit_b']
        name = item['name']
        usage_percentage = usage / limit
        if usage_percentage >= threshold:
            message = "Warning: {} bandwidth usage is at {:.1%} of the limit!".format(
                name, usage_percentage
            )
            send_bandwidth_alert(message, dashboard_url)


dashboard_url = 'https://github.xujiayi.me/data_counter/'

if any_notification_configured():
    check_usage_and_notify(data, dashboard_url)
else:
    print(
        "No notification channels configured. Set BARK_DEVICE_KEY (and optionally "
        "BARK_SERVER for self-hosted Bark), and/or NTFY_URL."
    )
