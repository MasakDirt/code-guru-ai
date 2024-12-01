from fastapi import Depends, HTTPException

from code_guru.dependencies import get_code_review_service
from code_guru.exceptions import BaseAPIException
from code_guru.schemas import CodeReviewRequest, CodeReviewResponse
from code_guru.services import CodeReviewService


async def code_review_controller(
    code_review_request: CodeReviewRequest,
    review_service: CodeReviewService = Depends(get_code_review_service)
) -> CodeReviewResponse:
    try:
        return await review_service.review(code_review_request)
    except BaseAPIException as exception:
        raise HTTPException(
            status_code=exception.status_code,
            detail=exception.message
        )
