from fastapi import APIRouter

from app.api.matches import router as matches_router
from app.api.teams import router as teams_router
from app.api.knowledge import router as knowledge_router

api_router = APIRouter()

api_router.include_router(matches_router)
api_router.include_router(teams_router)
api_router.include_router(knowledge_router)