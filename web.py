import splinter
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


driver = webdriver.Firefox()
#driver.implicitly_wait(10) # seconds
driver.get('https://10.10.61.30:8006/apprecovery/admin')

try:
    WebDriverWait(driver, 3).until(EC.alert_is_present())
    asd = driver.switch_to_alert()
    asd.send_keys("Administrator")
    asd.send_keys(Keys.TAB + '123asdQ')
    asd.accept()

except TimeoutException:
    print("no alert")
    driver.close()

try:
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ".//*[@id='protectMachine']/div[1]/span")))
    new = driver.find_element_by_xpath(".//*[@id='protectMachine']/div[1]/span")
    new.click()
    print("DONE")
    #arrow = driver.find_element_by_xpath('//div[@id="protectMachine"]/div/span')
    #arrow.click()

finally:
    print("no alert")
    driver.close()