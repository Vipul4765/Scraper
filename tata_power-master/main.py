from lxml import etree
import requests
import urllib.parse
from io import BytesIO
from PIL import Image
from datetime import datetime


class DataFetching:
    def __init__(self):
        self.id = "60007179694"
        self.captcha_value = None

    session = requests.session()
    base_url = "https://www.tatapower-ddl.com/billpay/"

    def pre_request(self):
        response = self.session.get(self.base_url)
        tree = etree.HTML(response.content)
        view_state = tree.xpath("//input[@id='__VIEWSTATE']/@value")
        view_generator = tree.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value")
        event_validator = tree.xpath("//input[@id='__EVENTVALIDATION']/@value")

        xpath_expression = "//img[@id='Img']/@src"
        image = tree.xpath(xpath_expression)
        response_image = image[0]
        self.captcha_value = self.get_captcha(response_image)

        self.post_query(view_state, view_generator, event_validator)

    def post_query(self, view_state, view_generator, event_validator):
        payload = {
            '__VIEWSTATE': view_state,
            '__VIEWSTATEGENERATOR': view_generator,
            '__EVENTVALIDATION': event_validator,
            'txtcano': '60007179694',
            'txtmobile': '',
            'txtemail': 'gfhg@gmail.com',
            'TxtImgVer': self.captcha_value,
            'btnpay': 'Pay Now',
            'searchtext': ''
        }

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'close',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Origin': 'https://www.tatapower-ddl.com',
            'Referer': 'https://www.tatapower-ddl.com/billpay/paybillonline.aspx',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',

        }
        url = "https://www.tatapower-ddl.com/billpay/paybillonline.aspx"
        response = self.session.request("POST", url, headers=headers, data=payload )
        result = self.data_extraction(response)
        print(result)


    def get_captcha(self, url):
        captcha_url = urllib.parse.urljoin(self.base_url, url)
        captcha_image = self.session.get(captcha_url)

        image_io = BytesIO(captcha_image.content)
        image = Image.open(image_io)

        image.show()
        solve_captcha = input('Solve the Captcha: ')
        return solve_captcha

    def data_extraction(self,reponse):
        tree = etree.HTML(reponse.content)
        name = tree.xpath('//span[@id="lblname"]/text()')[0].replace('.','').strip()
        bill_no_date_number = tree.xpath('//span[@id="lblbillnobilldate"]/text()')[0]
        due_date = tree.xpath('//span[@id="lblduedate"]/text()')[0]
        bill_ = tree.xpath('//span[@id="lblexactbill"]/text()')[0]
        Amount = tree.xpath('//span[@id="lbloutstn"]/text()')[0]
        bill_no, bill_date = bill_no_date_number.split('/')
        bill_no = bill_no.strip()
        bill_ = bill_.strip()
        due_date = datetime.strptime(due_date,'%d-%b-%Y')
        due_date = due_date.strftime("%Y-%m-%d")
        return {

            'name':name,
            'bill_no':bill_no,
            'due_date': bill_date,
            'due_date': due_date,
            'exact_bill' : bill_,
            'outstanding_amount' : Amount
        }


obj = DataFetching()
obj.pre_request()
