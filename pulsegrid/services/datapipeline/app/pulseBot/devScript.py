import asyncio
import re
import time
from urllib.parse import urlparse, urljoin
from curl_cffi import requests
import trafilatura
from courlan import extract_links
from bs4 import BeautifulSoup

regex_expression = re.compile(r"(?i)^https://(?:[a-zA-Z0-9\-]+\.)*sports\.ndtv\.com/[a-zA-Z0-9\-]+/[a-zA-Z0-9\-]+-\d+/?$")
time.sleep(5)
response = requests.get("https://sports.ndtv.com/", impersonate="chrome")

soup = BeautifulSoup(response.text, 'html.parser')
# for link in soup.find_all("a"):
#     href = link.get("href") or 
#     full_url = urljoin('https://www.thehindu.com/sci-tech/technology/', href)
#     print(href)

for a_tag in soup.find_all("a", href=True):
    raw_href = a_tag["href"].strip()
    
    # 1. Resolve relative links (e.g. "/sci-tech/technology/article1234.ece" -> full URL)
    full_url = urljoin('https://sports.ndtv.com/', raw_href)
    
    # 2. Clean tracking query parameters (e.g., ?utm_source=rss)
    clean_url = urlparse(full_url)._replace(query="", fragment="").geturl()

    # 3. Match against your exact URL prefix pattern
    if regex_expression.match(clean_url):
        print(clean_url)
    # print(clean_url)