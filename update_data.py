import requests
import json
from datetime import datetime

urls = [
    "https://justmysocks6.net/members/getbwcounter.php?service=1059848&id=596939ca-d377-4cb5-8ba5-d59ce98b4a60",
    # Add more URLs here
]

data = [requests.get(url).json() for url in urls]

with open('bandwidth_data.json', 'w') as f:
    json.dump(data, f)