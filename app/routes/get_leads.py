from fastapi import APIRouter

from app.database.leads_repository import get_all_leads

router = APIRouter()


@router.get("/get-leads")
def get_all_leads_route():
    return get_all_leads()
