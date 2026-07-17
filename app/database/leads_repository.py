from app.database.mongodb import leads_collection

def save_lead(lead: dict):

    result = leads_collection.insert_many(
        lead
    )

    return str(result.inserted_ids)