import requests
import pandas as pd

df = pd.read_excel(r"MN\work_00_MN_results.xlsx", sheet_name=0)
df["web_status"] = '' #iloc 19 print(df.iloc[:,19])
df["web_error"] = '' #iloc 20
url_list = df.url#.dropna()
headers = {'User-Agent': 'ozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
url = 'https://httpbin.org/status/404'
count = 0
for i in url_list.index:
    #print(df.iloc[i,])
    try:
        r = requests.get(url_list[i], timeout=2, headers=headers)
        if r.status_code == requests.codes.ok:
            print("good")
            #df['web_status'][i] = "good"
            df.iloc[i, 19] = "good"
        else:
            r.raise_for_status()
            
    except Exception as e:
        print(e)
        print("bad")
        df.iloc[i, 19] = "bad"
        #df['web_status'][i] = "bad"
        df.iloc[i, 20] = e
        #df['web_error'][i] = e
    finally:
        count += 1
        print(f'{len(url_list.index) - count} remaining urls to check')

df.to_csv(r"MN\work_00_MN_status_check.csv")
