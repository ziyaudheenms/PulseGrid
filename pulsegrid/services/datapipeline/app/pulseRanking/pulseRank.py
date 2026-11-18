"""
Main module that which initiates the ranking of the atricle collections

Collection with more that 2 articles should get priority also all the articles in the db will be subjected to the ranking 
process of clickbaitk analysis and depth analysis for the quality of the articles and they will be awarded with some points.
"""
import asyncio
from typing import Any
from bson import ObjectId

import structlog
from pymongo.asynchronous.database import AsyncDatabase

from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

DEFAULT_BATCH_SIZE = 50


class PulseRank:
    def __init__(
        self,
        db: AsyncDatabase,
        concurrency_limit: int,
        max_retries: int,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be greater than zero")

        self.collection = db["articleCollection"]
        self.article_collection = db["articleMetaData"]
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.max_retries = max_retries
        self.batch_size = batch_size

    async def rank_collections(self) -> None:
        """
        We will be implementing the fetching of the records from the collection with the cursor based approch
        """
        last_seen_id = None

        while True:
            match_query: dict[str, Any] = {}

            if last_seen_id is not None:
                match_query["_id"] = {"$gt": last_seen_id}

            pipeline = [
                {"$match": match_query},
                {"$sort": {"_id": 1}},  #sorting thr documents with id is requird so that we can get the true last_seen_id
                {"$limit": self.batch_size},
                {
                    "$lookup": {
                        "from": self.article_collection.name,
                        "localField": "article_ids",
                        "foreignField": "_id",
                        #we dont need all the field of the dcument , so we would implement the project inside pipeline
                        "pipeline" : [
                            {
                                "$project": {
                                    "genunity_score": 1,
                                    "ranking_depth_score" : 1,
                                }
                            }
                        ],
                    "as": "articles", # the left joined collection will be stored in this document field
                    }
                },
            ]

            cursor = self.collection.aggregate(pipeline)

            #cursor will contain the documents from the collection with the articles joined in the articles field

            batch_collections : list[dict[str, Any]] = []

            async for collection_document in cursor:
                collection_dict = {
                    "_id" : collection_document.get("_id"),
                    "article_ids" : collection_document.get("article_ids"),
                    "articles" : collection_document.get("articles"),
                }

                batch_collections.append(collection_dict)

            if not batch_collections:
                logger.info("No more collections to process. Exiting.")
                break

            last_seen_id = ObjectId(batch_collections[-1]["_id"])

            #now we have to offload the batch to the ranking process
            await self.initialise_ranking(batch_collections)

            await asyncio.sleep(0.05)  #a pause btw each batch fetching




    async def initialise_ranking(
        self,
        collection_documents: list[dict[str, Any]],
    ) -> None:
        """
        Using asyncio we will fire up all the documents if the batch and will control them using the semaphore to limit the concurrency of the ranking process 
        """
        