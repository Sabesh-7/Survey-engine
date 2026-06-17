from fastapi import APIRouter, Depends

from app.core.dependencies import get_intent_analyzer
from app.schemas.intent import IntentRequest, IntentResponse
from app.services.intent_analyzer import IntentAnalyzerService

router = APIRouter()


@router.post("", response_model=IntentResponse)
async def analyze_intent(
    payload: IntentRequest,
    service: IntentAnalyzerService = Depends(get_intent_analyzer),
) -> IntentResponse:
    return await service.analyze(payload)
