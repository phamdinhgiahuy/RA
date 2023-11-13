#from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from bs4 import BeautifulSoup
import pprint
import json



def save_file(save_path, file_name):
    os.makedirs(save_path, exist_ok=True)
    n=os.path.join(save_path, file_name)
    return open(n, 'w', encoding="utf-8")

def pp_json(json_thing, sort=False, indents=4):
      if type(json_thing) is str:
        return (json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
      else:
            return (json.dumps(json_thing, sort_keys=sort, indent=indents))
    

def scroll_to_bottom(driver):

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return 


def web_access(url):
    driver = webdriver.Firefox()
    driver.get(url)
    scroll_to_bottom(driver)
    time.sleep(5)
    page_source = driver.page_source
    #print(page_source)
    with save_file(save_path, "ohioproud.html") as fw:
        fw.write(page_source)

    i=0
    for request in driver.requests:
        if request.response and str(request.url).find(header) > -1:
            print(request.url)
            print(request.response.status_code)
            if request.response.body:

                jfile= str(i)+".json"
                with save_file(save_path, jfile) as fw:
                    fw.write(pp_json(request.response.body.decode("utf-8")))
                    print("downloaded:", jfile)
                    i=i+1
    driver.quit()
    return

SCROLL_PAUSE_TIME = 1
cwd = os.getcwd()
save_path = os.path.join(cwd, "OH/data")
url = "http://ohioproud.org/farm-markets-all/farmers-market-search/find-a-farmers-market/#!directory/map"
header="https://api.membershipworks.com/v2/directory?"
web_access(url)





    
