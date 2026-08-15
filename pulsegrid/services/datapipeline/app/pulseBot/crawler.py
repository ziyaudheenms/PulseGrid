"""
    This PulseBot crawler is responsible for crawling the URLS from the provided websources so that for fetching the data
"""

import asyncio
from datetime import date
import random
import re
from typing import List
from urllib.parse import urlparse, urljoin

import structlog
from curl_cffi.requests import AsyncSession, Response
from curl_cffi.requests.errors import RequestsError
from bs4 import BeautifulSoup
from pymongo.asynchronous.database import AsyncDatabase

from .schema import BrowserProfile
from app.core.logging import setup_logging
from schema.source_schema import SourceSchema

setup_logging()
logger = structlog.get_logger()

# async def main():
#      async with AsyncSession(impersonate="chrome") as session:
#         results = await asyncio.gather(*(session.get(url) for url in urls))   #asyncio.gather is the method that is used to run the functions asychronosly
#         return [r.status_code for r in results]


# print(asyncio.run(main()))





class PulseBot:
    def __init__(
            self,
            db: AsyncDatabase,
            profiles: List[BrowserProfile],
            concurrency_limit:int,
            max_retries:int = 3,
        ):

        self.db = db
        self.profiles = profiles
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(concurrency_limit)  # semaphore is a asyncio method used in python that is used to control the no of asyncio connections that is been issued by the OS at a time.

    async def pulse_crawl(self, session: AsyncSession,source:SourceSchema) -> bool:

        async with self.semaphore:  #self.semaphore controls the simultaneous request opening by the given count
            #implementing the retry mechanism , if the fucntion doesnt gets its return it will loop again
            for attempt in range(self.max_retries):
                browser_profile = random.choice(self.profiles) # selects a ransom browser profile for each saperate URL

                try:
                    logger.info(f"trying to fetch-{source.source_url} attempt-{attempt}")
                    response: Response = await session.get(url=source.source_url, impersonate=browser_profile.impersonate, headers=browser_profile.headers, timeout=30, allow_redirects=True)

                    if response.status_code == 200:
                        #we have successfully got the html content, now we need to parse it so that to get all the urls present in it and want to filter out the unwanted urls.\
                        logger.info(f"successfully fetched-{source.source_url} attempt-{attempt}")
                    
                        #encoding the regex pattern to identify the pattern matching
                        pattern_str = source.regex_pattern
                        # If the DB returned literal escaped backslashes '\\', unescape them:
                        if "\\\\" in pattern_str or "\\d" in pattern_str:
                            pattern_str = pattern_str.encode("utf-8").decode("unicode_escape")

                        regex_website_pattern = re.compile(pattern_str)

                        html_soup = BeautifulSoup(response.text, 'html.parser')
                        logger.info(f"trying to parse the html-{source.source_url} attempt-{attempt}")

                        seen_urls = set() #set datatype is used in order to prevent the addition of duplicate urls.
                        urls_to_be_inserted = []

                        for a_tag in html_soup.find_all("a", href=True):
                            raw_href = a_tag["href"].strip()
                            
                            full_url = urljoin('https://sports.ndtv.com/', raw_href)
                            
                            # 2. Clean tracking query parameters (e.g., ?utm_source=rss)
                            clean_url = urlparse(full_url)._replace(query="", fragment="").geturl()

                            # 3. Match against your exact URL prefix pattern
                            if regex_website_pattern.match(clean_url):
                                if clean_url not in seen_urls:
                                     seen_urls.add(clean_url)
                                     logger.info(f"adding the new url found-{clean_url} of the url-{source.source_url} attempt-{attempt}")
                                     urls_to_be_inserted.append(clean_url)  # the clean url which is not duplicate is inserted and added into the URL list


                        #object to be added into the database
                        urls_database_object = {
                             "source_id" : source.id,
                             "no_of_urls":len(urls_to_be_inserted),  #the number of urls fetched
                             "article_urls": urls_to_be_inserted,
                             "created_at" : date.today(),
                             "updated_at" : date.today()
                        }

                        result = await self.db["articleURLS"].insert_one(urls_to_be_inserted)
                        if result.acknowledged:
                             logger.info(f"added the article urls into DB of website url-{source.source_url} attempt-{attempt}")
                             return True
                        logger.info(f"failed to add the article urls into DB of website url-{source.source_url} attempt-{attempt}")
                        return False

                    if response.status_code in (429, 502, 503):
                            logger.warning(f"RATE LIMITED ({response.status_code}) on {source.source_url}. Retrying...")    
                    else:
                        logger.warning(f"HTTP {response.status_code} for {source.source_url}")
                        # return ScrapeResult(url, response.status_code, None, f"HTTP Status {response.status_code}")
                except RequestsError as req_err:
                        logger.error(f"Network error on attempt {attempt+1} for {source.source_url}: {req_err}")
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt+1} for {source.source_url}: {e}") 

                #implementing a pause in between so that to feel human like and to prevent from the rate limting or blockings
                # Exponential backoff with random jitter before retry
                backoff = (2 ** attempt) + random.uniform(0.1, 0.5)
                logger.error(f"ATTEMPT FAILED :- trying to fetch the URL-{source.source_url} again attempt-{attempt}")
                await asyncio.sleep(backoff)

            logger.info(f"Unfortunate , pulseBot is unbale to crawl {source.source_url}, max retries exceeded the limits!")
            return False

    async def fetch_urls(self):
         pass


