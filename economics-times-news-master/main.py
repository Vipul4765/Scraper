import requests
from lxml import etree
import csv
import os
from datetime import datetime
from urllib.parse import urljoin


class WebScraper:

    def __init__(self):
        self.url = 'https://economictimes.indiatimes.com/markets/stocks/news'
        self.session = requests.Session()
        self.pre_request()


    def e_tree(self, response):
        tree = etree.HTML(response.content)
        return tree

    def pre_request(self):
        response = self.session.get(self.url)
        tree = self.e_tree(response)
        load_more_xpath = '//div[@class="autoload_continue"]'

        each_story_elements = tree.xpath('//div[@class="eachStory"]')

        # Get today's date
        today = datetime.now().date()

        # Check if the CSV file exists
        file_exists = os.path.exists('data.csv')

        with open('data.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header only if the file is newly created
            if not file_exists:
                writer.writerow(['Article URL', 'Heading', 'Date-Time', 'Paragraph', 'text_content'])

            for each_story in each_story_elements:
                each_story_tree = etree.HTML(etree.tostring(each_story))
                date_time_str = each_story_tree.xpath('.//time/@data-time')[0]

                # Remove the 'IST' suffix from the date-time string
                date_time_str = date_time_str.replace(' IST', '')

                # Parse the date-time string using the adjusted format
                date_time = datetime.strptime(date_time_str, '%b %d, %Y, %I:%M %p')

                # Check if the date is today
                if date_time.date() == today:
                    article_url = each_story_tree.xpath('.//span/@href')[0]
                    heading = each_story_tree.xpath('.//h3/a/text()')[0]
                    paragraph = each_story_tree.xpath('.//p/text()')[0]
                    full_url = urljoin(self.url, article_url)
                    para_request = requests.request('GET',full_url)
                    mini_content = etree.HTML(para_request.content)
                    text_content = mini_content.xpath("//div[@class='artText']/text()")
                    text_content = ''.join(text_content)


                    writer.writerow([full_url, heading, date_time_str, paragraph, text_content])
                else:
                    # If date is not today, break the loop
                    break


# Create an instance of the WebScraper class
scraper = WebScraper()
