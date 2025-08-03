
import asyncio
import aiohttp
import pandas as pd
from lxml import etree
import pytz
from datetime import datetime, timedelta



# noinspection PyCompatibility
class MatchScraper:
    def __init__(self):
        self.base_url = 'https://crex.live/fixtures/match-list'
        self.match_list = []

    async def scrape_match(self, match):
        """
        Main match scraping controller.
        Handles different match states.
        """
        print(f"Scraping match: {match}")

    async def fetch_html(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def convert_to_ist(self, london_time_str):
        london_time = datetime.strptime(london_time_str, "%I:%M %p")
        india_time = london_time + timedelta(hours=5, minutes=30)
        return india_time.strftime("%I:%M %p")

    async def scrape_static_data(self):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch_html(session, self.base_url)
            if html:
                tree = etree.HTML(html)

                dates_wise_xpath = tree.xpath("//div[@class='date']/div")

                date_xpath = "(//div[@class='date'])/following-sibling::div[contains(@class, 'matches-card-space')]"
                date_match_elements = tree.xpath(date_xpath)
                count = 0
                for ddd in date_match_elements:
                    cc_date = dates_wise_xpath[count].text
                    dd_date = cc_date.split(',')[-1].strip()
                    dd_date = dd_date.replace(' ', '-')
                    all_matches = ddd.xpath(".//li[@class='match-card-container']")
                    for match in all_matches:
                        team1_name = match.xpath(".//div[@class='team-info'][1]//span[@class='team-name']/text()")
                        team1_score = match.xpath(".//div[@class='team-info'][1]//span[@class='team-score']/text()")

                        team2_name = match.xpath(".//div[@class='team-info'][2]//span[@class='team-name']/text()")
                        team2_score = match.xpath(".//div[@class='team-info'][2]//span[@class='team-score']/text()")

                        match_status = match.xpath(
                            ".//div[@class='result']//span/text() | .//div[@class='live-info']//span/text()"
                        )
                        match_href = match.xpath(".//a[@class='match-card-wrapper']/@href")
                        match_time = match.xpath(".//div[@class='team-info']/following-sibling::div[@class='not-started']//div[@class='start-text']/text()[normalize-space()]")


                        # Clean up the time string (strip any unnecessary whitespace)
                        if match_time:
                            match_time = match_time[0].strip()
                            match_time = await self.convert_to_ist(match_time)
                            date_obj = datetime.strptime(dd_date + ' ' + str(match_time), "%d-%b-%Y %I:%M %p")

                        else:
                            date_obj = None


                        match_dict = {
                            "team1": team1_name[0] if team1_name else "Unknown",
                            "team1_score": team1_score[0] if team1_score else "Yet to bat",
                            "team2": team2_name[0] if team2_name else "Unknown",
                            "team2_score": team2_score[0] if team2_score else "Yet to bat",
                            "status": match_status[0] if match_status else "Not Started",
                            "link": f"https://crex.live{match_href[0]}" if match_href else "N/A",
                            "time" : date_obj,

                        }

                        self.match_list.append(match_dict)

                    count+=1
        return self.match_list




# Create an instance of the class
scraper = MatchScraper()


# Run an async method
# noinspection PyCompatibility
async def main():
    all_matches = await scraper.scrape_static_data()
    df = pd.DataFrame(all_matches)
    df.drop_duplicates(inplace=True)
    df.to_pickle('dataframe.pkl')



# Run the event loop
asyncio.run(main())