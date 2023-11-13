from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import os
import json
from bs4 import BeautifulSoup
def safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')
def pp_json(json_thing, sort=False, indents=4):
      if type(json_thing) is str:
        return (json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
      else:
            return (json.dumps(json_thing, sort_keys=sort, indent=indents))
prefix='https://www.sweetgrownalabama.org'
cwd = os.getcwd()
html_path = os.path.join(cwd, "RA Code Hub/alllistings.html")
html = open(html_path, 'r', encoding="utf-8")

soup = BeautifulSoup(html, "html.parser")


listings = []

elements=soup.find_all("div",{"class":"flexbox"})

for elm in elements:
    
    divs = elm.find_all("div")
    item={"businessname":"","individuallink":"","location":"","website":"","phone":""}
    for div in divs:       
 
        if div.p is not None:
            item["location"] = div.p.text
            if div.p.parent.a is not None:
                item["businessname"] = div.p.parent.a.text
                item["individuallink"] = prefix + div.p.parent.a["href"]

        adds = div.find_all("a", href=re.compile(""))
        for add in adds:
            if add['href'] != None:
                if add['href'].find("tel") > -1:
                    item["phone"] = add.text
                if add.text.find('Website') > -1:
                    item["website"] = add['href']

    if item not in listings:  
        listings.append(item)
       
with safe_open_w("data/listings.json") as fw:
    fw.write(pp_json(listings))

    
