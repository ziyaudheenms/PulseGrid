"""
Through this module we are going to implement the global classification of the  data we have stored as ArticleMetadata
we have already generated the embedding of the articles that which we have stored in the db.

for the implementation we are going to use numpy and scipy libraries to implement the classification of the articles based on their embeddings.
The main challenge is of implementing the global classification of the articles based on their embeddings.

for that we are going to use the numpy dot operation btw the metrix build of the vectors of embeddings as rows with its transpose metrix
which will simultaneously give us the cosine similarity of the articles with each other and then we can use the scipy library to implement the clustering of the articles based on their cosine similarity.

using the scipy we use the graph method and finds out all the related nodes or articles by using the conncted_components method of the scipy library which will give us the clusters of the articles based on their cosine similarity.


"""
from datetime import datetime, timezone
import numpy as np
import structlog

from pymongo.asynchronous.database import AsyncDatabase
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from bson import ObjectId
from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()


class PulseClassify:
    def __init__(
        self, 
        db:AsyncDatabase    
    ):
        self.db = db
        self.collection = self.db["articleMetaData"]
        self.similarity_threshold = 0.8  # Define a threshold for cosine similarity to consider articles as similar


    async def add_to_db(self, clusters_map: dict[str, list[str]], category: str):
        """
        This method is used to update the status of the articles in the database based on their cluster classification.
        """

        cluster_grps = []
        articles_ids_to_update = []
        logger.info("Saving article classification clusters", category=category, cluster_count=len(clusters_map))

        for cluster_id, article_ids in clusters_map.items():

            #converting the article ids to ObjectId references for database operations
            object_id_refs = []
            for aid in article_ids:
                if isinstance(aid, ObjectId):
                    object_id_refs.append(aid)
                elif isinstance(aid, str) and ObjectId.is_valid(aid):
                    object_id_refs.append(ObjectId(aid))
                else:
                    logger.error("Invalid article ObjectId in classification cluster", category=category, cluster_id=cluster_id, article_id=aid)

            cluster_grps.append({
                "cluster_id": cluster_id,
                "category": category,
                "article_no": len(object_id_refs),
                "article_ids": object_id_refs,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })

            articles_ids_to_update.extend(object_id_refs)

        if cluster_grps:
            try:
                result = await self.collection.insert_many(cluster_grps)
                logger.info(
                    "Inserted article classification clusters",
                    category=category,
                    inserted_count=len(result.inserted_ids),
                )
            except Exception as exc:
                logger.error("Failed to insert article classification clusters", category=category, error=str(exc), exc_info=True)
                return

        if articles_ids_to_update:
            try:
                result = await self.collection.update_many(
                    {"_id": {"$in": articles_ids_to_update}},
                    {"$set": {"status": "Classified"}}
                )
                logger.info(
                    "Updated classified article status",
                    category=category,
                    matched_count=result.matched_count,
                    modified_count=result.modified_count,
                )
            except Exception as exc:
                logger.error("Failed to update classified article status", category=category, error=str(exc), exc_info=True)
                return


    async def classify_articles(self, embeddings: list, article_ids: list):
        """
            Now we have the embeddings and the article ids as of in correct order, what we need is just to perform the futher ops,
            error handling of if the embeddings are empty or the article ids are empty will be handled outside 
        """
        if not embeddings or not article_ids:
            logger.error("Cannot classify articles with empty embeddings or article IDs", embedding_count=len(embeddings), article_id_count=len(article_ids))
            return

        if len(embeddings) != len(article_ids):
            logger.error(
                "Embedding and article ID counts do not match",
                embedding_count=len(embeddings),
                article_id_count=len(article_ids),
            )
            return

        #convert all this embeddings to numpy array for the further operations
        try:
            embeddings_array = np.array(embeddings, dtype=np.float32)
        except (TypeError, ValueError) as exc:
            logger.error("Failed to convert article embeddings to NumPy array", error=str(exc), exc_info=True)
            return

        #now we have to perform the calculate the simularity globally for all the articles simultnaeously, for that we will use the dot product of the embeddings with its transpose to get the cosine similarity matrix

        similarity_matrix = np.dot(embeddings_array, embeddings_array.T)

        #convert them into True False for further cals

        adjacency_bool = similarity_matrix > self.similarity_threshold  #all less than the threshold will be false and all greater than the threshold will be true

        #now comes one of the  most important part of to compress the adjacency_bool by dropping out the False relations out

        adjacency_sparse_graph = csr_matrix(adjacency_bool)  #this function will convert that into 1D array of three layers that are related

        #we will feed this to the connected_components method of the scipy library to get the clusters of the articles based on their bool simelarity

        clusters, labels = connected_components(adjacency_sparse_graph, directed=False, return_labels=True)  #directed is false because we are not considering the direction of the similarity and return_labels is true because we want to get the labels of the clusters

        #now we have the no of clustors with the labels of the clusters

        clusters_map = {}
        for idx, cluster_id in enumerate(labels):
            if cluster_id not in clusters_map:
                clusters_map[cluster_id] = []
            clusters_map[cluster_id].append(article_ids[idx])

        #once we have the clustor map next comes of integrating it with our database so that to have a meaning.
        logger.info(
            "Article clustering completed",
            article_count=len(article_ids),
            cluster_count=len(clusters_map),
        )
        return clusters_map


    async def get_article_embeddings(self, category: str):
        """
        Fetches the embeddings of articles from the database based on the specified category.
        """
        #as of for this operation we just need the article ids and the embedding which we will use for further references.
        
        logger.info("Fetching article embeddings for classification", category=category)
        try:
            cursor = self.collection.find(
                {
                    "category": category,
                    "status" : {"$ne": "Classified"}  # Exclude already classified articles
                },
                {
                "_id": 1,        # MongoDB ObjectId reference
                "embedding": 1   # 1536-dim vector for linear algebra
                }
            )
        except Exception as exc:
            logger.error("Failed to query article embeddings", category=category, error=str(exc), exc_info=True)
            return

        embeddings = []
        article_ids = []
        #since async is written each document will be fetched one by one and we will append the embedding and the article id to the list of embeddings and article_ids  so that to save the memmory usage
        try:
            async for document in cursor:
                if "embedding" in document:
                    embeddings.append(document["embedding"])
                    article_ids.append(document["_id"])
        except Exception as exc:
            logger.error("Failed while reading article embeddings", category=category, error=str(exc), exc_info=True)
            return
        
        logger.info(
            "Fetched article embeddings for classification",
            category=category,
            article_count=len(article_ids),
        )
        return embeddings, article_ids