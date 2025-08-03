import requests
from lxml import etree
from PIL import Image
from io import BytesIO
from datetime import datetime


class InvalidCaptcha(Exception):
    pass


class Tin:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'close',
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    session = requests.session()
    base_url = "https://tinxsys.com/TinxsysInternetWeb/searchByTin_Inter.jsp"
    captcha_url ="https://tinxsys.com/TinxsysInternetWeb/images/simpleCaptcha.jpg"
    tin_number = "09137500718"

    def __init__(self):
        self.captcha_result = None

    def pre_request(self):
        response = self.session.get(self.base_url, headers=self.headers, verify=False)
        tree = etree.HTML(response.content)
        self.captcha_fetch(tree)

    def captcha_fetch(self,tree):
        x_path_url = tree.xpath("//img[@id='captcha']/@src")
        if x_path_url:
            # Combine with the base URL
            full_url = 'https://tinxsys.com' + str(x_path_url[0])
            self.captcha_image(full_url)
        else:
            print("Image source URL not found.")


    def captcha_image(self, full_url):
        print(full_url)
        image_byte = self.session.get(full_url)
        print(image_byte)
        image_io = BytesIO(image_byte.content)
        image = Image.open(image_io)
        image.show()
        solve_captcha = input('Solve the Captcha: ')
        self.captcha_result = solve_captcha
        self.search_tin()

    def search_tin(self):
        base_url = "https://tinxsys.com/TinxsysInternetWeb/dealerControllerServlet"
        params = {
            "tinNumber": self.tin_number,
            "answer": self.captcha_result,
            "searchBy": "TIN",
            "backPage": "searchByTin_Inter.jsp"
        }
        response_= self.session.get(base_url, params=params)
        tree= etree.HTML(response_.content)

        self.data_fetch(tree)

    def date_format(self,data):
        if not data:
            return ''
        try:
            date_object = datetime.strptime(data, '%d/%m/%y')
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            return ''

    def check_for_empty_string(self,data):

        if not data:
            return ''
        else:
            data = data[0].strip()
            return data

    def data_fetch(self,tree):
        cst_number = tree.xpath("//div[contains(text(), 'CST Number')]/parent::td/following-sibling::td/div/text()")
        dealer_number = tree.xpath("//div[contains(text(), 'Dealer Name')]/parent::td/following-sibling::td/div/text()")
        dealer_address = tree.xpath("//div[contains(text(), 'Dealer Address')]/parent::td/following-sibling::td/div/text()")
        state_name = tree.xpath("//td[contains(text(), 'State Name')]/following-sibling::td/text()")
        pan_number = tree.xpath("//td[contains(text(), 'PAN')]/following-sibling::td/text()")
        date_of_registration_under_cst_act = tree.xpath("//div[contains(text(),'Date of Registration under CST Act')]/parent::td/following-sibling::td/div/text()")
        dealer_registration_status_under_cst_act = tree.xpath("//td[contains(text(),'Dealer Registration Status under CST Act')]/following-sibling::td/text()")
        valid_as_on = tree.xpath("//td[contains(text(),'This record is valid as on')]/following-sibling::td/text()")

        # Assuming the variables are already defined
        date_of_registration_under_cst_act = self.check_for_empty_string(date_of_registration_under_cst_act)
        valid_as_on = self.check_for_empty_string(valid_as_on)


        data_dict = {
            'cst_number': self.check_for_empty_string(cst_number),
            'dealer_number': self.check_for_empty_string(dealer_number),
            'dealer_address': self.check_for_empty_string(dealer_address),
            'state_name': self.check_for_empty_string(state_name),
            'pan_number': self.check_for_empty_string(pan_number),
            'date_of_registration_under_cst_act': self.date_format(date_of_registration_under_cst_act),
            'dealer_registration_status_under_cst_act': self.check_for_empty_string(dealer_registration_status_under_cst_act),
            'valid_as_on': self.date_format(valid_as_on)
        }

        print(data_dict)


obj = Tin()
obj.pre_request()

thonny