from datetime import datetime
import threading
from pickle import FALSE

import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
from temp import writting_the_xapth
from playwright.sync_api import sync_playwright
import os

class TrackingSystem:
    def __init__(self, output_path):
        self.df = pd.read_pickle(r'C:\Users\vipul\PycharmProjects\crex_webscarph\dataframe.pkl')
        self.df['inning_1'] = False
        self.df['inning_2'] = False
        self.output_path = output_path
        self.live = []


    def block_ads(self, route, request):

        blocked_patterns = [

            "googleads", "doubleclick.net", "adservice", "adsafeprotected", "advertising",
            "adroll", "pubmatic", "zergnet", "yieldmo", "advertising.com", "rubiconproject",
            "adform", "adnxs", "contextual.media.net", "gstatic.com/admanager",
            "pagead2.googlesyndication.com",
            "safeframe.googlesyndication.com",
            "gumi.criteo.com",
            "/pagead/",
            "/ads/",
            "/ad-",
            "/banner/",
            "/syncframe",
        ]

        url = request.url.lower()
        is_ad_related = (
                any(pattern in url for pattern in blocked_patterns) or
                request.resource_type in ["image", "script", "media", "iframe"] and
                ("ad" in url or "doubleclick" in url or "googlesyndication" in url)
        )

        if is_ad_related:
            route.abort()  # Cancel the request if it’s an ad
        else:
            route.continue_()

    def click_button(self, page, button_selector, team_name):
        page.on("route", self.block_ads)
        team_locator = page.locator(button_selector, has_text=team_name)
        team_locator.wait_for(state='attached')
        team_locator.click()
        print(f"Clicked on {team_name}'s team name!")
        page.wait_for_load_state("networkidle")
        team_name = page.locator("//div[@class='team-tab m-right bgColor']//span[@class='team-name']").text_content().strip()
        score = page.locator("//div[@class='team-tab m-right bgColor']//div[@class='score-over']/span[1]").text_content().strip()
        overs = page.locator("//div[@class='team-tab m-right bgColor']//div[@class='score-over']/span[@class='over']").text_content().strip()
        updated_html_content = page.content()
        return updated_html_content, team_name+'-'+score+'-'+overs

    def run(self, url, button_selector, team_name):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            updated_html, detail = self.click_button(page, button_selector, team_name)
            browser.close()
            return updated_html, detail

    def write_in_database(self, track_link):
        try:
            html_content = requests.get(track_link)
            if html_content.status_code == 200:
                tree = etree.HTML(html_content.content)
                match_heading = tree.xpath("//h1[@class='name-wrapper']/span/text()")[0].strip().replace(' ', '_').replace(',', '')
                main_headline = tree.xpath("//span[contains(text(), 'won')]/text()")[0].strip()
                left_team = tree.xpath("//div[contains(@class, 'team-tab') and contains(@class, 'm-right') and not(contains(@class, 'bgColor'))]//span[@class='team-name']/text()")
                finish_batting_html_content, team1_detail = self.run(track_link, 'span.team-name', left_team[0].strip())
                first_batting_df, first_df_bowler, first_fow_df, first_yet_df = writting_the_xapth(finish_batting_html_content)

                right_team = tree.xpath("//div[contains(@class, 'team-tab') and contains(@class, 'm-right') and contains(@class, 'bgColor')]//span[@class='team-name']/text()")
                team_name = tree.xpath("//div[@class='team-tab m-right bgColor']//span[@class='team-name']/text()")
                team_name = team_name[0].strip() if team_name else "Not found"
                score = tree.xpath("//div[@class='team-tab m-right bgColor']//div[@class='score-over']/span[1]/text()")
                score = score[0].strip() if score else "Not found"
                overs = tree.xpath("//div[@class='team-tab m-right bgColor']//div[@class='score-over']/span[@class='over']/text()")
                overs = overs[0].strip() if overs else "Not found"
                team2_detail = team_name + '-' + score + '-' + overs
                batting_df, df_bowler, fow_df, yet_df = writting_the_xapth(html_content.content)
                team1_path = os.path.join(self.output_path,'completed', match_heading, team1_detail)
                team2_path = os.path.join(self.output_path,'completed', match_heading, team2_detail)

                os.makedirs(team1_path, exist_ok=True)
                os.makedirs(team2_path, exist_ok=True)

                first_batting_df.to_csv(os.path.join(team1_path, 'batting.csv'), index=False, encoding='utf-8')
                first_df_bowler.to_csv(os.path.join(team1_path, 'bowling.csv'), index=False, encoding='utf-8')
                first_fow_df.to_csv(os.path.join(team1_path, 'fall_of_wicket.csv'), index=False, encoding='utf-8')
                first_yet_df.to_csv(os.path.join(team1_path, 'yet.csv'), index=False, encoding='utf-8')

                batting_df.to_csv(os.path.join(team2_path, 'batting.csv'), index=False, encoding='utf-8')
                df_bowler.to_csv(os.path.join(team2_path, 'bowling.csv'), index=False, encoding='utf-8')
                fow_df.to_csv(os.path.join(team2_path, 'fall_of_wicket.csv'), index=False, encoding='utf-8')
                yet_df.to_csv(os.path.join(team2_path, 'yet.csv'), index=False, encoding='utf-8')
                with open(os.path.join(self.output_path, 'completed', match_heading,'summary.txt'), 'w', encoding='utf-8') as f:
                    f.write(match_heading + '\n')
                    f.write(main_headline + '\n')
                    f.write(left_team[0].strip() + ' - ' + team1_detail.replace('_', '') + '\n')
                    f.write(right_team[0].strip() + ' - ' + team2_detail.replace('_', '') + '\n')
                    f.write(f"Click here: {track_link}\n")
                return 'success'
        except Exception as e:
            print(f"Error: {str(e)}")
            return 'fail'

    def track_completed_match(self):
        for index, row in self.df.iterrows():
            href = row['link']
            status = row['status'].strip()
            if 'won' in status.lower():
                track_link = href.replace('/live', '/scorecard')
                response = self.write_in_database(track_link)
                count = 0
                while count <= 5:
                    if response == 'success':
                        self.df.loc[index,'inning_1'] = True
                        self.df.loc[index,'inning_2'] = True
                        break
                    else:
                        response = self.write_in_database(track_link)
                        print('something is wrong')
                    count+=1

    def recently_completed_match_track(self, row):
        href = row['link']
        status = row['status'].strip()
        if 'won' in status.lower():
            track_link = href.replace('/live', '/scorecard')
            response = self.write_in_database(track_link)
            count = 0
            while count <= 5:
                if response == 'success':
                    break
                else:
                    response = self.write_in_database(track_link)
                    print('something is wrong')
                count += 1

    def track_live_match(self):
        for index, row in self.df.iterrows():
            status = row['status'].strip()
            if status.lower() == 'live':
                href = row['link']
                track_link = href.replace('/live', '/scorecard')
                team1 = row['team1']
                team2 = row['team2']
                live_track_link = href.replace('/live', '/scorecard')
                html_content = requests.get(live_track_link)
                if html_content.status_code == 200:
                    tree = etree.HTML(html_content.content)
                    word = tree.xpath("//span[contains(text(), 'won')]/text()")[0].strip()
                    if 'won' in word.lower():
                        row['status']= 'won'
                        self.recently_completed_match_track(row)
                        self.df.loc[index, 'inning_1'] = True
                        self.df.loc[index, 'inning_2'] = True
                        self.df.loc[index,'status'] = 'won'

                    else:
                        match_heading = tree.xpath("//h1[@class='name-wrapper']/span/text()")[0].strip().replace(' ', '_').replace(',', '')
                        right_team = tree.xpath("//div[contains(@class, 'team-tab') and contains(@class, 'm-right') and contains(@class, 'bgColor')]//span[@class='team-name']/text()")[0].strip()
                        left_team = tree.xpath("//div[contains(@class, 'team-tab') and contains(@class, 'm-right') and not(contains(@class, 'bgColor'))]//span[@class='team-name']/text()")[0].strip()
                        if right_team and left_team:
                            if not row['inning_1']:
                                first_batting_df, first_df_bowler, first_fow_df, first_yet_df = writting_the_xapth(html_content.content)
                                match_heading = tree.xpath("//h1[@class='name-wrapper']/span/text()")[0].strip().replace(' ', '_').replace(',', '')
                                left_team = tree.xpath("//div[contains(@class, 'team-tab') and contains(@class, 'm-right') and not(contains(@class, 'bgColor'))]//span[@class='team-name']/text()")
                                finish_batting_html_content, team1_detail = self.run(track_link, 'span.team-name', left_team[0].strip())
                                first_batting_df, first_df_bowler, first_fow_df, first_yet_df = writting_the_xapth(finish_batting_html_content)
                                right_team = tree.xpath("//div[contains(@class, 'team-tab') and contains(@class, 'm-right') and contains(@class, 'bgColor')]//span[@class='team-name']/text()")
                                team1_path = os.path.join(self.output_path, 'live', match_heading, team1_detail)
                                os.makedirs(team1_path, exist_ok=True)
                                first_batting_df.to_csv(os.path.join(team1_path, 'batting.csv'), index=False,encoding='utf-8')
                                first_df_bowler.to_csv(os.path.join(team1_path, 'bowling.csv'), index=False, encoding='utf-8')
                                first_fow_df.to_csv(os.path.join(team1_path, 'fall_of_wicket.csv'), index=False,encoding='utf-8')
                                first_yet_df.to_csv(os.path.join(team1_path, 'yet.csv'), index=False, encoding='utf-8')
                                # make the flag the false do not trace again
                                self.df.loc[index, 'inning_1'] = True
                        elif right_team:
                            right_team = tree.xpath("//div[contains(@class, 'team-tab') and contains(@class, 'm-right') and contains(@class, 'bgColor')]//span[@class='team-name']/text()")
                            team_name = tree.xpath("//div[@class='team-tab m-right bgColor']//span[@class='team-name']/text()")
                            team_name = team_name[0].strip() if team_name else "Not found"
                            score = tree.xpath("//div[@class='team-tab m-right bgColor']//div[@class='score-over']/span[1]/text()")
                            score = score[0].strip() if score else "Not found"
                            overs = tree.xpath("//div[@class='team-tab m-right bgColor']//div[@class='score-over']/span[@class='over']/text()")
                            overs = overs[0].strip() if overs else "Not found"
                            team2_detail = team_name + '-' + score + '-' + overs
                            batting_df, df_bowler, fow_df, yet_df = writting_the_xapth(html_content.content)
                            team2_path = os.path.join(self.output_path, 'live', match_heading, team2_detail)
                            batting_df.to_csv(os.path.join(team2_path, 'batting.csv'), index=False, encoding='utf-8')
                            df_bowler.to_csv(os.path.join(team2_path, 'bowling.csv'), index=False, encoding='utf-8')
                            fow_df.to_csv(os.path.join(team2_path, 'fall_of_wicket.csv'), index=False, encoding='utf-8')
                            yet_df.to_csv(os.path.join(team2_path, 'yet.csv'), index=False, encoding='utf-8')

    def always_on_thread(self):
        while True:
            try:
                self.track_live_match()
            except Exception as e:
                print('Error', e)




    def make_live_when_time_hit(self):
        """This function make the status live when time is hit """
        while True:
            current_time = datetime.now()
            for index, row in self.df.iterrows():
                if row['time'] is not None:
                    if current_time >= row['time']:
                        self.df.loc[index, 'status'] = 'live'
                    else:
                        pass

if __name__ == '__main__':
    output_path = r"C:\Users\vipul\PycharmProjects\crex_webscarph\Database"
    obj = TrackingSystem(output_path)
    completed_thread = threading.Thread(target=obj.track_completed_match)
    completed_thread.start()
    completed_thread.join()

    live_thread = threading.Thread(target=obj.always_on_thread)
    time_hit_thread = threading.Thread(target=obj.make_live_when_time_hit)

    # Start both threads
    live_thread.start()
    time_hit_thread.start()

    # Wait for both to complete
    live_thread.join()
    time_hit_thread.join()

    print("\nFinal DataFrame:")
    print(obj.df)