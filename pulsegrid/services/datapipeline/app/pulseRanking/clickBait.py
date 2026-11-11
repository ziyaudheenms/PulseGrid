import asyncio
import math
from collections.abc import Mapping, Sequence
from functools import partial
from typing import Any

import spacy
import structlog
from pymongo.asynchronous.database import AsyncDatabase
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

    async def analyze_all_categories(self) -> None:
        for category in SourceScope:
            await self.analyze_category(category.value)

    async def analyze_category(self, category: str) -> list[float | None]:
        cursor = self.collection.find({"category": category})
        articles = await cursor.to_list(length=None)

        if not articles:
            logger.info("No articles available for clickbait analysis", category=category)
            return []

        logger.info(
            "Analyzing all articles for category",
            category=category,
            article_count=len(articles),
        )
        return await asyncio.gather(
            *(self._analyze_article(article) for article in articles)
        )

    async def _analyze_article(self, article: Mapping[str, Any]) -> float | None:
        async with self.semaphore:
            title = article.get("title")
            body = article.get("body")

            if not isinstance(title, str) or not title.strip():
                logger.warning(
                    "Skipping clickbait analysis for article without a title",
                    article_id=article.get("_id"),
                )
                return None

            if not isinstance(body, str) or not body.strip():
                logger.warning(
                    "Skipping clickbait analysis for article without a body",
                    title=title,
                    article_id=article.get("_id"),
                )
                return None

            sentences = [
                sentence.text.strip()
                for sentence in self.nlp(body).sents
                if sentence.text.strip()
            ][:5]
            if not sentences:
                logger.warning(
                    "Skipping clickbait analysis because no sentences were extracted",
                    title=title,
                    article_id=article.get("_id"),
                )
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
                        article_id=article.get("_id"),
                        attempt=attempt,
                        max_retries=self.max_retries,
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(2 ** (attempt - 1))

            if vectors is None:
                logger.error(
                    "Unable to generate clickbait-analysis embeddings after retries",
                    title=title,
                    article_id=article.get("_id"),
                )
                return None

            similarities = [
                self._cosine_similarity(vectors[0], sentence_vector)
                for sentence_vector in vectors[1:]
            ]
            top_scores = sorted(similarities, reverse=True)[:2]
            genuinity_score = sum(top_scores) / len(top_scores)

            logger.info(
                "Article genuinity score",
                title=title,
                genuinity_score=genuinity_score,
                article_id=article.get("_id"),
            )
            return genuinity_score

    @staticmethod
    def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
        dot_product = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        denominator = left_norm * right_norm
        return dot_product / denominator if denominator else 0.0
