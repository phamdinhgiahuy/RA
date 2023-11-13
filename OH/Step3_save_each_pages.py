from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import os
import json
from bs4 import BeautifulSoup

def load_json(path):
    with open(path) as json_data:
        data = json.load(json_data)
        json_data.close()
    return data

def save_pages(save_path, id):
    os.makedirs(save_path, exist_ok=True)
    n=os.path.join(save_path, id + ".html")
    return open(n, 'w', encoding="utf-8")

json_data = load_json('OH/data/child_link.json')
#pages = []
save_folder = 'OH/data/listed_page/'
prefix = "http://ohioproud.org/farm-markets-all/farmers-market-search/find-a-farmers-market/"
#cwd = os.getcwd()
pages_count = len(json_data)
for data in json_data[2:3]:
    pages_count += -1
    print(f'{pages_count} pages left to save')
    page = prefix+ data['individuallink']
    page_id = page.replace(prefix, "")
    page_id = page_id.replace("/", "_")[2:]
    try:
        driver = webdriver.Firefox()
        driver.get(page)
        driver.implicitly_wait(2)
        page_source = driver.page_source
        with save_pages(save_folder, page_id) as fw:
            fw.write(page_source)
        input("Wait: ")
        #driver.quit()
        time.sleep(1)
        
        print("Done saving page: ", page)
   
    except Exception as e:
        print("Can not save page: ", page, e)