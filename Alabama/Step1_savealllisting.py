from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from bs4 import BeautifulSoup

cwd = os.getcwd()
save_path = os.path.join(cwd, "RA Code Hub")

url = "https://www.sweetgrownalabama.org/find-sweet-grown"

def save_listing_html(save_path):
    os.makedirs(save_path, exist_ok=True)
    n=os.path.join(save_path, "alllistings.html")
    return open(n, 'w', encoding="utf-8")

def web_access(url):
    driver = webdriver.Firefox()
    driver.get(url)
    page_source = driver.page_source
    with save_listing_html(save_path) as fw:
        fw.write(page_source)
    driver.quit()
web_access(url)