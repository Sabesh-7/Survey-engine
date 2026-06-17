from fastapi import APIRouter, Depends

from app.core.dependencies import get_question_generator
from app.schemas.generation import GenerationRequest, GenerationResponse
from app.services.question_generation import QuestionGenerationService

router = APIRouter()


@router.post("", response_model=GenerationResponse)
async def generate_missing_questions(
    payload: GenerationRequest,
    service: QuestionGenerationService = Depends(get_question_generator),
) -> GenerationResponse:
    return await service.generate(payload)
