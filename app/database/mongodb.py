from pymongo import MongoClient

from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)

db = client["social_media_db"]

posts_collection = db["posts"]
engagements_collection = db["engagements"]
leads_collection = db["leads"]
post_analytics_collection = db["post_analytics"]

# post = {
#     "postId": "7482344406616842241",
#     "postText": "Excited to be exploring new ideas in tech and connecting with like-minded people here on LinkedIn.",
#     "platform": "LinkedIn"
# }

# posts_collection.insert_one(post)
