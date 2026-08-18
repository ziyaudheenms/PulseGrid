"""
    This class is used to scrap the URLS that has beed crawled by the 
    PulseBotCrawler.

    Implementation :- 
    - curl_cffi --> newspaper4k(for title extraction) --> trafilatura(for content extraction).
    - to implement the human nature a pause of asyncio time sleep is implemented with a max retries of 3 times.
    - asyncio semaphore is used to control the async operation of the source URL collection with inside each collection the URLS 
      are processed batch by batch.
"""

import asyncio
import datetime
import json
import random

import structlog
import trafilatura
import redis.asyncio as redis_asyncio
from newspaper import Article
from curl_cffi.requests import AsyncSession, Response
from curl_cffi.requests.errors import RequestsError
from pymongo.asynchronous.database import AsyncDatabase

from pulseBot.pulse_profiles import PROFILES
from schema.source_schema import CrawlObjectSchema
from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

class PulseBotScrapper:
    def __init__(
            self,
             db: AsyncDatabase,
             concurrency_limit:int,
             redis: redis_asyncio.Redis | None,
             max_retries:int = 3,
        ) -> None:
            self.db = db
            self.redis = redis
            self.max_retries = max_retries 
            self.profiles = PROFILES 
            self.semaphore = asyncio.Semaphore(concurrency_limit) # setting the asyncio threads to be openened by the OS at at a time.
            self.article = Article("") #setting up an plane article instance
            self.cache_key = 'pulsegrid:sources:article_meta_data:all'
            
    async def scrap_the_URL(self, session:AsyncSession, crawl_object:CrawlObjectSchema):
          async with self.semaphore:  #self.semaphore controls the simultaneous request opening by the given count
                  #implementing the retry mechanism , if the fucntion doesnt gets its return it will loop again
                  browser_profile = random.choice(self.profiles) # selects a ransom browser profile for each saperate URL
                  urls_to_scarp_the_content = crawl_object.article_urls  #this contains the list of the articles that are to be scrapped.

                  result_tracker: list[bool] = [] #is used to track the end result of the scrapping of each URL

                  #to mimic the human behaviour scrapping each request at a time of a web source and implemeting a time gap
                  for url in urls_to_scarp_the_content:
                        for attempt in range(self.max_retries):
                              try:
                                    response: Response = await session.get(url=url, impersonate=browser_profile.impersonate,  timeout=30, allow_redirects=True)
                                    if response.status_code == 200:
                                          logger.info("Successfully extracted the html data", url=url, source_id= crawl_object.source_id)

                                          #Next we have to extract the title and the body contents.
                                          self.article.download(input_html=response.text) #setting up the html content with the article instance
                                          self.article.parse()

                                          title_of_the_article = self.article.title #Getting the title of the article
                                          body_of_the_article = trafilatura.extract(response.text) #getthing the body of the article

                                          article_metadata =  {
                                                "crawl_object_id": crawl_object.id,
                                                "title":title_of_the_article,  
                                                "body": body_of_the_article,
                                                "created_at" : datetime.datetime.now(datetime.timezone.utc),  #date-time format to be used with mongo db 
                                                "updated_at" : datetime.datetime.now(datetime.timezone.utc)   #date-time format to be used with mongo db 
                                          }
                                          result = await self.db["articlearticleMetaData"].insert_one(article_metadata)

                                          if result.acknowledged:
                                                logger.info(f"added the article url into DB attempt-{attempt}", url=url, source_id=crawl_object.source_id)

                                                if self.redis is not None:
                                                      await self.redis.rpush(
                                                            self.cache_key,
                                                            json.dumps(article_metadata, default=str),
                                                      )
                                                      logger.info(f"successfully cached the article attempt-{attempt}", url=url, source_id=crawl_object.source_id)
                                                      result_tracker.append(True)
                                                return True

                                          logger.info(f"failed to add the article metadata into DB, attempt-{attempt}", url=url, source_id=crawl_object.source_id)
                                          result_tracker.append(False)
                                          return False

                                    if response.status_code in (429, 502, 503):
                                          logger.warning("failed to fetch the content", url=url, source_id= crawl_object.source_id)  
                                    else:
                                          logger.warning("failed to fetch the content", url=url, source_id= crawl_object.source_id)  
                                                # return ScrapeResult(url, response.status_code, None, f"HTTP Status {response.status_code}")
                              
                              except RequestsError as req_err:
                                    logger.error(f"network error on attempt - {attempt + 1}", url=url, source_id= crawl_object.source_id)  
                              except Exception as e:
                                    logger.error(f"Unexpected error on attempt - {attempt+1}", url=url, source_id= crawl_object.source_id)

                              # A pause for mimiking the human nature
                              backoff = (2 ** attempt) + random.uniform(0.1, 0.5)
                              logger.error(f"ATTEMPT FAILED :- trying to fetch the URL again attempt-{attempt}", url=url, source_id= crawl_object.source_id)

                              await asyncio.sleep(backoff)
                        logger.info("Unfortunate,cant scrap the content", url=url, source_id=crawl_object.source_id)
                        result_tracker.append(False)
                        return False

                  if all(result_tracker):
                        return True
                  else:
                        return False


    async def load_the_collection(self, crawlObjects:list[CrawlObjectSchema]):
          async with AsyncSession() as session:
                  #assiging and calling all the functions for each of the sources that exists
                  tasks = [
                        self.scrap_the_URL(session=session, crawl_object=crawl_source)
                        for crawl_source in crawlObjects
                  ]
      
                  #next we have to call the tasks asychronously controlled by the semaphore concurrency rate
                  results = await asyncio.gather(
                        *tasks, return_exceptions=True   
                  )
      
                  logger.info(f"completed the scrapping function here the results are" , result = results)
      
                  return results