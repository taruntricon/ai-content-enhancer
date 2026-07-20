from app.database.mongodb import leads_collection

def save_lead(lead: dict):

    result = leads_collection.insert_many(
        lead
    )

    return str(result.inserted_ids)


def get_all_leads():
    leads = list(
        leads_collection.find({}, {"_id": 0})
    )

    return leads
