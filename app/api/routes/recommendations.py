from fastapi import APIRouter, Depends

from app.core.dependencies import get_question_retrieval
from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.services.retrieval_service import QuestionRetrievalService

router = APIRouter()


@router.post("", response_model=RecommendationResponse)
async def recommend_questions(
    payload: RecommendationRequest,
    service: QuestionRetrievalService = Depends(get_question_retrieval),
) -> RecommendationResponse:
    return await service.recommend(payload)
