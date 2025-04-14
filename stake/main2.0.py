from selenium import webdriver
import time
driver = webdriver.Chrome()
url = 'https://www.google.com'
driver.get(url)
print(driver.title)
print(driver.current_url)
driver.save_screenshot('curr.png')
time.sleep(5)
