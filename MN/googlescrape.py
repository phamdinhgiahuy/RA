#coding=utf-8
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import brotli
from selenium.webdriver.support.ui import Select
import time
import os
import json
import pprint
from bs4 import BeautifulSoup
import re
import pandas as pd
import requests
from urlextract import URLExtract
import html2text
h = html2text.HTML2Text()
h.ignore_links = False
h.mark_code=True
h.wrap_links=True
h.wrap_list_items=True
h.open_quote="^["
h.close_quote="]^"

h.skip_internal_links=False
h.ignore_images=True
h.body_width=False
h.protect_links=True
h.images_to_alt=True
h.ignore_emphasis=False

h.escape_snob=True
#h.single_line_break=True
#h.emphasis=True
#h.emphasis_mark=True

h.skip_internal_links=False
h.links_each_paragraph=True


#h.blockquote=True
h.bypass_tables = False

h.ignore_tables=False

from newspaper import Article

from urllib.parse import urlparse

import warnings

warnings.filterwarnings('ignore')

def pp_json(json_thing, sort=False, indents=4):
    if type(json_thing) is str:
        return (json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        return (json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None

def safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'a', encoding="utf-8")

def convert_to_json_array(filename, filetype, returnfilename,tab=""):
    if filetype == "csv":
        df = pd.read_csv(filename)
        df.to_json(returnfilename, orient='records')
        f = open(returnfilename, "r", encoding="utf-8")
        return json.load(f)
    else:
        if tab:
            df = pd.read_excel(filename, sheet_name=tab)
        else:
            df=pd.read_excel(filename)
        df.to_json(returnfilename, orient='records')
        f = open(returnfilename, "r", encoding="utf-8")
        return json.load(f)

def save_url_conent(myitem,content):
    id = myitem["id"]
    type = myitem["type"]
    url = myitem["url"]
    filename="data/files1/"+str(type)+"_"+str(id)+".txt"
    if os.path.exists(filename):
        return
    else:
        with safe_open_w(filename) as fw:
            #fw.write(pp_json(myitem))
            #fw.write("state: "+ myitem["state"])
            #fw.write(str(id))
            fw.write("state:   "+str(myitem["state"]) + "\n")
            fw.write("type:    "+str(type)+"\n")
            fw.write(str(url)+"\n")
            fw.write("title:   "+str(myitem["title"])+"\n")
            fw.write("title_s: "+str(myitem["title_sub"])+"\n")

            #fw.write("title_sub: "+ myitem["title_sub"])
            fw.write("\n```````````````````````````````````````\n")
            fw.write("~~marketname:\n")
            fw.write("~~region:\n")
            fw.write("~~loop items:n\n")
            fw.write("~~format: text\n")
            fw.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
            fw.write(content)
            print("saved to",filename)

def get_short_content(url,myhtml):
    text = h.handle(myhtml)
    article = Article(url)
    article.download()
    article.parse()
    atext=article.text
    #print("####################################")
    #print(text)
    #print("####################################")
    #print(article.title)
    #print(atext)
    if article.title and article.title in text:
        return "~~title: "+article.title+"\n"+text.split(article.title)[1]
    return text



file="MN/00_MN_results.xlsx"
jsonfile=file.rstrip(".xlsx")+".json"
if os.path.exists(jsonfile):
    f=open(jsonfile, "r", encoding="utf-8")
    urls=json.load(f)
else:
    #filename, filetype, returnfilename,tab=""
    urls=convert_to_json_array(file,"excel",jsonfile,"Sheet3")

options = Options()
options.add_argument("--disable-notifications")
#options.add_argument('--headless')
options.add_experimental_option('detach', True)
options.add_argument("--disable-popup-blocking")

driver=webdriver.Chrome()
driver.implicitly_wait(0.5)

i=0
for item in urls[:3]:
    print(item)
    id = item['Unnamed: 0']
    type = item["Data Condition"]
    url = item["url"]
    filename = "data/files1/" + str(type) + "_" + str(id) + ".txt"
    if os.path.exists(filename):
        i=i-1
        continue
    if (type=="listings" or type=="1") and url.find("facebook")==-1 and url.find("instagram")==-1:

        #pprint.pprint(item)
        try:
            driver.get(url)
            driver.implicitly_wait(5)
            text = get_short_content(url, driver.page_source)
            print(filename)
            print(text)
            try:
                save_url_conent(item, text)
            except:
                print("failed to save")
                break
        except:
            pass

        #break

driver.quit()
