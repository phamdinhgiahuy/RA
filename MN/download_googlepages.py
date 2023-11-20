#coding=utf-8
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import logging
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
from timeout_decorator import timeout
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

@timeout(30)  



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

def save_url_conent(myitem,content,anws="",comments=""):
    id = myitem["Unnamed: 0"]
    type = myitem["type"]
    url = myitem["url"]
    dict={"1":"individual","2":"listings","3":"other","4":"bad link"}

    if comments:
        if anws=="1":
            if comments=="a":
                comments="farmers market website"
            if comments == "b":
                comments = "city website"
            if comments=="c":
                comments="event"
            if comments == "d":
                    comments = "news"
            if comments=="e":
                comments="a list on a directory"
            if comments=="f":
                comments="closed"
            if comments=="n":
                comments=""
        elif anws == "2":
            if comments=="a":
                comments="directory"
            if comments == "b":
                comments = "orgnization"
            if comments=="c":
                comments="event"
            if comments == "d":
                    comments = "news"
            if comments=="n":
                comments=""

    filename="data/files1/"+str(type)+"_"+str(id)+".txt"
    if os.path.exists(filename):
        return
    else:
        with safe_open_w(filename) as fw:
            #fw.write(pp_json(myitem))
            #fw.write("state: "+ myitem["state"])
            #fw.write(str(id))
            fw.write("state:   "+str(myitem["state"]) + "\n")

            fw.write("type:   " + str(dict[anws]) + "\n")
            fw.write(str(url)+"\n")
            fw.write("title:   "+str(myitem["title"])+"\n")
            fw.write("title_s: "+str(myitem["title_sub"])+"\n")
            fw.write("comments: " + str(comments) + "\n")
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

urls=convert_to_json_array(file,"excel",jsonfile,"Sheet1")

options = Options()
#options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--disable-proxy-certificate-handler")
options.add_argument("--disable-content-security-policy")
options.add_argument('--ignore-certificate-errors')
#options.add_argument('--allow-running-insecure-content')

#options.add_argument('--headless')
options.add_experimental_option('detach', True)
# options.add_argument("--disable-popup-blocking")
service = ChromeService(executable_path=r'C:\Users\Admin\Downloads\chromedriver-win64\chromedriver.exe')
#driver = webdriver.Chrome(service=service, options=options)
driver=webdriver.Chrome(service=service)
driver.implicitly_wait(0.5)
logging.getLogger('seleniumwire').setLevel(logging.ERROR)

i=0
for item in urls:
    print(item)
    id = item["Unnamed: 0"]
    type = item["type"]
    url = item["url"]
    filename = "data/files1/" + str(type) + "_" + str(id) + ".txt"
    if os.path.exists(filename):
        i=i-1
        continue
    if (type=="listings" or str(type)=="1") and url.find("facebook")==-1 and url.find("instagram")==-1:

        filename = "data/files1/" + str(type) + "_" + str(id) + ".txt"
        if os.path.exists(filename):
            continue
        #pprint.pprint(item)
        try:
            response = requests.get(url, timeout=15)
            page_re=""
            if response.status_code == 200:
                page_re = response.content
            driver.get(url)
            driver.set_page_load_timeout(15)
            #driver.implicitly_wait(1)
            
            if  driver.page_source==page_re:
                print(">>>>>>>>>>>>>>>>>> same")
                text=  driver.page_source
            else:
                if len(driver.page_source)>len(page_re):
                    print(">>>>>>>>>>>>>>>>>> use driver results")
                    text=  driver.page_source
                else:
                    time.sleep(3)
                    if len(driver.page_source) >= len(page_re):
                        text = driver.page_source
                    else:
                        print(">>>>>>>>>>>>>>>>>> use the request results")
                        text= page_re
            try:
                text = h.handle(text)
            except TimeoutError:
                print(f"Timeout occurred while processing HTML content. Moving on...")
            #text=h.handle(text)
            print("######",filename)
            #print(text)
            anws=input("website type: 1: individual 2:listings 3:other,4:bad link")
 
            if anws in ["1","2","3"]:
                if anws=="1":
                    comments = input("type of the website: a:farmersmarket b:city website c:event d:news e: a list on a directory f:closed n:nothing to report")
                elif anws == "2":
                    comments = input("type of the website: a:directory b:orgnization c:event d:news  n:nothing to report")
                else:
                    comments = input("put comments why you belive it belong to other category")
                try:

                    if comments:
                        save_url_conent(item, text, anws,comments)
                except Exception as e:
                    print("failed to save")
                    break
            elif anws=="4":
                save_url_conent(item, "", anws,"")
        except Exception as e:
            print("wrong", e)
            anws=input("url has problem, check, 4 is bad url")
            if anws == "4":
                save_url_conent(item, "", anws,"")

            pass

        #break

driver.quit()
