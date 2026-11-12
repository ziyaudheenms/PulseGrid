from typing import Any
import structlog
from bullmq import Job

from pulseClean.embedEngine import PulseCleanEmbedd
from pulseClean.pulseClassify import  PulseClassify
from pulseRanking.clickBait import PulseBaitAnalysis

from core.database import get_database
from core.config import settings
from core.logging import setup_logging
from schema.source_schema import SourceScope
setup_logging()
logger = structlog.get_logger()

async def implement_embedding_handler(job:Job):
    logger.info(f"Got a task, looking for the function suitable to execute this. Job name: {job.name}")
    db = await get_database()

    try:

        #Initiallzing our embedd bot for initializing the embedding
        pulseclean = PulseCleanEmbedd(
            db = db,
            concurrency_limit=5,
            max_retries=3,
            transformer_model='sentence-transformers/all-mpnet-base-v2'
        )

        #all the required batching , processing asyn, controlling the simultaneous async threads all are controlled by the PulseCleanClass itself
        #we just have to initiate push for the batching process
        logger.info("Starting the embedding process for the articles in the database")
        await pulseclean.fetch_article_batch(batch_size=50)
    finally:
        #once all the process completed either successfull or failure cleanig up the openened connections
        # await db.client.close()
        pass


async def implement_classification_handler(job:Job):

    db = await get_database()

    try:
        #Initiallzing our crawler bot for crawling
        pulseclean = PulseClassify(
            db = db,
            threshold=0.6
        )

        # Iterate over enum members, then use their database value rather than the enum name.
        for category in SourceScope:
            category_name = category.value
            embeddings, article_ids = await pulseclean.get_article_embeddings(category=category_name)

            if not embeddings or not article_ids:
                logger.info("No articles available for classification", category=category_name)
                continue

            clusters_map: dict[str, list[str]] = await pulseclean.classify_articles(
                embeddings=embeddings,
                article_ids=article_ids,
            )
            if not clusters_map:
                continue

            await pulseclean.add_to_db(clusters_map=clusters_map, category=category_name)

    finally:
        #once all the process completed either successfull or failure cleanig up the openened connections
        # await db.client.close()
        pass


async def implement_clickbait_handler(job: Job):
    logger.info("Starting clickbait analysis", job_name=job.name)
    db = await get_database()

    analyzer = PulseBaitAnalysis(
        db=db,
        concurrency_limit=3,
        max_retries=3,
        transformer_model="sentence-transformers/all-mpnet-base-v2",
    )
    await analyzer.initiate_analysis()


# async def implement_mattr_scoring(job: Job):
#     logger.info("Starting mattr analysis scoring", job_name=job.name)
#     db = await get_database()

#     for category in SourceScope:
#         category_name = category.value
#         embeddings, article_ids = await pulseclean.get_article_embeddings(category=category_name)

#         if not embeddings or not article_ids:
#             logger.info("No articles available for classification", category=category_name)
#             continue

#         clusters_map: dict[str, list[str]] = await pulseclean.classify_articles(
#             embeddings=embeddings,
#             article_ids=article_ids,
#         )
#         if not clusters_map:
#             continue

#         await pulseclean.add_to_db(clusters_map=clusters_map, category=category_name)