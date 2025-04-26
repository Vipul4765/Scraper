import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


class BseScraper:

    def __init__(self):
        self.url = "https://member.bseindia.com/"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.driver = None

    def transfer_cookies(self):
        selenium_driver = self.driver
        selenium_driver.get(self.url)  # Navigate to base URL first

        for cookie in self.session.cookies:
            cookie_dict = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
            }
            selenium_driver.add_cookie(cookie_dict)

    def get_hidden(self, name, soup):
        tag = soup.find("input", {"name": name})
        return tag["value"] if tag else ""



    def build_payload(self, soup, event_target="", event_argument=""):
        return {
            "__EVENTTARGET": event_target or self.get_hidden("__EVENTTARGET", soup),
            "__EVENTARGUMENT": event_argument or self.get_hidden("__EVENTARGUMENT", soup),
            "__VIEWSTATE": self.get_hidden("__VIEWSTATE", soup),
            "__VIEWSTATEGENERATOR": self.get_hidden("__VIEWSTATEGENERATOR", soup),
            "__EVENTVALIDATION": self.get_hidden("__EVENTVALIDATION", soup),
        }

    def get_hidden_field(self, soup, field_name):
        tag = soup.find("input", {"name": field_name})
        return tag["value"] if tag else ""

    def extract_data(self, soup):
        table = soup.find("table", {"id": "FileGridVB1_gvFiles"})
        if not table:
            print("No file table found!")
            return

        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                file_name = cols[1].get_text(strip=True)
                file_type = cols[2].get_text(strip=True)
                created_time = cols[3].get_text(strip=True)
                print(f"File: {file_name}, Type: {file_type}, Created Time: {created_time}")

    def extract_ajax_value(self, response_text, key):
        pattern = re.compile(fr"{key}\|([^|]+)\|")
        match = pattern.search(response_text)
        return match.group(1) if match else ""

    def get_second_last_target(self, soup):
        table = soup.find("table", {"id": "FileGridVB1_gvFiles"})
        rows = table.find_all("tr")[1:]  # Skip header

        if len(rows) < 2:
            raise ValueError("Not enough rows to select second-last folder")



        second_last_row = rows[-2]
        link = second_last_row.find("a", id=lambda x: x and "lbFolderItem" in x)

        if not link:
            raise ValueError("Folder link not found in row")

        control_id = link["id"].split("_")[-1]
        return f"FileGridVB1$gvFiles${control_id}$lbFolderItem"

    def launch_selenium(self, html):
        options = Options()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")  # Optional: run in headless mode

        driver = webdriver.Chrome(options=options)
        driver.get("data:text/html;charset=utf-8," + html)

        self.driver = driver  # Save driver if needed later

        time.sleep(3)  # Let the JS render, if needed

        print("🎯 Selenium is now controlling the page after 5th request.")

    def start_engine(self):
        # Initial GET
        response = self.session.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # First POST
        payload = self.build_payload(
            soup,
            event_target="FileGridVB1$gvFiles$ctl06$lbFolderItem"
        )
        print(f"First Payload: {payload}")  # Log the first payload
        post_resp = self.session.post(self.url, data=payload, headers=self.headers)
        soup = BeautifulSoup(post_resp.text, 'html.parser')

        # Second POST
        payload = self.build_payload(
            soup,
            event_target="FileGridVB1$gvFiles$ctl06$lbFileItem"
        )
        print(f"Second Payload: {payload}")  # Log the second payload
        second_resp = self.session.post(self.url, data=payload, headers=self.headers)
        soup = BeautifulSoup(second_resp.text, 'html.parser')

        # Third POST
        payload = self.build_payload(soup)
        print(f"Third Payload: {payload}")  # Log the third payload
        third_resp = self.session.post(self.url, data=payload, headers=self.headers)
        soup = BeautifulSoup(third_resp.text, 'html.parser')

        # Fourth POST
        fourth_payload = {
            "ScriptManager1": "UpdatePanel1|FileGridVB1$gvFiles$ctl02$lbFolderItem",
            "__EVENTTARGET": "FileGridVB1$gvFiles$ctl02$lbFolderItem",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": self.get_hidden("__VIEWSTATE", soup),
            "__VIEWSTATEGENERATOR": self.get_hidden("__VIEWSTATEGENERATOR", soup),
            "__ASYNCPOST": "true",
        }
        print(f"Fourth Payload: {fourth_payload}")  # Log the fourth payload

        fourth_resp = self.session.post(self.url, data=fourth_payload, headers=self.headers)
        soup = BeautifulSoup(fourth_resp.text, 'html.parser')


        # Fifth POST (with updated VIEWSTATE and other hidden values)
        # Extract updated ViewState from AJAX response
        updated_viewstate = self.extract_ajax_value(soup.text, "__VIEWSTATE")
        updated_viewstate_generator = self.extract_ajax_value(soup.text, "__VIEWSTATEGENERATOR")

        # Fifth POST (using AJAX-extracted values)
        print("\n🔑 Sending fifth POST...")
        fifth_payload = {
            "ScriptManager1": "UpdatePanel1|FileGridVB1$gvFiles$ctl02$lbFolderItem",
            "__EVENTTARGET": "FileGridVB1$gvFiles$ctl02$lbFolderItem",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": updated_viewstate,
            "__VIEWSTATEGENERATOR": updated_viewstate_generator,
            "__ASYNCPOST": "true",
        }
        fifth_resp = self.session.post(self.url, data=fifth_payload, headers=self.headers)
        soup = BeautifulSoup(fifth_resp.text, 'html.parser')
        # Convert the fifth response (or AJAX response) into full HTML and launch Selenium
        full_html = fifth_resp.text
        self.launch_selenium(full_html)
        print()

        # sixth request okk using the selenium



    # Run the scraper
if __name__ == "__main__":
    scraper = BseScraper()
    scraper.start_engine()
