import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.models.qa_plan import QAPlan
from app.models.qa_plan_version import QAPlanVersion
from app.schemas.version import QAPlanVersionResponse, CreateVersionRequest
from typing import List

router = APIRouter()


@router.post("/{plan_id}/versions", response_model=QAPlanVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    plan_id: uuid.UUID,
    request: CreateVersionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Snapshots the current QA Plan state and creates a new version.
    """
    stmt = (
        select(QAPlan)
        .options(
            selectinload(QAPlan.test_cases),
            selectinload(QAPlan.acceptance_criteria)
        )
        .where(QAPlan.id == plan_id)
    )
    result = await db.execute(stmt)
    qa_plan = result.scalars().first()

    if not qa_plan:
        raise HTTPException(status_code=404, detail="QA Plan not found")

    # Increment Version
    new_version_number = qa_plan.current_version + 1
    qa_plan.current_version = new_version_number

    # Snapshot test cases (serialize to dict)
    test_cases_snapshot = []
    for tc in qa_plan.test_cases:
        tc_dict = {
            "title": tc.title,
            "description": tc.description,
            "test_type": tc.test_type.value,
            "category": tc.category.value,
            "status": tc.status.value,
            "priority": tc.priority.value,
            "rationale": tc.rationale,
            "steps": tc.steps,
            "expected_result": tc.expected_result,
        }
        test_cases_snapshot.append(tc_dict)

    snapshot = {
        "user_story": qa_plan.requirement_or_user_story,
        "acceptance_criteria": [ac.text for ac in qa_plan.acceptance_criteria],
        "implementation_summary": qa_plan.implementation_summary,
        "assumptions": qa_plan.assumptions,
        "coverage": qa_plan.coverage_summary,
        "test_cases": test_cases_snapshot,
    }

    version_record = QAPlanVersion(
        qa_plan_id=qa_plan.id,
        version_number=new_version_number,
        change_summary=request.change_summary,
        snapshot=snapshot,
    )
    
    db.add(version_record)
    await db.commit()
    await db.refresh(version_record)

    return version_record


@router.get("/{plan_id}/versions", response_model=List[QAPlanVersionResponse], status_code=status.HTTP_200_OK)
async def list_versions(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    List all versions of a specific QA Plan.
    """
    result = await db.execute(
        select(QAPlanVersion)
        .where(QAPlanVersion.qa_plan_id == plan_id)
        .order_by(QAPlanVersion.version_number.desc())
    )
    versions = result.scalars().all()

    return versions

@router.get("/{plan_id}/versions/{version_number}", response_model=QAPlanVersionResponse, status_code=status.HTTP_200_OK)
async def get_specific_version(plan_id: uuid.UUID, version_number: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific version snapshot of a QA Plan.
    """
    result = await db.execute(
        select(QAPlanVersion)
        .where(
            QAPlanVersion.qa_plan_id == plan_id,
            QAPlanVersion.version_number == version_number
        )
    )
    version_record = result.scalars().first()

    if not version_record:
        raise HTTPException(status_code=404, detail="Version not found")

    return version_record
