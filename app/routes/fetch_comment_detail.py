from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.models.post_model import (
    PostCommentsRequest,
)

from app.services.unipile_service import (
    fetch_post_comments,
)

router = APIRouter()


@router.post(
    "/fetch-post-comment",
    status_code=status.HTTP_200_OK,
)
def get_post_comments(
    request: PostCommentsRequest,
):

    try:

        comments = fetch_post_comments(
            request.postId
        )

        if comments is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unable to fetch comments."
            )

        return {
            "message": "Comments fetched successfully.",
            "data": comments,
        }

    except HTTPException:
        raise

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comments: {str(ex)}",
        )