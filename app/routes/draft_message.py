from fastapi import APIRouter, HTTPException, status
from app.models.draft_message_model import DraftMessageRequest, DraftMessageResponse
from app.services.content_service import generate_outreach_draft

router = APIRouter()

@router.post(
    "/draft-message",
    response_model=DraftMessageResponse,
    status_code=status.HTTP_200_OK,
)
def draft_message(request: DraftMessageRequest):
    try:
        result = generate_outreach_draft(
            lead_name=request.lead_name,
            lead_message=request.lead_message or "",
            post_text=request.post_text or "",
            intent=request.intent or "HIGH",
            reasoning=request.reasoning or "",
            channel=request.channel,
            variation=request.variation or 1,
        )
        return DraftMessageResponse(
            subject=result.get("subject"),
            body=result["body"],
            channel=result["channel"],
            variation=result["variation"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Outreach drafting failed: {str(e)}"
        ) from e
