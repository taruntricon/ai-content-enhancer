from app.database.mongodb import posts_collection


def save_post(post: dict):
    return posts_collection.insert_one(post)


def get_post(post_id: str):
    return posts_collection.find_one(
        {"postId": post_id}
    )

def get_all_posts():
    return list(posts_collection.find())


# def update_post(post_id: str, data: dict):
#     return posts_collection.update_one(
#         {"postId": post_id},
#         {"$set": data}
#     )