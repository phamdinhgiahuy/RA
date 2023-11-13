import requests
import pandas as pd
from multiprocessing import Pool, cpu_count
import os

def check_url(args):
    url, headers = args
    try:
        print(url)
        r = requests.get(url, timeout=5, headers=headers)
        if r.status_code == requests.codes.ok:
            return "good", ""
        else:
            r.raise_for_status()
    except Exception as e:
        print(e)
        return "bad", str(e)

def process_row(args):
    index, row = args
    url = row['url']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
    status, error = check_url((url, headers))
    return index, pd.Series({'web_status': status, 'web_error': error})


def safe_open(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'r', encoding="utf-8")

def list_excel(folder):
    files_path = []
    
    for file in os.listdir(folder):
        if file.startswith("00") & file.endswith(".xlsx"):
            files_path.append(os.path.join(folder, file))
    return files_path

print(cpu_count())
# if __name__ == '__main__':
#     excels_folder = 'checkbystate'
#     excels = list_excel(excels_folder)
#     for excel_path in excels:
#         df = pd.read_excel(excel_path, sheet_name=0, usecols=['state', 'title', 'url', 'domain' ])
#         excel_out_path = excel_path.replace('.xlsx', "") + "_status_checked.xlsx"

#         df["web_status"] = ''
#         df["web_error"] = ''
#         url_list = df.url

#         # Define the number of processes to use (you can adjust this based on your system's capabilities)
#         num_processes = 6

#         # Use Pool to parallelize the processing
#         with Pool(processes=num_processes) as pool:
#             results = pool.map(process_row, df.iterrows())

#         # Update the DataFrame with the results
#         for index, result in results:
#             df.at[index, 'web_status'] = result['web_status']
#             df.at[index, 'web_error'] = result['web_error']

#         df.to_excel(excel_out_path)
