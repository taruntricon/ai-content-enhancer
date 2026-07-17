from pymongo.errors import DuplicateKeyError

from app.database.mongodb import (
    post_analytics_collection,
)


def save_post_analytics(post_analytics: dict):

    post_analytics_collection.update_one(
        {
            "postId": post_analytics["postId"]
        },
        {
            "$set": post_analytics
        },
        upsert=True,
    )


def get_all_post_analytics():
    analytics = list(
        post_analytics_collection.find({}, {"_id": 0})
    )

    return analytics