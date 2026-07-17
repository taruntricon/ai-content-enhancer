from pydantic import BaseModel


class PublishPostRequest(BaseModel):
    text: str

class PostDetailsRequest(BaseModel):
    postId: str

class PostCommentsRequest(BaseModel):
    postId: str
