import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.enums import TestPriority, TestStatus
from app.models.test_case import TestCase
from app.schemas.test_case import TestCaseResponse, UpdateTestCaseRequest

router = APIRouter()


@router.patch("/{test_case_id}", response_model=TestCaseResponse, status_code=status.HTTP_200_OK)
async def update_test_case(
    test_case_id: uuid.UUID,
    request: UpdateTestCaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific test case (e.g., to edit content, approve, reject, or reprioritize).
    """
    result = await db.execute(select(TestCase).where(TestCase.id == test_case_id))
    test_case = result.scalars().first()

    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    if request.title is not None:
        test_case.title = request.title
    if request.description is not None:
        test_case.description = request.description
    if request.steps is not None:
        test_case.steps = request.steps
    if request.expected_result is not None:
        test_case.expected_result = request.expected_result
    if request.rationale is not None:
        test_case.rationale = request.rationale

    if request.status is not None:
        try:
            test_case.status = TestStatus[request.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400, detail=f"Invalid status: {request.status}"
            )

    if request.priority is not None:
        try:
            test_case.priority = TestPriority[request.priority.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400, detail=f"Invalid priority: {request.priority}"
            )

    await db.commit()
    await db.refresh(test_case)

    return test_case
