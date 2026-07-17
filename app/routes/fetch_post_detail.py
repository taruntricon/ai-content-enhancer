from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.models.post_model import (
    PostDetailsRequest,
)

from app.services.unipile_service import (
    fetch_post_details,
)

router = APIRouter()


@router.post(
    "/fetch-post-detail",
    status_code=status.HTTP_200_OK,
)
def get_post_details(
    request: PostDetailsRequest,
):

    post = fetch_post_details(
        request.postId
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Unable to fetch post details."
        )

    return {
        "message": "Post details fetched successfully.",
        "data": post,
    }