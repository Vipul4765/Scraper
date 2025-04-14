import requests
from datetime import datetime
import pandas as pd


url = "https://prices.algotest.in/straddle-mtm"

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://algotest.in",
    "priority": "u=1, i",
    "referer": "https://algotest.in/",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

payload = {
    "ticker": "NIFTY",
    "start_date": "2024-04-04",
    "end_date": "2024-04-04"
}

# First get initial cookies from the website
with requests.Session() as s:
    # Get base cookies
    s.get("https://algotest.in/heatmap", headers=headers)

    # Make the API request with collected cookies
    response = s.post(
        url,
        headers=headers,
        json=payload
    )

print(f"Status Code: {response.status_code}")
print("Response:", response.json())
data_rec = response.json()['data']
index = list(range(10, 101, 10))
data_seggration = []
for elem in data_rec:
    new_dict = {
        'symbol': elem[0],
        'date': datetime.strptime(elem[1], '%Y-%m-%d').date(),
        'time': elem[2],
        'range': int(elem[3]),
        'price': float(elem[4])+float(elem[5]),
    }
    data_seggration.append(new_dict)
df = pd.DataFrame(data_seggration)
df['range'] = df['range'].astype(int)
pivot_df = df.pivot(index='time', columns='range', values='price')
pivot_df = pivot_df.sort_index(axis=1)
pivot_df['Total'] = pivot_df.sum(axis=1)
pivot_df.loc['Total'] = pivot_df.sum(axis=0)
print(pivot_df)


