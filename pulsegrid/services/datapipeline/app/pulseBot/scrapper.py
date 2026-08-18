"""
    This class is used to scrap the URLS that has beed crawled by the 
    PulseBotCrawler.

    Implementation :- 
    - curl_cffi --> newspaper4k(for title extraction) --> trafilatura(for content extraction).
    - to implement the human nature a pause of asyncio time sleep is implemented with a max retries of 3 times.
    - asyncio semaphore is used to control the async operation of the source URL collection with inside each collection the URLS 
      are processed batch by batch.
"""

from pymongo.asynchronous.database import AsyncDatabase

class PulseBotScrapper:
    def __init__(
            self,
             db: AsyncDatabase,
             concurrency_limit:int,
             max_retries:int = 3,
        ) -> None:
            self.db = db
            self.concurrency_limit = int(concurrency_limit)
            self.max_retries = max_retries  

    async def scrap_the_URL(self):
          pass

    async def load_the_collection(self):
          pass