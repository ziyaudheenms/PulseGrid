"""
    This PulseBot crawler is responsible for crawling the URLS from the provided websources so that for fetching the data
"""

import asyncio
from datetime import date
import datetime
import random
import re
from typing import List
from urllib.parse import urlparse, urljoin
import json

import structlog
from curl_cffi.requests import AsyncSession, Response
from curl_cffi.requests.errors import RequestsError
from bs4 import BeautifulSoup
from pymongo.asynchronous.database import AsyncDatabase
import redis.asyncio as redis_asyncio

from pulseBot.pulse_profiles import PROFILES

from .schema import BrowserProfile
from core.logging import setup_logging
from schema.source_schema import SourceResponceSchema

setup_logging()
logger = structlog.get_logger()

class PulseBotCrawler:
    def __init__(
            self,
            db: AsyncDatabase,
            redis: redis_asyncio.Redis | None,
            concurrency_limit:int,
            max_retries:int = 3,
        ):

        self.db = db
        self.profiles = PROFILES
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(concurrency_limit)  # semaphore is a asyncio method used in python that is used to control the no of asyncio connections that is been issued by the OS at a time.
        self.redis = redis
        self.cache_key = "pulsegrid:sources:crawl:all"  #this key in the redis is used to store all the results --> urls_database_object


    async def pulse_crawl(self, session: AsyncSession,source:SourceResponceSchema) -> bool:
        #session is used to persist the cokkies or other details of the request and the browser which helps to hit with same config in retries.
        async with self.semaphore:  #self.semaphore controls the simultaneous request opening by the given count
            #implementing the retry mechanism , if the fucntion doesnt gets its return it will loop again
            for attempt in range(self.max_retries):
                browser_profile = random.choice(self.profiles) # selects a ransom browser profile for each saperate URL

                try:
                    logger.info(f"trying to fetch-{source.source_url} attempt-{attempt}")
                    response: Response = await session.get(url=source.source_url, impersonate=browser_profile.impersonate,  timeout=30, allow_redirects=True)

                    if response.status_code == 200:
                        #we have successfully got the html content, now we need to parse it so that to get all the urls present in it and want to filter out the unwanted urls.\
                        logger.info(f"successfully fetched-{source.source_url} attempt-{attempt}")
                    
                        #encoding the regex pattern to identify the pattern matching
                        pattern_str = source.crawl_pattern
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
                            
                            full_url = urljoin(source.source_url, raw_href)
                            
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
                             "created_at" : datetime.datetime.now(datetime.timezone.utc),  #date-time format to be used with mongo db 
                             "updated_at" : datetime.datetime.now(datetime.timezone.utc)   #date-time format to be used with mongo db 
                        }

                        result = await self.db["articleURLS"].insert_one(urls_database_object)
                        if result.acknowledged:
                             logger.info(f"added the article urls into DB of website url-{source.source_url} attempt-{attempt}")
                            #  urls_database_object["id"] = result.inserted_id

                             #STORING THE RESULTS IN THE REDIS CACHE FOR EASY RETRIEVL
                             #storing in the redis by utilizing the redis LIST
                             # STORING THE RESULTS IN THE REDIS CACHE FOR EASY RETRIEVAL
                             # Append the newly generated payload to the right side of the Redis list
                             if self.redis is not None:
                                    await self.redis.rpush(
                                        self.cache_key,
                                        json.dumps(urls_database_object, default=str),
                                    )
                                    logger.info(
                                        f"appended crawl result to redis list key-{self.cache_key} for source-{source.source_url}"
                                    )
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

    async def fetch_urls(self, sources:list[SourceResponceSchema]):
         """
            Using this function we have to implement the fetching of the given url objects.
         """

         logger.info(f"starting with the pulseBot-Crawler to get all the URLS")

         async with AsyncSession() as session:
              #assiging and calling all the functions for each of the sources that exists
              tasks = [
                   self.pulse_crawl(session=session, source=source)
                   for source in sources
              ]

              #next we have to call the tasks asychronously controlled by the semaphore concurrency rate
              results = await asyncio.gather(
                *tasks, return_exceptions=True   
              )

              logger.info(f"completed the crawling function here the results are" , result = results)

              return results