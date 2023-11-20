import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import spacy

nlp = spacy.load('en_core_web_md')

def extract_features(text):
    doc = nlp(text)
    return doc.vector

url = 'http://www.clearlakefarmersmarket.com/'


#'https://bringmethenews.com/minnesota-living/heres-where-to-find-farmers-markets-in-minneapolis-in-2023' sele not req

#cookies = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}

#r = requests.post('http://wikipedia.org', cookies=cookies)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
        #   'Upgrade-Insecure-Requests': '1',
        #   'TE' : 'trailers',
        #   'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        #   'cache-control' : 'max-age=0, public'}
	
try:
    r = requests.get(url, timeout=10, headers=headers)
    if r.status_code == requests.codes.ok:
        print("good")
        soup = BeautifulSoup(r.text, 'html.parser')
        text_soup = ' '.join([st for st in soup.stripped_strings])
        print(text_soup)
        text_data = ' '.join([p.text for p in soup.find_all('p')])
        print("Text data:  \n\n\n", text_data)

    else:
        r.raise_for_status()
except Exception as e:
    print(e)

def web_access(url):
    driver = webdriver.Firefox()
    driver.get(url)
    body = driver.find_element(By.XPATH, "/html/body")
    print(body.text)
    driver.implicitly_wait(2)
    driver.quit()
web_access(url)
