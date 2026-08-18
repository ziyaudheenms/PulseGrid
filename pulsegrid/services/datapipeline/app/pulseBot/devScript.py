import asyncio
import re
import time
from urllib.parse import urlparse, urljoin
from curl_cffi import requests
import trafilatura
from courlan import extract_links
from bs4 import BeautifulSoup

# regex_expression = re.compile(r"(?i)^https://(?:[a-zA-Z0-9\-]+\.)*espn\.(?:in|com)/[a-zA-Z0-9\-]+/story/_/id/\d+/[a-zA-Z0-9\-]+/?$")
# time.sleep(5)
# response = requests.get("https://www.espn.in/", impersonate="chrome")

# soup = BeautifulSoup(response.text, 'html.parser')
# # for link in soup.find_all("a"):
# #     href = link.get("href") or 
# #     full_url = urljoin('https://www.thehindu.com/sci-tech/technology/', href)
# #     print(href)

# for a_tag in soup.find_all("a", href=True):
#     raw_href = a_tag["href"].strip()
    
#     # 1. Resolve relative links (e.g. "/sci-tech/technology/article1234.ece" -> full URL)
#     full_url = urljoin('https://www.espn.in/', raw_href)
    
#     # 2. Clean tracking query parameters (e.g., ?utm_source=rss)
#     clean_url = urlparse(full_url)._replace(query="", fragment="").geturl()

#     # 3. Match against your exact URL prefix pattern
#     if regex_expression.match(clean_url):
#         print(clean_url)
#     # print(clean_url)



# #SCRAPPING OF THE WEBSITE

# import json
# import trafilatura

# # # 1. Fetch the raw HTML content from the URL
# url = "https://www.theverge.com/tech/978323/whisker-litter-robot-5-pro-review"
# downloaded = trafilatura.fetch_url(url)
# # # 2. Extract the main body text (strips ads, footers, and sidebars)
# # result = trafilatura.extract(downloaded)


# extracted_json = trafilatura.extract(html_raw, output_format="json")

# if extracted_json:
#     data = json.loads(extracted_json)
    
#     title = data.get("title")
#     text = data.get("raw_text")
#     author = data.get("author")
#     date = data.get("date")

#     print(f"Title: {title}")
# print(result)

# import newspaper
# a = newspaper.article('https://www.theverge.com/tech/978323/whisker-litter-robot-5-pro-review')
# a.download()
# a.parse()
# print(a.text)


import asyncio
from curl_cffi.requests import AsyncSession
import trafilatura
from newspaper import Article

article = Article("")
async def main():
    async with AsyncSession() as s:
        response = await s.get("https://www.theverge.com/report/980933/trump-border-wall-big-bend-arizona-cottonwood-tree-sit", impersonate="chrome")
        if response.status_code == 200:
            article.download(input_html=response.text)
            article.parse()
            print("article title:-", article.title)

            print("...........CONTENT BODY...........")
            body = trafilatura.extract(response.text)
            print(body)

asyncio.run(main())
