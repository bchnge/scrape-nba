import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup

s = requests.Session()

ip = '203.30.190.23'
port = '80'

# proxies = {
#     'http': 'http://' + ip + ':' + port,
#     'https': 'https://' + ip + ':' + port,
# }

proxies = {
    'socks5': 'socks5h://162.223.88.244:51236'
}

# Create the session and set the proxies.
s = requests.Session()
s.proxies = proxies

# retry = Retry(connect=10, backoff_factor=0.5)
# adapter = HTTPAdapter(max_retries=retry)
# s.mount('http://', adapter)

# Make the HTTP request through the session.
r = s.get('http://www.showmemyip.com/')
print(r)
print(r.text)
print(BeautifulSoup(r.text))