from pydantic import BaseModel, Field
from typing import Optional

class DraftMessageRequest(BaseModel):
    lead_name: str = Field(..., description="Name of the lead")
    lead_message: Optional[str] = Field("", description="Comment or message posted by the lead")
    post_text: Optional[str] = Field("", description="Context of the original post")
    intent: Optional[str] = Field("HIGH", description="Lead intent tier (HIGH, MEDIUM, LOW)")
    reasoning: Optional[str] = Field("", description="Reasoning from lead scoring")
    channel: str = Field("email", description="Outreach channel: email or message")
    variation: Optional[int] = Field(1, description="Variation index for regeneration (1, 2, 3...)")

class DraftMessageResponse(BaseModel):
    subject: Optional[str] = Field(None, description="Email subject line if applicable")
    body: str = Field(..., description="Generated email/message body")
    channel: str = Field(..., description="Channel used")
    variation: int = Field(1, description="Variation index generated")
