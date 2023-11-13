from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import os
import json
from bs4 import BeautifulSoup
import pprint

def safe_open(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'r', encoding="utf-8")

def pp_json(json_thing, sort=False, indents=4):
      if type(json_thing) is str:
        return (json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
      else:
            return (json.dumps(json_thing, sort_keys=sort, indent=indents))
      
def new_listing():
    listing = {"businessname":"","individuallink":"",
          "location":"","website":"","phone":""}
    return listing
    
def load_json(path):
    with open(path) as json_data:
        data = json.load(json_data)
        json_data.close()
    return data    

def save_file(save_path, file_name):
    os.makedirs(save_path, exist_ok=True)
    n=os.path.join(save_path, file_name)
    return open(n, 'w', encoding="utf-8")

url = "http://ohioproud.org/farm-markets-all/farmers-market-search/find-a-farmers-market/#!directory/map"
prefix='https://www.sweetgrownalabama.org'
cwd = os.getcwd()
save_path = os.path.join(cwd, "OH/data")
html_path = os.path.join(cwd, "OH/data/ohioproud.html")
html = safe_open(html_path)


soup = BeautifulSoup(html, "html.parser")
#print(soup)
listings = []

elements=soup.find("div", id="SFylpcrd", class_="SFcrdlst")
all_a = elements.find_all("a", recursive=False)
for a in all_a:
    listing = new_listing()
    #print(a['title'], a['href'])
    listing['businessname'] = a['title']
    listing['individuallink'] = a['href']

    if listing not in listings:  
        listings.append(listing)

#Add locaction info
json_data = load_json("OH/data/0.json")

name_map = {}
for i in enumerate(listings):
    print(i[0])
    print(i[1]['businessname'])
    name_map.update({i[1]['businessname']: i[0]}) 
print(name_map)
    

for listing in json_data['usr']:
    ind = name_map.get(listing['nam'])
    if ind:
        #print(listing['loc'])
        listings[ind]['location'] = listing['loc']


pprint.pprint(listings)

with save_file(save_path, 'child_link.json') as fw:
    fw.write(pp_json(listings))
