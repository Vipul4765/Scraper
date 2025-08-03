import requests
from lxml import etree
import csv
import re
from urllib.parse import urljoin

class InternShalaData:
    count = 1
    session = requests.Session()
    base_url = "https://internshala.com/internships/page-{}"
    page_number = 1
    base_url = 'https://internshala.com/internships'
    payload = {}


    def get_text_content(self, data_list):
        """
        Safely retrieves text content from an XPath expression.

        Parameters:
        - tree: The lxml etree object.
        - xpath_expression: The XPath expression to select the desired element.

        Returns:
        - Text content if found, otherwise an empty string.
        """
        if data_list:
            return data_list[0].strip()
        else:
            return ''


    def web_scrape(self):
        all_data = []
        response = self.session.request('GET', self.base_url.format(self.page_number))
        tree = etree.HTML(response.content)
        xpath_view_detail = '//a[@class=" btn btn-secondary view_detail_button_outline"]/@href'
        all_view_detail = tree.xpath(xpath_view_detail)
        for view in all_view_detail:
            print(self.count)
            self.count+=1
            url = urljoin(self.base_url, view)
            view_detail_page = requests.request("GET", url, data=self.payload)
            print(view_detail_page.status_code)
            tree = etree.HTML(view_detail_page.content)

            # role
            xpath_role = '//h1[@class="heading_2_4 heading_title"]/text()'
            role = tree.xpath(xpath_role)
            role = self.get_text_content(role)


            # company
            xpath_company = '//div[@class="company_and_premium"]/p/text()'
            company_name = tree.xpath(xpath_company)
            company_name = self.get_text_content(company_name)

            # location
            xpath_location = '//div[@id="location_names"]/span/a/text()'
            location_name = tuple(tree.xpath(xpath_location))

            # duration
            xpath_duration = '//i[@class="ic-16-calendar"]/parent::div/following-sibling::div/text()'
            duration = tree.xpath(xpath_duration)
            duration = self.get_text_content(duration)

            # stipend
            xpath_stipend = '//span[@class="stipend"]/text()'
            stipend = tree.xpath(xpath_stipend)
            stipend = self.get_text_content(stipend)

            # intern type
            xpath_type = '//div[@class = "status status-small status-inactive"]/text()'
            type_ = tree.xpath(xpath_type)
            intern_type = [item for item in type_ if 'internship' in item.lower()]

            # Skills
            xpath_skills = '//*[@id="details_container"]/div[4]/div[2]/div[2]/span/text()'
            skills = tree.xpath(xpath_skills)

            # Perks
            xpath_perks = '//*[@id="details_container"]/div[4]/div[2]/div[6]/span/text()'
            perks = tree.xpath(xpath_perks)



            # hiring since
            xpath_opportunity = '//i[@class="ic-16-suggested-time"]/parent::div/div/text()'
            opportunity_date = tree.xpath(xpath_opportunity)
            opportunity_date = self.get_text_content(opportunity_date)

            # hired candidate
            xpath_hired_candidate = '//i[@class="ic-16-hired"]/following-sibling::div/text()'
            hired_candidate = tree.xpath(xpath_hired_candidate)
            hired_candidate = self.get_text_content(hired_candidate)

            #  website link

            print('---')
            all_data.append(
                [role, company_name, location_name, duration, stipend, intern_type, skills, perks, opportunity_date,
                 hired_candidate])

        return all_data

    def save_to_csv(self, data, filename='internship_data.csv'):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['Role', 'Company Name', 'Location', 'Duration', 'Stipend', 'Intern Type', 'Skills', 'Perks',
                 'Opportunity Date', 'Hired Candidate'])
            writer.writerows(data)
        print('Data written to', filename)

    def run(self):
        data = self.web_scrape()
        if data:
            self.save_to_csv(data)
        else:
            print('No data scraped.')






obj = InternShalaData()
obj.web_scrape()
obj.run()
