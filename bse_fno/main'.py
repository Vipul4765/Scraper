import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime


class BSESCRAPER:
    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = uc.Chrome(options=options)
        self.dates = []

    @classmethod
    def get_curr_month(cls):
        return datetime.now().strftime('%B-%Y')  # Returns 3-letter month abbreviation (e.g., 'Jun')

    def scrape(self):
        try:
            self.driver.get("https://member.bseindia.com/")

            # Wait and click the main button
            wait = WebDriverWait(self.driver, 15)
            button = wait.until(EC.element_to_be_clickable(
                (By.ID, "FileGridVB1_gvFiles_ctl06_lbFolderItem")
            ))
            button.click()
            print("Clicked the specified button.")

            # Wait and click the Common folder button
            common_button = wait.until(EC.element_to_be_clickable(
                (By.ID, "FileGridVB1_gvFiles_ctl02_lbFolderItem")
            ))
            common_button.click()
            print("Clicked Common folder button.")

            # Get current month abbreviation and click corresponding button
            month_button = wait.until(EC.element_to_be_clickable(
                (By.ID, "FileGridVB1_gvFiles_ctl02_lbFolderItem")
            ))
            month_button.click()

            # Find all date elements using XPath
            date_elements = self.driver.find_elements(By.XPATH,
                                                      '//table[@id="FileGridVB1_gvFiles"]//tr[position()>1]/td[2]/a')

            # Extract text from each element and clean it
            for element in date_elements:
                date_text = element.text.strip()
                if date_text:
                    self.dates.append(date_text)

            selected_date = self.dates[-2].strftime('%d-%m-%Y')
            date_xpath = f"//a[contains(., '{selected_date}')]"
            selected_link = wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath)))
            selected_link.click()

        except Exception as e:
            print("Error:", e)
        finally:
            self.driver.quit()


if __name__ == "__main__":
    obj = BSESCRAPER()
    obj.scrape()