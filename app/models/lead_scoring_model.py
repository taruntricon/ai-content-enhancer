from datetime import datetime

from pydantic import BaseModel
from typing import Any

class Actor(BaseModel):
    name: str | None = None
    designation: str | None = None
    company: str | None = None
    industry: str | None = None
    followers: int | None = None
    profileUrl: str | None = None
    previousInteractions: int = 0


class LeadEngagementRequest(BaseModel):
    engagementId: str
    platform: str
    postId: str
    postText: str | None = None
    action: str
    message: str | None = None
    actor: Actor
    timestamp: datetime


class LeadScoreResponse(BaseModel):
    postText: str | None = None
    intent: str
    # confidence: str
    name: str
    # industry: str | None = None
    reasoning: str
    # scores: dict[str, Any]
    total_score: int
    message: str | None = None
