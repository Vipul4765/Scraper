from playwright.sync_api import sync_playwright
import time

class ButtonClicker:
    def __init__(self, url, button_selector):
        self.url = url
        self.button_selector = button_selector
        self.requests_data = []  # Store network requests

    def start_browser(self):
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False)  # Set to True for no UI
            self.page = self.browser.new_page()
            self.page.on("request", self.on_request)
            self.page.goto(self.url)

    def on_request(self, request):
        request_data = {
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "post_data": request.post_data if request.method in ["POST", "PUT"] else None
        }
        self.requests_data.append(request_data)
        print(f"Request captured: {request.url} (Method: {request.method})")

    def click_button(self):
        self.page.wait_for_selector(self.button_selector, state='attached')
        self.page.locator(self.button_selector).click()
        print("Button clicked!")
        time.sleep(2)  # Wait for network requests to complete
        return [req for req in self.requests_data if req["url"] != self.url]

    def close_browser(self):
        self.browser.close()

    def get_scorecard_request(self):
        requests = self.click_button()
        # Filter for API-like requests
        api_requests = [req for req in requests if '/api/' in req["url"] or req["url"].endswith(('.json', '/data'))]
        return api_requests[0] if api_requests else None

# Run the script
url = "https://crex.live/scoreboard/STU/1PK/14th-Match/QI/QL/dcw-vs-rcbw-14th-match-womens-cricketleague-2025/scorecard"
button_selector = "div.team-tab.m-right div.team-details div.team-flag span.team-name"

clicker = ButtonClicker(url, button_selector)
clicker.start_browser()
triggered_request = clicker.get_scorecard_request()

if triggered_request:
    print("\nCaptured Scorecard Request:")
    print(f"URL: {triggered_request['url']}")
    print(f"Method: {triggered_request['method']}")
    print(f"Headers: {triggered_request['headers']}")
    if triggered_request['post_data']:
        print(f"POST Data: {triggered_request['post_data']}")

clicker.close_browser()