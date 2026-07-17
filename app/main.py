from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.content import router as content_router
from app.routes.lead_scoring import router as lead_scoring_router
from app.routes.publish_post import router as post_router
from app.routes.fetch_post_detail import router as post_detail_router
from app.routes.fetch_comment_detail import router as comment_detail_router
from app.routes.mongodb import router as mongodb_router
from app.routes.post_analytics import router as post_analytics_router

from app.scheduler.scheduler import (
    start_scheduler,
    stop_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting...")

    start_scheduler()

    yield

    print("Application shutting down...")

    stop_scheduler()


app = FastAPI(
    lifespan=lifespan
)

origins = [
    "https://social-media-manager-frontend-enmpr9drl-apex-tricon.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content_router)
app.include_router(lead_scoring_router)
app.include_router(post_router)
app.include_router(post_detail_router)
app.include_router(comment_detail_router)
app.include_router(mongodb_router)
app.include_router(post_analytics_router)

@app.get("/")
def health():
    return {
        "status": "UP"
    }
