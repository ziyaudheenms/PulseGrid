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
        concurrency_limit: int,
        redis: redis_asyncio.Redis | None,
        max_retries: int = 3,
    ) -> None:
        self.db = db
        self.redis = redis
        self.max_retries = max_retries 
        self.profiles = PROFILES 
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.cache_key = 'pulsegrid:sources:article_meta_data:all'

    async def _process_single_url(self, session: AsyncSession, url: str, crawl_object: CrawlObjectSchema) -> bool:
        """Helper method to handle scraping and saving a single URL with retries."""
        async with self.semaphore:
            browser_profile = random.choice(self.profiles)
            
            for attempt in range(1, self.max_retries + 1):
                try:
                    response: Response = await session.get(
                        url=url, 
                        impersonate=browser_profile.impersonate,  
                        timeout=30, 
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        logger.info("Successfully extracted the html data", url=url, source_id=crawl_object.source_id)

                        # Create a fresh Article instance per request to avoid race conditions
                        article = Article("")
                        article.download(input_html=response.text)
                        article.parse()

                        title_of_the_article = article.title
                        body_of_the_article = trafilatura.extract(response.text)

                        article_metadata = {
                            "crawl_object_id": crawl_object.id,
                            "title": title_of_the_article,  
                            "body": body_of_the_article,
                            "url" : url,
                            "created_at": datetime.datetime.now(datetime.timezone.utc),
                            "updated_at": datetime.datetime.now(datetime.timezone.utc),
                        }
                        
                        # MongoDB mutates dict in-place by adding `_id`
                        result = await self.db["articleMetaData"].insert_one(article_metadata)

                        if result.acknowledged:
                            logger.info(f"Added article metadata into DB (attempt {attempt})", url=url, source_id=crawl_object.source_id)

                            if self.redis is not None:
                                # Convert ObjectId or datetimes gracefully for Redis caching
                                cache_data = {**article_metadata, "_id": str(article_metadata.get("_id"))}
                                await self.redis.rpush(
                                    self.cache_key,
                                    json.dumps(cache_data, default=str),
                                )
                                logger.info(f"Successfully cached article (attempt {attempt})", url=url, source_id=crawl_object.source_id)
                            
                            return True

                        logger.warning(f"Failed to write article metadata to DB (attempt {attempt})", url=url, source_id=crawl_object.source_id)

                    else:
                        logger.warning(f"HTTP status {response.status_code} received", url=url, source_id=crawl_object.source_id)

                except RequestsError as req_err:
                    logger.error(f"Network error on attempt {attempt}: {req_err}", url=url, source_id=crawl_object.source_id)
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt}: {e}", url=url, source_id=crawl_object.source_id)

                # Exponential backoff delay before retrying
                if attempt < self.max_retries:
                    backoff = (2 ** attempt) + random.uniform(0.1, 0.5)
                    logger.info(f"Retrying URL in {backoff:.2f}s...", url=url, source_id=crawl_object.source_id)
                    await asyncio.sleep(backoff)

            logger.error("Failed to scrape URL after max retries", url=url, source_id=crawl_object.source_id)
            return False

    async def scrap_the_URL(self, session: AsyncSession, crawl_object: CrawlObjectSchema) -> bool:
        urls_to_scrape = crawl_object.article_urls
        result_tracker: list[bool] = []

        for url in urls_to_scrape:
            success = await self._process_single_url(session, url, crawl_object)
            result_tracker.append(success)
            
            # Brief human pause between scraping individual URLs within the same source
            await asyncio.sleep(random.uniform(1.0, 2.5))

        return all(result_tracker) if result_tracker else False

    async def load_the_collection(self, crawlObjects: list[CrawlObjectSchema]):
        async with AsyncSession() as session:
            tasks = [
                self.scrap_the_URL(session=session, crawl_object=crawl_source)
                for crawl_source in crawlObjects
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("Completed scraping all sources", result=results)
            return results