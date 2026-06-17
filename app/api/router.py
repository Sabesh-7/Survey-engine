from fastapi import APIRouter

from app.api.routes import duplicates, generation, intent, recommendations

api_router = APIRouter()

api_router.include_router(intent.router, prefix="/analyze-intent", tags=["intent"])
api_router.include_router(recommendations.router, prefix="/recommend-questions", tags=["recommendations"])
api_router.include_router(duplicates.router, prefix="/detect-duplicates", tags=["duplicates"])
api_router.include_router(generation.router, prefix="/generate-missing-questions", tags=["generation"])
