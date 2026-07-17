from fastapi import APIRouter

from app.database.post_analytics_repository import get_all_post_analytics

router = APIRouter()


@router.get("/post-analytics")
def get_post_analytics():
    return get_all_post_analytics()