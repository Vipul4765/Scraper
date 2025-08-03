from bs4 import BeautifulSoup
import json

class DrivingLicenseParser:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            html_content = file.read()

        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.result_json = {}

    def extract_text(self, tag):
        return tag.get_text(strip=True) if tag else None

    def save_to_json(self, filename='output.json'):
        with open(filename, 'w') as json_file:
            json.dump(self.result_json, json_file, indent=2)

    def extract_information(self):
        # Extracting Information
        current_status_tag = self.soup.find('td', string='Current Status')
        self.result_json["current_status"] = self.extract_text(current_status_tag.find_next('td')) if current_status_tag else None

        holder_name_tag = self.soup.find('td', string="Holder's Name")
        self.result_json["holder_name"] = self.extract_text(holder_name_tag.find_next('td')) if holder_name_tag else None

        old_new_dl_no_tag = self.soup.find('td', string='Old / New DL No.')
        self.result_json["old_new_dl_no"] = self.extract_text(old_new_dl_no_tag.find_next('td')) if old_new_dl_no_tag else None

        source_of_data_tag = self.soup.find('td', string='Source Of Data')
        self.result_json["source_of_data"] = self.extract_text(source_of_data_tag.find_next('td')) if source_of_data_tag else None

        # Driving License Initial Details
        initial_issue_date_tag = self.soup.find('td', string='Initial Issue Date')
        self.result_json["initial_issue_date"] = self.extract_text(initial_issue_date_tag.find_next('td')) if initial_issue_date_tag else None

        initial_issuing_office_tag = self.soup.find('td', string='Initial Issuing Office')
        self.result_json["initial_issuing_office"] = self.extract_text(initial_issuing_office_tag.find_next('td')) if initial_issuing_office_tag else None

        # Driving License Endorsed Details
        last_endorsed_date_tag = self.soup.find('td', string='Last Endorsed Date')
        self.result_json["last_endorsed_date"] = self.extract_text(last_endorsed_date_tag.find_next('td')) if last_endorsed_date_tag else None

        last_endorsed_office_tag = self.soup.find('td', string='Last Endorsed Office')
        self.result_json["last_endorsed_office"] = self.extract_text(last_endorsed_office_tag.find_next('td')) if last_endorsed_office_tag else None

        last_completed_transaction_tag = self.soup.find('td', string='Last Completed Transaction')
        self.result_json["last_completed_transaction"] = self.extract_text(last_completed_transaction_tag.find_next('td')) if last_completed_transaction_tag else None

        # Driving License Validity Details
        non_transport_valid_from_tag = self.soup.find('span', string='Non-Transport').find_next('span', class_='font-bold').find_next('td')
        self.result_json["driving_license_validity_details"] = {
            "non_transport": {
                "valid_from": self.extract_text(non_transport_valid_from_tag),
                "valid_upto": self.extract_text(non_transport_valid_from_tag.find_next('td'))
            }
        }

        transport_valid_from_tag = self.soup.find('span', string='Transport').find_next('span', class_='font-bold').find_next('td')
        self.result_json["driving_license_validity_details"]["transport"] = {
            "valid_from": self.extract_text(transport_valid_from_tag),
            "valid_upto": self.extract_text(transport_valid_from_tag.find_next('td'))
        }

        hazardous_valid_till_tag = self.soup.find('span', string='Hazardous Valid Till').find_next('td')
        self.result_json["hazardous_valid_till"] = self.extract_text(hazardous_valid_till_tag)

        hill_valid_till_tag = self.soup.find('span', string='Hill Valid Till').find_next('td')
        self.result_json["hill_valid_till"] = self.extract_text(hill_valid_till_tag)

        # Class Of Vehicle Details
        class_of_vehicle_details = []
        table = self.soup.find('div', class_='ui-datatable')
        if table:
            for row in table.select('tbody tr'):
                columns = row.find_all('td')
                cov_category = self.extract_text(columns[0])
                class_of_vehicle = self.extract_text(columns[1])
                cov_issue_date = self.extract_text(columns[2])
                class_of_vehicle_details.append({
                    'cov_category': cov_category,
                    'class_of_vehicle': class_of_vehicle,
                    'cov_issue_date': cov_issue_date
                })

        self.result_json["class_of_vehicle_details"] = class_of_vehicle_details