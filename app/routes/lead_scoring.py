from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.models.lead_scoring_model import (
    LeadEngagementRequest,
    LeadScoreResponse,
)
from app.services.llm_lead_scoring import (
    score_leads_llm,
)


router = APIRouter()


TARGET_INDUSTRIES = [
    "Healthcare",
    "Legal Services",
    "Logistics",
    "Manufacturing",
]


@router.post(
    "/score-leads",
    response_model=list[LeadScoreResponse],
    status_code=status.HTTP_200_OK,
)
def score_leads(
    request_data: list[LeadEngagementRequest],
) -> list[LeadScoreResponse]:

    try:
        # Convert Pydantic models
        # into normal Python dictionaries.
        engagement_data = [
            item.model_dump(
                mode="json"
            )
            for item in request_data
        ]

        results = score_leads_llm(
            engagement_data,
            target_industries=TARGET_INDUSTRIES,
        )

        return results

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Lead scoring failed: "
                f"{str(error)}"
            ),
        ) from error