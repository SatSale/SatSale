from lnpbp_testkit.cadr import network
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import sys
import os

print("Initializing driver")
chrome_options = webdriver.ChromeOptions()
if not "DISPLAY" in os.environ:
    chrome_options.add_argument("headless")

driver = webdriver.Chrome(chrome_options=chrome_options)

print("Warming up network")
network().warm_up(channels=True)

print("Initializing payment")
driver.get("http://127.0.0.1:5000")
driver.find_element_by_id("amount").send_keys("5")
driver.find_element_by_id("amount").send_keys(Keys.RETURN)
sleep(10)
print("Retrieving invoice")
invoice = driver.find_element_by_id("address").text
network().auto_pay("lightning:" + invoice)
for i in range(16):
    sleep(1)
    print("Checking status")
    if driver.find_element_by_id("status").text == "Payment finalised. Thankyou!":
        print("Success")
        sys.exit(0)

print("LN payment failed")
sys.exit(1)
