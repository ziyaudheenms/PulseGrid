"""
Main module that which initiates the ranking of the atricle collections

Collection with more that 2 articles should get priority also all the articles in the db will be subjected to the ranking 
process of clickbaitk analysis and depth analysis for the quality of the articles and they will be awarded with some points.
"""
import math
import asyncio
from typing import Any
from bson import ObjectId

import structlog
from pymongo.errors import BulkWriteError
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
        self.genunity_low_threshold = 0.30
        self.genunity_hihg_threshold = 0.60
        self.popularity_factor_weight = 0.40  # Weight for the popularity factor in the final score
    async def rank_collections(self) -> None:
        """
        We will be implementing the fetching of the records from the collection with the cursor based approch
        """
        last_seen_id = None
        logger.info(
            "Initializing the Ranking process for the batch of collections",
            batch_size=self.batch_size
        )

        batch_final_processing_result =[]

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
            batch_id = str(last_seen_id) if last_seen_id else "Initial Batch"  # Using the last seen ID as the batch ID
            
            bool_result = await self.initialise_ranking(batch_collections, batch_id=batch_id)
            logger.info(
                "Batch processing completed",
                batch_id=batch_id,
                update_success=bool_result
            )
            batch_final_processing_result.append(bool_result)
            await asyncio.sleep(0.05)  #a pause btw each batch fetching



        if False in batch_final_processing_result:
            logger.info(
                "All batches havent compltly processed genunity score",
                results = batch_final_processing_result
            )
        else:
            logger.info(
                "All batches successfully passed genunity score",
                results = batch_final_processing_result
            )
            
        return




    async def initialise_ranking(
        self,
        collection_documents: list[dict[str, Any]],
        batch_id: str,
    ) -> None:
        """
        Using asyncio we will fire up all the documents if the batch and will control them using the semaphore to limit the concurrency of the ranking process 
        """
        if not collection_documents:
            logger.info(
                "No collections to rank in this batch.", 
                batch_id=batch_id
            )

            return
        
        logger.info(
            "Starting ranking for batch",
            batch_id=batch_id,
            num_collections=len(collection_documents)
        )

        tasks = [self._start_ranking_collection(collection_document) for collection_document in collection_documents]
        
        results: list[dict[str, Any]| None] = await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(
            "Completed ranking for batch",
            batch_id=batch_id,
            num_collections=len(collection_documents),
            results=results
        )

        #we have to update our collection with the final scores and the best article id for each collection
        bool_result = await self._update_bulk_collection_score(collection_documents=results, batch_id = batch_id)

        logger.info(
            "Completed the updation in the db for the batch",
            batch_id=batch_id,
            num_collections=len(collection_documents),
            update_success=bool_result
        )

        return bool_result

    async def _start_ranking_collection(self, collection_document: dict[str, Any], batch_id: str) -> None:
        """
        Here , in this function we will implement the ranking of the collection and the articles inside it.
        """

        async with self.semaphore:
            collection_id = collection_document.get("_id")
            article_ids = collection_document.get("article_ids")
            articles = collection_document.get("articles")

            if not articles:
                logger.info(f"No articles found for collection {collection_id}. Skipping ranking.")
                return None

            # Implement the ranking logic here

            N = len(articles)

            article_final_scores = []

            #we have to get into each articles and perform some clean up operations
            for article in articles:
                genunity_score = article.get("genunity_score", 0)
                ranking_depth_score = article.get("ranking_depth_score", 0)

                logger.info(
                    "Ranking article",
                    collection_id=collection_id,
                    article_id=article.get("_id"),
                    genunity_score=genunity_score,
                    ranking_depth_score=ranking_depth_score,
                    batch_id=batch_id
                )

                #now we have to find out the genunity factor

                t = (genunity_score - self.genunity_low_threshold) / (self.genunity_hihg_threshold - self.genunity_low_threshold) #we will get a t with in a various scale

                #we have to cap it into a unifies scale
                capped_t = max(0, min(1, t))  # Cap t to be within [0, 1]

                #next we have to handle the 0 case , for 0 we need to give a min value of 0.5 
                adjusted_t = 0.5 + 0.5 * capped_t  # Adjust t to be within [0.5, 1]

                logger.info(
                    "Adjusted genunity factor",
                    collection_id=collection_id,
                    article_id=article.get("_id"),
                    adjusted_genunity_factor=adjusted_t,
                    batch_id=batch_id
                )

                article_scoring = adjusted_t * ranking_depth_score #the final score of the article that which we are going to use
                article_final_scores.append(article_scoring)

            artcile_with_max_score = max(article_final_scores)
            #now we have to get the quality factor of the collection based on the final scores of the articles inside it
            quality_factor = 0.8 * artcile_with_max_score + 0.2 * (sum(article_final_scores) / N)  # Weighted average of max and mean scores
            #here 80% quality is defined by the max score of the articles and 20% is defined by the mean score of the articles


            #now we have to add the popularity factor to the final score of the collection so that to make ut complete
            popularity_factor = 1 + self.popularity_factor_weight * math.log10(N)  # Assuming each article contributes equally to the popularity

            #now we have to combine both together and have to update final collection score
            final_collection_score  = 0.55 * quality_factor + 0.45 * popularity_factor  # Weighted average of quality and popularity factors
            #55% of the final score is defined by the quality factor and 45% is defined by the popularity factor

            id_of_the_best_article_score = articles[article_final_scores.index(artcile_with_max_score)].get("_id")


            logger.info(
                "Completed the analysis and tweaked the final scores",
                collection_id=collection_id,
                article_id=article.get("_id"),
                adjusted_genunity_factor=adjusted_t,
                batch_id=batch_id
            )

            collection_analysis_report = {
                "_id" : collection_id,
                "quality_factor" : quality_factor, #overall quality of the collection
                "popularity_factor" : popularity_factor, #overall popularity of the collection
                "final_collection_score" : final_collection_score, #final mix of the quality and popularity
                "best_article_id" : id_of_the_best_article_score #the best article to show up
            }

            return collection_analysis_report


    async def _update_bulk_collection_score(self, collection_analysis_reports: list[dict[str, Any]], batch_id: str) -> None:
        """
        This function will update the collection with the final scores and the best article id for each collection
        """
        N = len(collection_analysis_reports)
        
        if not collection_analysis_reports:
            logger.info(
                "No collection analysis reports to update.",
                batch_id=batch_id
            )
            return

        bulk_operations = []
        for report in collection_analysis_reports:
            if report is None:
                continue  # Skip None reports

            bulk_operations.append(
                {
                    "update_one": {
                        "filter": {"_id": report["_id"]},
                        "update": {
                            "$set": {
                                "quality_factor": report["quality_factor"],
                                "popularity_factor": report["popularity_factor"],
                                "final_collection_score": report["final_collection_score"],
                                "best_article_id": ObjectId(report["best_article_id"]),
                            }
                        },
                    }
                }
            )

        try:
            # 1. Execute bulk write and capture the acknowledgment result object
            result = await self.collection.bulk_write(bulk_operations, ordered=False)
            
            # 2. Extract acknowledgment metrics from the result object
            matched = result.matched_count
            modified = result.modified_count  # if the coming data is already the value , mongodb will not perform the updatioin function
            
            logger.info(
                "Saved genunity scores to database",
                record_count=N,
                batch_id=batch_id,
                matched_count=matched,
                modified_count=modified,
            )

            #modified sometimes comes less becase may be if the updating value exists, the modified doesnt counts
            return matched == N

        except BulkWriteError as bwe:
            # 3. Handle partial failures if `ordered=False` encounters specific document errors
            details = bwe.details
            successful_modifications = details.get("nModified", 0)
            logger.warning(
                "Bulk write completed with errors",
                record_count=N,
                batch_id=batch_id,
                modified_count=successful_modifications,
                write_error_count=len(details.get("writeErrors", [])),
            )
            return successful_modifications == N

        except Exception as e:
            # 4. Handle catastrophic network or connection drops
            logger.error(
                "Unexpected database error during bulk write",
                record_count=N,
                batch_id=batch_id,
                error=str(e),
                exc_info=True,
            )
            return False
        
        
            