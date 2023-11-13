import os
import glob
import time
import json
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flatten_json import flatten
import ast
from urlextract import URLExtract
from urllib.parse import urlparse
from datetime import timedelta, date,datetime
from collections import OrderedDict
import bs4
import pprint
from nltk.tokenize import RegexpTokenizer, sent_tokenize, word_tokenize
tokenizer = RegexpTokenizer(r'\w+')

def safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')

def pp_json(json_thing, sort=False, indents=4):
      if type(json_thing) is str:
        return (json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
      else:
            return (json.dumps(json_thing, sort_keys=sort, indent=indents))
      
def get_template_new(current_datetime_string, host):
    return {"extract_time": current_datetime_string, "source": host, "tag": "", "state": "",
            "update_date": current_datetime_string[:10], "individuallink": "","lid":"",
            "businessname": "",
            "address": {
                "address": "", "address_desc": "", "street": "", "city": "", "zipcode": "",
                "location_type": "",
                "county": "", "county_fips": "", "lat": "", "lon": "", "urbanization": "", "censusregion": "",
                "censusfivision": "", },
            "phones": "", "emails": "",
            "manager_name": "", "mailing_address": "", "manager_phones": "", "manager_email": "",
            "website": {
                "url": "", "update_date": "", "website_type": "", "contact": "", "email": "",
                "phone": "", "has_contactform": "", "about": "", "operation_schedule": "",
                "products": "", "fmnp": "", "start_year": "",
                "other_websites": "", "notes": ""
            },
            "facebook": {"url": "", "update_date": "", "address": "", "contact": "", "email": "", "phone": "",
                         "about": ""},
            "instagram": {"url": "", "update_date": "", "notes": ""},
            "twitter": {"url": "", "update_date": "", "notes": ""},
            "urls":[],
            "operation_schedule": {"json": [], "desc": "","source":""},
            "payment": {"json": [], "desc": ""},
            "fmnp": {"json": [], "desc": "","source":""},
            "products": {"json": [], "desc": "","source":""},
            "num_vendor":"",
            "about": "", "amenities": "", "affiliations": "", "market_organizer": "", "market_startyear": "",
            "docname": "", "notes": "","parent_id":-1
            }

def get_currenttime():
    # Get the current date and time
    current_datetime = datetime.now()
    # Convert the datetime object to a string
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')
def find_operation_schedule(mytext):
    tmp=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
         'sunday', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
         'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december',
    'jan', 'feb', 'mar', 'apr', 'may', 'jun',
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec',"year round", "year-round","yearround",
         "spring","fall","winter","summer"
         ]
    myarr = tokenizer.tokenize(mytext.lower())
    for key in myarr:
        if key in tmp:
           return True
    return False

def find_payments(mytext):
    tmp=["cash","credit","debit"]
    myarr = tokenizer.tokenize(mytext.lower())
    for key in myarr:
        if key in tmp:
           return True
    return False

def find_fnmp(mytext):
    tmp=["wic","ewic","fmnp","sfmnp","snap","cfm","wfmnp"]
    myarr = tokenizer.tokenize(mytext.lower())
    for key in myarr:
        if key in tmp:
           return True
    for t in tmp:
       if mytext.lower().find(t)>-1:
           return True
    return False

def load_json(path):
    with open(path, 'r') as json_data:
        data = json.load(json_data)
        json_data.close()
    return data

def savefile_safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'r', encoding= 'utf-8')

def scrape_bio(soup, template):
    #bio section
    bio = soup.find("div", id="bio_section")

    #get businessname, tag, city, state
    template["businessname"] = bio.find('h2').text
    if template["businessname"].find("Market")>-1 and template["businessname"].find("Farm Market")==-1:
        template["tag"]="farmersmarket"
    else:
        template["tag"]="farm"
    template["address"]["city"], template["state"] = bio.find('h4').text.split(',')
    #print(template)
    #get about info
    about = bio.find("div", id="farm-bio")
    template["about"] = about.text

    #get social media info
    media = bio.find("ul", class_="social-links")
    if media.find("a", class_="icon-facebook") != None:
        template["facebook"]["url"] = media.find("a", class_="icon-facebook")['href']
    if media.find("a", class_="icon-instagram") != None:
        template["instagram"]["url"] = media.find("a", class_="icon-instagram")['href']
    if media.find("a", class_="icon-twitter") != None:
        template["twitter"]["url"] = media.find("a", class_="icon-twitter")['href']

    #get operation hours "operation_schedule": {"json": [], "desc": "","source":""},
    oper = bio.find("div", class_="farm-hours")
    if oper != None:
        template["operation_schedule"]["desc"] = oper.p.text

    #Products section "products": {"json": [], "desc": "","source":""}
    products = soup.find("div", id="product_list")
    if products != None:
        template["products"]["desc"] = products.text.strip()
    return template

def scrape_details(soup, template):
    #detail section with contact info: tel, address, website, email
    detail = soup.find("div", id="detail_section")
    for i in detail.find_all("div", class_="flex-grid-unit"):
        zip = i.find(string=re.compile(r"\d{5}"))
        if zip != None:
            template["address"]["zipcode"] = zip
        address = i.find(string=re.compile(r"\d+\s+([A-Z])\w+"))
        if address != None:
            template["address"]["address"] = zip
            m = re.match(r"(?P<number>\d+) (?P<street>([A-Z])\w+.*)", address)
            if m != None:
                template["address"]["street"] = m["street"]
        
        phone = i.find("p", string = re.compile(r"\d+-\d+"))
        if phone != None:
            template["phone"] = phone.text

        contact = i.find_all(href=True)
        for j in contact:
            if j.text.find(r'@') != -1:
                template["emails"] = j.text
            if j.text.find(r'-') != -1:
                template["phone"] = j['href']
            if j.text.find(r'https:') != -1:
                template["website"]["url"] = j['href']
    return template



save_folder = 'data/listed_page/'
prefix = "https://www.sweetgrownalabama.org/"

#get list of child pages
htmlfiles = []
for file in glob.glob(save_folder + "*.html"):
    htmlfiles.append(file)
#print(htmlfiles)

items=[]
for i in htmlfiles:
    cur_time = get_currenttime()
    template = get_template_new(cur_time, i)
    html = savefile_safe_open_w(i)


    #save individuallink                                                                                                                                                                                                                                                   \").replace("_","/")
    childlink = prefix + i.strip(".html"+save_folder).replace("_","/")[1:]
    template["individuallink"] = childlink
    soup = BeautifulSoup(html, "html.parser")

    #bio section
    template = scrape_bio(soup, template)

    #purchase channel:
    purchase = soup.find("div", id="purchase_locations")
    #print(purchase.find_all(p))

    #detail section with contact info: tel, address, website, email
    template = scrape_details(soup, template)

    #save in items list 
    if template not in items:
         items.append(template)


with safe_open_w("data/child_listings.json") as fw:
    fw.write(pp_json(items))

print(f"Done exporting listing data for {len(items)}/{len(htmlfiles)} children pages")
#pprint.pprint(len(items))











