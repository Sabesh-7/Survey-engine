from fastapi import APIRouter, Depends

from app.core.dependencies import get_duplicate_detector
from app.schemas.duplicates import DuplicateDetectionRequest, DuplicateDetectionResponse
from app.services.duplicate_detection import DuplicateDetectionService

router = APIRouter()


@router.post("", response_model=DuplicateDetectionResponse)
async def detect_duplicates(
    payload: DuplicateDetectionRequest,
    service: DuplicateDetectionService = Depends(get_duplicate_detector),
) -> DuplicateDetectionResponse:
    return await service.detect(payload)
