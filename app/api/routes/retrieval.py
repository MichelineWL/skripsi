from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.retrieval import (
    RetrievalRequest,
    RetrievalResponse,
)
from app.core.dependencies import get_retrieval_service
from app.core.exceptions import BusinessRuleError
from app.services.retrieval_service import RetrievalService


router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)


RetrievalServiceDep = Annotated[
    RetrievalService,
    Depends(get_retrieval_service),
]


@router.post(
    "/search",
    response_model=RetrievalResponse,
)
def search_knowledge(
    payload: RetrievalRequest,
    service: RetrievalServiceDep,
):
    try:
        return service.search(
            query=payload.query,
            organization_id=payload.organization_id,
            limit=payload.limit,
        )

    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc