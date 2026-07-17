from app.database.mongodb import db
from fastapi import APIRouter

router = APIRouter()
@router.get("/test-mongodb")
def test_mongodb():

    db.command("ping")

    return {
        "message": "MongoDB Connected Successfully"
    }