from fastapi import APIRouter, HTTPException

from app.models.post_model import PublishPostRequest

from app.services.unipile_service import publish_post

from app.utils.file_utils import write_json_file
from app.database.post_repository import save_post


router = APIRouter()


@router.post("/publish-post")
def publish_linkedin_post(request: PublishPostRequest):

    try:

        response = publish_post(request.text)

        post_data = {
            "postId": response.get("post_id"),
            "postText": request.text,
            "platform": "LinkedIn",
        }

        save_post(post_data)

        write_json_file(
            post_data,
            "app/models/post_data.json",
        )

        return {
            "message": "Post published successfully.",
            "data": post_data,
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )