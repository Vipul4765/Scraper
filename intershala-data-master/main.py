import requests
from lxml import etree
import csv
import re
from urllib.parse import urljoin


class InternShalaData:
    count = 1
    error = 1
    loop_whole = 1
    session = requests.Session()
    base_url = "https://internshala.com/internships/page-{}"
    page_number = 1


    def get_text_content(self, tree, xpath_expression):
        """
        Safely retrieves text content from an XPath expression.

        Parameters:
        - tree: The lxml etree object.
        - xpath_expression: The XPath expression to select the desired element.

        Returns:
        - Text content if found, otherwise an empty string.
        """
        elements = tree.xpath(xpath_expression)
        if elements:
            return elements[0].strip()
        else:
            return ''

    def scrape_page(self):
        count = 1
        response = self.session.get(self.base_url.format(self.page_number))
        self.page_number += 1
        if response.status_code == 200:
            print("Request successful! Status code:", response.status_code)
            data = etree.HTML(response.content)
            print(self.count)
            self.count += 1
            internship_elements = data.xpath('//*[@internshipid]')
            internship_ids = [element.get('internshipid') for element in internship_elements]
            internship_data = []

            for internship_id in internship_ids:
                temp_internship_data = []

                tree = data.xpath(f'//div[@internshipid="{internship_id}"]')
                resp = etree.tostring(tree[0], encoding='unicode')
                href_regex = r'href="([^"]*)"'

                # Find href attribute value using regular expression
                match = re.search(href_regex, resp)
                new_tree = etree.HTML(resp)

                # Retrieve role
                role_xpath = '//*[@class="heading_4_5 profile"]/text()'
                role = self.get_text_content(new_tree, role_xpath)

                # Retrieve company name
                company_name_xpath = './/div[@class="company_and_premium"]/p/text()'
                company_name = self.get_text_content(new_tree[0], company_name_xpath)

                # Retrieve location
                location_xpath = './/*[@id="location_names"]/span/a/text()'
                location = self.get_text_content(new_tree[0], location_xpath)

                # Retrieve start date
                start_date_xpath = '//*[@id="start-date-first"]/span[1]/text()'
                start_date = self.get_text_content(new_tree[0], start_date_xpath).replace('\xa0', ' ')

                # Retrieve duration
                duration_xpath = f'//*[@id="individual_internship_{internship_id}"]/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/text()'
                duration = self.get_text_content(new_tree[0], duration_xpath)

                # Retrieve type
                type_xpath = '//*[@class="other_label_container"]/div[@class="status-container"]/div/text()'
                type_ = self.get_text_content(new_tree, type_xpath)

                # Retrieve stipend
                stipend_xpath = '//*[@class="stipend"]/text()'
                stipend = self.get_text_content(new_tree[0], stipend_xpath)


                # internship detail
                if match:
                    href_value = match.group(1)
                    self.internship_detail(href_value)

                temp_internship_data.extend([role, company_name, location, start_date, duration, type_, stipend])
                internship_data.append(temp_internship_data)
                print(count)
                count+=1

            return internship_data
        else:
            print("Failed to fetch page. Status code:", response.status_code)
            return None

    def internship_detail(self, href_value):
        base_url = "https://internshala.com"
        view_detail_url = urljoin(base_url, href_value)
        response = requests.get(view_detail_url)
        if response.status_code == 200:
            data = response.text
            tree = etree.HTML(data)

            # skills
            xpath_expression = '//*[@id="details_container"]/div[2]/div[2]/div[2]//span[@class="round_tabs"]/text()'
            skills = tree.xpath(xpath_expression)

            # perks
            xpath_perks = '//*[@id="details_container"]/div[2]/div[2]/div[6]/span/text()'
            perks = tree.xpath(xpath_perks)

            # job opening
            xpath_job_opening = '//*[@id="details_container"]/div[2]/div[2]/div[9]/text()'
            job_opening = tree.xpath(xpath_job_opening)

            # opportunity posted
            xpath_job_opportunity = '//*[@id="details_container"]/div[2]/div[2]/div[11]/div[2]/div[2]/div/text()'
            job_opportunity = tree.xpath(xpath_job_opportunity)

            # hired candidate
            xpath_hired_candidate = '//*[@id="details_container"]/div[2]/div[2]/div[11]/div[2]/div[3]/div'
            hired_candidate = tree.xpath(xpath_hired_candidate)



            #  website link
            print(self.error)
            self.error += 1

    def get_all_companies(self):
        all_internship_data = []

        for i in range(1, 10):
            internship_data = self.scrape_page()
            if internship_data:
                all_internship_data.extend(internship_data)
            else:
                break

        with open('internship_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ROLE', 'Company Name', 'location', 'Start Date', 'Duration', 'Type', 'Stipend'])
            writer.writerows(all_internship_data)
        print('Done')


obj = InternShalaData()
obj.get_all_companies()
