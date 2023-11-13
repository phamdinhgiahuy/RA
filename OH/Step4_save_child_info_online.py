from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import re
import os
import json
from bs4 import BeautifulSoup
import pprint
from datetime import timedelta, date,datetime

def safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')

def pp_json(json_thing, sort=False, indents=4):
      if type(json_thing) is str:
        return (json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
      else:
            return (json.dumps(json_thing, sort_keys=sort, indent=indents))

def load_json(path):
    with open(path) as json_data:
        data = json.load(json_data)
        json_data.close()
    return data

def save_pages(save_path, id):
    os.makedirs(save_path, exist_ok=True)
    n=os.path.join(save_path, id + ".html")
    return open(n, 'w', encoding="utf-8")

def get_currenttime():
    # Get the current date and time
    current_datetime = datetime.now()
    # Convert the datetime object to a string
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')

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


json_data = load_json('OH/data/child_link.json')
#pages = []
save_folder = 'OH/data/listed_page/'
prefix = "http://ohioproud.org/farm-markets-all/farmers-market-search/find-a-farmers-market/"
#cwd = os.getcwd()
pages_count = len(json_data)
items =[]
for data in json_data:
    pages_count += -1
    print(f'{pages_count} pages left to save')
    page = prefix+ data['individuallink']
    page_id = page.replace(prefix, "")
    page_id = page_id.replace("/", "_")[2:]
    try:
        driver = webdriver.Firefox()
        driver.get(page)
        driver.implicitly_wait(1)
        
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#SFbizmnu0"))).click()
        #content1 = driver.find_element(By.CSS_SELECTOR, 'div.SFbizbox:nth-child(6)')
        element_about = driver.find_element(By.CSS_SELECTOR, "#SFpne")
        elementHTML1 = element_about.get_attribute('outerHTML')
        elementSoup1 = BeautifulSoup(elementHTML1,'html.parser')

        
        driver.implicitly_wait(1)
        contact = driver.find_element(By.CSS_SELECTOR, '#SFbizmnu1')
        driver.execute_script("arguments[0].click();", contact)
        #element_contact = driver.find_element(By.CSS_SELECTOR, '#SFbizctc5b474eabf033bfbf37af2da3')
        
        element_contact = driver.find_element(By.CSS_SELECTOR, '#SFbizpne1')
        elementHTML2 = element_contact.get_attribute('outerHTML')
        elementSoup2 = BeautifulSoup(elementHTML2,'html.parser')
        #pprint.pprint(element)
        
        #pprint.pprint(elementSoup1)
        #print("aaaaaa")
        #pprint.pprint(elementSoup2)
        cur_time = get_currenttime()
        template = get_template_new(cur_time, page)
        template["individuallink"] = data['individuallink']
        template["businessname"] = data['businessname']
        medias = elementSoup1.find_all("a", class_="SFbizpfu")
        #print(medias)
        for i in medias:
            if i['title'].find(r'Facebook') != -1:
                template["facebook"]["url"] = i['href']
            if i['title'].find(r'Instagram') != -1:
                template["instagram"]["url"] = i['href']
            if i['title'].find(r'Twitter') != -1:
                template["twitter"]["url"] = i['href']


        abouts = elementSoup1.find_all("div", class_="SFbizbox")
        for about in abouts:

            if about.text.find(r'Farm Market Products') != -1:
                prod_desc = template["products"]["desc"]
                for i in about.stripped_strings:
                    prod_desc = prod_desc + "/n" + i
                template["products"]["desc"] = prod_desc
            if about.text.find(r'Product Description') != -1:
                prod_desc = template["products"]["desc"]
                for i in about.stripped_strings:
                    prod_desc = prod_desc + "/n" + i
                template["products"]["desc"] = prod_desc

            if about.find("p"):
                template["about"] = about.text


        contacts = elementSoup2.find("div", class_="SFbizinf")
        #print(contacts.contents)
        tel = elementSoup2.find("a", class_="SFbizctcphn")
        if tel:
            template["phones"] = tel.text 
        biz_web = elementSoup2.find("a", class_="SFbizctcweb")
        if biz_web:
            template["website"]['url'] = biz_web['href']
        manager = elementSoup2.find("div", class_="SFbizctcctc") 
        if manager:
            template["manager_name"] = manager.text   
        map = elementSoup2.find("div", id="SFbizmap") 
        if map:
            map_json = json.loads(map['json-adr'])
            #print(map_json.keys())
            if "ad1" in map_json.keys():
                template["address"]["street"] = map_json["ad1"]
            if "cot" in map_json.keys():
                template["address"]["county"] = map_json["cot"]
            if "sta" in map_json.keys():
                template["state"] = map_json["sta"]
            if "zip" in map_json.keys():
                template["address"]["zipcode"] = map_json["zip"]
            if "cit" in map_json.keys():
                template["address"]["city"] = map_json["cit"]
            if "loc" in map_json.keys():
                template["address"]["lat"] = map_json["loc"][0]
                template["address"]["lon"] = map_json["loc"][1] 
                            
        if contacts.address:
            template["address"]["address"] = contacts.address.text 

        #print(template)

        if template not in items:
            items.append(template)
            print(f"Added {template['businessname']} to final json")
   
    except Exception as e:
        print("Can not save page: ", page)
        print(f"Error: {e}")
    finally:
        driver.quit()
with safe_open_w("OH/data/child_listings.json") as fw:
    fw.write(pp_json(items))

print(f"Done exporting listing data for {len(items)}/{len(json_data)} children pages")