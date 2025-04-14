import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome()
try:
    driver.get("https://stake.com/casino/games/crash")

    time.sleep(5)

    # Example: Find elements
    button = driver.find_element(By.CSS_SELECTOR, ".button-tag.variant-neutral.svelte-yomd1r")
    button.click()
    # for element in elements:
    #     print(element.text)
    print()

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()