import requests
url = 'https://www.axios.com/local/twin-cities/2021/11/16/winter-farmers-markets-near-minneapolis-st-paul'

cookies = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}

r = requests.post('http://wikipedia.org', cookies=cookies)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
        #   'Upgrade-Insecure-Requests': '1',
        #   'TE' : 'trailers',
        #   'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        #   'cache-control' : 'max-age=0, public'}
	
try:
    r = requests.get(url, timeout=10, headers=headers)
    if r.status_code == requests.codes.ok:
        print("good")
    else:
        r.raise_for_status()
except Exception as e:
    print(e)

