import requests
from datetime import datetime, timedelta
import pandas as pd


class AlgoScraper:

    def __init__(self):
        self.url = "https://prices.algotest.in/straddle-mtm"
        self.df = pd.DataFrame()
        self.file_name = 'nifty_straddle_heat_map_combined.csv'
        self.headers = {
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
        self.payload = {
            "ticker": "NIFTY",
            "start_date": "2024-01-01",
            "end_date": "2024-01-01"
        }
        self.session = requests.Session()

    def generate_date_range(self):
        start_date = datetime(2024, 1, 1)
        end_date = datetime.today()
        date_range = []

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Weekdays only
                date_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        return date_range

    def fetch_data_for_date_range(self):
        date_range = self.generate_date_range()
        self.session.get("https://algotest.in/heatmap", headers=self.headers)  # Initial session

        for i, date in enumerate(date_range, start=1):
            if i % 50 == 0:
                print("Refreshing session...")
                self.session = requests.Session()

            print(f"Fetching data for date: {date}")
            self.payload['start_date'] = date
            self.payload['end_date'] = date
            try:
                response = self.session.post(self.url, headers=self.headers, json=self.payload)

                if response.status_code == 200:
                    data_rec = response.json()['data']
                    data_seggration = []
                    for elem in data_rec:
                        new_dict = {
                            'symbol': elem[0],
                            'date': datetime.strptime(elem[1], '%Y-%m-%d').date(),
                            'time': elem[2],
                            'range': int(elem[3]),
                            'price': float(elem[4]) + float(elem[5]),
                        }
                        data_seggration.append(new_dict)

                    df = pd.DataFrame(data_seggration)
                    df['range'] = df['range'].astype(int)
                    pivot_df = df.pivot(index='time', columns='range', values='price')
                    pivot_df = pivot_df.sort_index(axis=1)
                    pivot_df['Total'] = pivot_df.sum(axis=1)
                    pivot_df['date'] = date  # Add date for tracking
                    pivot_df.reset_index(inplace=True)  # Flatten index before concat
                    self.df = pd.concat([self.df, pivot_df], ignore_index=True)

                else:
                    print(f"Failed to fetch data for {date}, Status Code: {response.status_code}")
            except Exception as e:
                print(f"Error occurred for {date}: {e}")

        # Save everything in one file
        self.df.to_csv(self.file_name, index=False)
        print(f"All data saved in: {self.file_name}")


# Running the scraper
if __name__ == "__main__":
    scraper = AlgoScraper()
    scraper.fetch_data_for_date_range()
