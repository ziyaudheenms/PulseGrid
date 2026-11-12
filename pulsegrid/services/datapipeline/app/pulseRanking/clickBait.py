import asyncio
import math
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from functools import partial
from typing import Any

import spacy
import structlog
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from sentence_transformers import SentenceTransformer

from core.logging import setup_logging
from schema.source_schema import SourceScope

setup_logging()
logger = structlog.get_logger()


class PulseBaitAnalysis:
    def __init__(
        self,
        db: AsyncDatabase,
        concurrency_limit: int = 3,
        max_retries: int = 3,
        transformer_model: str = "sentence-transformers/all-mpnet-base-v2",
        batch_size: int = 50
    ) -> None:
        if concurrency_limit < 1:
            raise ValueError("concurrency_limit must be greater than zero")
        if max_retries < 1:
            raise ValueError("max_retries must be greater than zero")

        self.collection = db["articleMetaData"]
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.max_retries = max_retries
        self.transformer = SentenceTransformer(transformer_model)
        self.nlp = spacy.load("en_core_web_sm")
        self.batch_size = batch_size
    
    async def initiate_analysis(self):
        """
            Since this operation is performed with all the documents in the DB , we have to fetch all off them, but directly calling
            them is a bad idea and drops performance

            Lets implement the batch based updation of the articles using the last seen id using the while loop as long as we get the documents from the db

        """

        last_seen_id = None
        bool_result_batches = []
        
        while True:
            #the baseline query that will be used
            query: dict[str, Any] = {
                # "status": {"$ne": "BAITSCORE"}
            }

            if last_seen_id:
                query["_id"] = {"$gt": last_seen_id}

            #projections includes the fields that is to be fetched for the matching records --> only specified fields will be fetcheddd
            projection = {
                "title": 1,
                "body": 1,  # or "content" depending on your schema field name
            }

            cursor = (
                self.collection.find(query, projection)
                .sort("_id", 1)
                .limit(self.batch_size)
            )

            #here we dont need to implement the pydantic serialization, that causes high compute resources
            batch_articles: list[dict[str, Any]] = []

            async for doc in cursor:
                doc_id = str(doc.get("_id"))
                title = doc.get("title", "")
                text = doc.get("body") or doc.get("text", "")

                if text and text.strip():
                        #storing the data as onjects 
                    batch_articles.append({
                        "doc_id": doc_id,
                        "title": title,
                        "body": text
                    })   


            
            if not batch_articles:
                break #this helps to stop the loop when no more documents is presnt

            batch_no = str(last_seen_id) if last_seen_id else 'initial batch'
            bool_result = await self._initiate_analysis(batch_articles, batch_no)
            logger.info('here the results are ', result = bool_result)
            bool_result_batches.append(bool_result)

            last_seen_id = ObjectId(batch_articles[-1]["doc_id"])#updating the last seen id so that the last doc's id of the loop will be stored there.

            await asyncio.sleep(0.05)  #a pause btw each batch fetching



        if False in bool_result_batches:
            logger.info(
                "All batches havent compltly processed genunity score",
                results = bool_result_batches
            )
        else:
            logger.info(
                "All batches successfully passed genunity score",
                results = bool_result_batches
            )
            
        return

  
    async def bulk_updation_db(self, data_to_update: list[dict[str, Any]| None]) -> bool:
        """
        We will implement the bulk updation of the records
        """

        operations = []
        data_count = len(data_to_update)

        if data_count == 0:
            return True

        for data in data_to_update:
            if not data:
                data_count -= 1
                continue  #we can contain null cases where the genuntiy scoring is not able to implement , so we are avoidgn them
            
            doc_id = data["doc_id"]
            operations.append(
                UpdateOne(
                    {"_id": ObjectId(doc_id)},
                    {
                        "$set": {
                            "genunity_score": data["genunity_score"],
                            "status": "BAITSCORE"  # status will be updated to implement MATTR
                        }
                    }
                )
            )

        try:
            # 1. Execute bulk write and capture the acknowledgment result object
            result = await self.collection.bulk_write(operations, ordered=False)
            
            # 2. Extract acknowledgment metrics from the result object
            matched = result.matched_count
            modified = result.modified_count  # if the coming data is already the value , mongodb will not perform the updatioin function
            
            logger.info(
                "Saved genunity scores to database",
                record_count=data_count,
                matched_count=matched,
                modified_count=modified,
            )

            #modified sometimes comes less becase may be if the updating value exists, the modified doesnt counts
            return matched == data_count

        except BulkWriteError as bwe:
            # 3. Handle partial failures if `ordered=False` encounters specific document errors
            details = bwe.details
            successful_modifications = details.get("nModified", 0)
            logger.warning(
                "Bulk write completed with errors",
                record_count=data_count,
                modified_count=successful_modifications,
                write_error_count=len(details.get("writeErrors", [])),
            )
            return successful_modifications == data_count

        except Exception as e:
            # 4. Handle catastrophic network or connection drops
            logger.error(
                "Unexpected database error during bulk write",
                record_count=data_count,
                error=str(e),
                exc_info=True,
            )
            return False


    async def _initiate_analysis(self, articles:list[dict[str, Any]], batch_id: str):
        """
        Here using the asyncio.gather we will fire the articles of the batch which will be handled by the semaphore 
        
        """

        if not articles:
            logger.info("No articles available for clickbait analysis", batch_id=batch_id)

        results_to_update_db = []
        #generating the task and shooting up with asyncio
        tasks = [self._analyze_article(article) for article in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(
            "Completed the genunity scoring of current batch",
            batch_id = batch_id,
            batch_size = len(articles)
        )
        #we will forward the request to implement the bulk update of the genunity scores
        bool_result = await self.bulk_updation_db(results)  #if all the valid articles are updated with the genunity score we will get true or false will be returned
        logger.info(
            "Completed the DB updation of current batch",
            batch_id = batch_id,
            batch_size = len(articles)
        )
        return bool_result

    async def _analyze_article(self, article: dict[str, Any]) -> dict[str, Any] | None:
        async with self.semaphore:
            title = article.get("title")
            body = article.get("body")

            if not isinstance(title, str) or not title.strip():
                logger.warning(
                    "Skipping clickbait analysis for article without a title",
                    article_id=article.get("doc_id"),
                )
                return None

            if not isinstance(body, str) or not body.strip():
                logger.warning(
                    "Skipping clickbait analysis for article without a body",
                    title=title,
                    article_id=article.get("doc_id"),
                )
                return None

            sentences = [
                sentence.text.strip()
                for sentence in self.nlp(body).sents   #using the npl.sents inorder to get the no of sentenses in the givrn article.
                if sentence.text.strip()
            ][:5]
            if not sentences:
                logger.warning(
                    "Skipping clickbait analysis because no sentences were extracted",
                    title=title,
                    article_id=article.get("doc_id"),
                )
                return None

            article_id = article.get("doc_id")
            if article_id is None:
                logger.error("Cannot save genuinity score for article without an ID", title=title)
                return None

            loop = asyncio.get_running_loop()
            vectors: list[list[float]] | None = None
            texts = [title.strip(), *sentences]
            for attempt in range(1, self.max_retries + 1):
                try:
                    encoded = await loop.run_in_executor(
                        None,
                        partial(
                            self.transformer.encode,
                            texts,
                            convert_to_numpy=True,
                            show_progress_bar=False,
                        ),
                    )
                    vectors = encoded.tolist()
                    break
                except Exception:
                    logger.exception(
                        "Failed to generate clickbait-analysis embeddings",
                        title=title,
                        article_id=article.get("doc_id"),
                        attempt=attempt,
                        max_retries=self.max_retries,
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(2 ** (attempt - 1))

            if vectors is None:
                logger.error(
                    "Unable to generate clickbait-analysis embeddings after retries",
                    title=title,
                    article_id=article.get("doc_id"),
                )
                return None

            similarities = [
                self._cosine_similarity(vectors[0], sentence_vector)
                for sentence_vector in vectors[1:]
            ]
            top_scores = sorted(similarities, reverse=True)[:2]
            genunity_score = sum(top_scores) / len(top_scores)

            logger.info(
                "Article genuinity score",
                title=title,
                genunity_score=genunity_score,
                article_id=article_id,
            )

            genunity_result = {
                "doc_id": article_id,
                "genunity_score": genunity_score
            }
            return genunity_result






    @staticmethod
    def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
        dot_product = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        denominator = left_norm * right_norm
        return dot_product / denominator if denominator else 0.0
