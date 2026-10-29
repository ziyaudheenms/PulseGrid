"""
    This embed engine is used in order to generate the embedd vectors for the content 
    including the tile + description.

    here in this project we are using the SBERT model sentence-Transformer which has the cababilites to 
    hold the context of long sentences and paragraphs. This also is build based on the transformer architecture and
    fine tunned over the BERT to hold the context and proper symmantic structure of the long content.

    Actually we dont need to generate the embeddings with the complete heading ad with complete discription 
    in place we can take like Title + first sentence or like first two sentences so that we can reduce the 
    unwanted computation.

    for the process of that extraction of the sentence we are using the nlp 'scapy'


    also the sentence transformer the python wrapper is synchroneous by default such that it bloxks the main thtread
    so we have to run it in a executor to cope up with the async flow.
"""

import asyncio
import random
from typing import Any
import spacy
from functools import partial
from sentence_transformers import SentenceTransformer
import structlog
import redis.asyncio as redis_asyncio
from pymongo.asynchronous.database import AsyncDatabase
from sympy import true
from transformers import NllbMoePreTrainedModel
from schema.source_schema import ArticleMetaData
from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()


#this is the class we are using for implementing the embeddings
class PulseCleanEmbedd():
    def __init__(
            self,
            db:AsyncDatabase,
            redis: redis_asyncio.Redis | None,
            concurrency_limit:int,
            max_retries:int = 3,
            transformer_model = ''
        ):

        self.db = db
        self.semaphore = asyncio.Semaphore(concurrency_limit)   #semaphore of asyncio is used to handle the no of concurrent request to shoot up from the OS
        self.retry = max_retries
        self.redis = redis
        self.transformer = SentenceTransformer(transformer_model)
        self.nlpAnalyzer = spacy.load('en_core_web_sm')  #this nlp model is used to extract the much wanted details from the article content that which we have to processs
        self.max_retries = max_retries
        self.collection = self.db["articleMetaData"]

    def extract_semantic_heart(
      self, title: str, description: str, num_sentences: int = 1
    ) -> str:
        
        """Uses spaCy to safely extract the title + true first sentence(s)
        without breaking on decimals ($280.0M) or abbreviations (Inc., Dr.).
        """
        clean_title = title.strip()
        clean_desc = description.strip()

        lead_text = ""
        if clean_desc:
        # Process description through spaCy pipeline
            doc = self.nlpAnalyzer(clean_desc)
            sentences = list(doc.sents)

        # Extract the specified number of leading sentences safely
        core_sentences = sentences[:num_sentences]
        lead_text = " ".join([sent.text.strip() for sent in core_sentences])

        # Combine title with the extracted semantic heart
        if lead_text:
            return f"{clean_title}. {lead_text}"
        return clean_title


    async def embedd_content(self, article: ArticleMetaData):
        """
        this method of embeddd class  is used to handle the embedding of the content, 
        as of the architecture we are planning of merging the title + description into a content and implemnentng the embedding
        """

        async with self.semaphore:
            """
            controlling the operation of the embedding function asynchronoulsy using the semaphore boundary limits
            """
            formatted_content = self.extract_semantic_heart(title=article.title, description=article.body)
            
            #the embedding process is of sync nature so we have to run this in a saperate loop
            loop = asyncio.get_running_loop() #gives the current event loop that which is executing the engine
            vector_list = None
            pause_time = 2

            for attempt in range(1, self.max_retries + 1):
                #we have to offload the transformer embedding into thread_pool

                try:
                    #partial is used in order to pass the args into the executer thread loop
                    encoding_task = partial(
                        self.transformer.encode,
                        formatted_content,
                        normalize_embeddings=True,
                    )

                    embedding = await loop.run_in_executor(None, encoding_task)
                    vector_list = embedding.tolist()
                    break
                except Exception as e:
                    logger.error("Cant generate the embedding right now", url=article.url, crawl_id=article.crawl_object_id, id= article.id)

                if self.max_retries == attempt:
                    logger.error("Max Retries reached, we cant generate the embeddings", url=article.url, crawl_id=article.crawl_object_id, id= article.id)
                    break

                backoff = (2 ** attempt) + random.uniform(0.1, 0.5)
                logger.info(f"Retrying URL in {backoff:.2f}s...", url=article.url, crawl_id=article.crawl_object_id, id= article.id)
                await asyncio.sleep(backoff) #this is used to genreate the 'pause btw each retries

            if not vector_list:
                logger.error("Cant find the vector embedding of this document", url=article.url, crawl_id=article.crawl_object_id, id= article.id)
                return

             
            try:
                updated_article_record = await self.collection.update_one(
                    {
                        "_id": article.id
                    },
                    {
                        "$set" : {
                            "embedding" : vector_list,
                            "status" : "Embedded"
                        }
                    }
                )
                if updated_article_record.matched_count == 0:
                    logger.error("No matching document is found", url=article.url, crawl_id=article.crawl_object_id, id= article.id)
                    return

                logger.info("successfully embedded the article", url=article.url, crawl_id=article.crawl_object_id, id= article.id)
                return
            
            except Exception as db_err:
                logger.error("Database update failed for this article", url=article.url, crawl_id=article.crawl_object_id, id= article.id)
                return   

    
    async def execute_batch(self, articles: list[ArticleMetaData], batch_no:str):
        """Class method: Takes a pre-fetched list of articles and runs them
        concurrently using self.embeddContent and internal semaphore controls.
        """
        if not articles:
            return []

        tasks = [self.embedd_content(article) for article in articles]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Completed the embedding of the current batch", result=results, batch = batch_no)
        return results

    
    async def fetch_article_batch(self, batch_size:int):
        """
            Through this function we are fetching the artciles from the database
            using the cursor based one , where we directlty point to the cursor for which we have to start
            picking up the batch.
        """

        last_seen_id = None

        while True:

            #assigining the pydantic verification for like saying that the query dict can have string as the key and type 'Any'
            query : dict[str, Any] = {
                "$or": [
                    {"status": {"$exists": False}},
                    {"status": {"$ne": "Embedded"}}
                ]
            }

            if last_seen_id:
                query["_id"] = {"$gt": last_seen_id}


            cursor = (
                self.collection.find(query)
                .sort("_id", 1)
                .limit(batch_size)
            )

            raw_docs = await cursor.to_list(length=batch_size)

            if not raw_docs:
                logger.info("All articles batched and completed the process")
                break

            article_batch_list : list[ArticleMetaData] = [ArticleMetaData.model_validate(article) for article in raw_docs]  #converted the list of articles into pydantic list of article models

            #offloading this in to our batch execution engine
            batch_no = str(last_seen_id) if last_seen_id else 'initial batch'
            await self.execute_batch(articles=article_batch_list, batch_no=batch_no)
            last_seen_id = raw_docs[-1]["_id"]  # assing the last id of the current batch so that the next iteration can direclty get into that id we required.

            await asyncio.sleep(0.05)
    
