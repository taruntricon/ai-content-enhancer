from app.database.mongodb import engagements_collection

def save_engagement(engagement: dict):

    result = engagements_collection.insert_one(
        engagement
    )

    return str(result.inserted_id)
