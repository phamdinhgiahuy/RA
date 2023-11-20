import requests
import pandas as pd
from multiprocessing import Pool
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def check_url(driver, url):
    try:
        print(url)
        driver.get(url)
        driver.set_page_load_timeout(15)
        body = driver.find_element(By.XPATH, "/html/body")
        print(body.text)

        driver.implicitly_wait(1)
        if body:
            return "good", ""
        else:
            return "bad", "no body in HTML"

    except Exception as e:
        print("Cannot access url: \n\n\n",e)
        return "bad", str(e)

def process_row(args):
    index, row = args
    url = row['url']
    driver = webdriver.Firefox()  # Create the webdriver instance here
    try:
        status, error = check_url(driver, url)
        return index, pd.Series({'web_status': status, 'web_error': error})

    finally:
        driver.quit()


def safe_open(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'r', encoding="utf-8")



if __name__ == '__main__':
    excels_folder = 'checkbystate'
    excels = ['checkbystate\\00_MN_results_status_checked.xlsx']
    for excel_path in excels:
        df = pd.read_excel(excel_path, sheet_name=0, usecols=['state', 'title', 'url', 'domain', 'web_status', 'web_error'])
        
        df = df[df['web_status'] == 'bad']
        df_blocked = df[df['web_error'].str.find('404 Client Error:') == -1]
        df_blocked = df_blocked[4:10]
        excel_out_path = excel_path.replace('.xlsx', "") + "_status_validated.xlsx"

        df["sel_web_status"] = ''
        df["sel_web_error"] = ''
        url_list = df_blocked['url']
        #print(url_list)
        #driver = webdriver.Firefox()
        #Define the number of processes to use (you can adjust this based on your system's capabilities)
        # num_processes = 4
        
        # # Use Pool to parallelize the processing
        # with Pool(processes=num_processes) as pool:
            
        #     results = pool.map(process_row, df_blocked.iterrows())
        results = list(map(process_row, df_blocked.iterrows()))
        print(results)
        
        for index, result in results:
            df_blocked.at[index, 'sel_web_status'] = result['web_status']
            df_blocked.at[index, 'sel_web_error'] = result['web_error']
        print(df_blocked)
        df_blocked.to_excel(excel_out_path)



 