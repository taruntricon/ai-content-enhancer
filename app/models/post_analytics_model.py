from pydantic import BaseModel


class Analytics(BaseModel):
    impressions: int
    members_reached: int
    profile_viewers: int
    followers_gained: int
    reactions: int
    comments: int
    reposts: int


class PostAnalyticsResponse(BaseModel):
    postId: str
    analytics: Analytics