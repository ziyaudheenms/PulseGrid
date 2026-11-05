from pymongo import MongoClient

# Initialize synchronous PyMongo client
client = MongoClient("localhost", 27017)
db = client["pulseGrid"]

# Fetch all clusters, sorted by article_no descending (largest clusters first)
clusters = db["articleCollection"].find().sort("article_no", -1)

total_clusters = db["articleCollection"].count_documents({})
print(f"Total Clusters Found: {total_clusters}\n")

for cluster in clusters:
    count = cluster.get('article_no', len(cluster.get('article_ids', [])))
    print(f"=== Cluster ID: {cluster['cluster_id']} (Total Articles: {count}) ===")
    
    for aid in cluster["article_ids"]:
        article = db["articleMetaData"].find_one({"_id": aid})
        if article:
            print(f"  • {article.get('title', 'No Title Found')}")
    print("-" * 50)