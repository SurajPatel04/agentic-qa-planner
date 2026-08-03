import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.models.qa_plan import QAPlan
from app.services.planner_service import PlannerService
from app.schemas.plan import (
    QAPlanResponse,
    QAPlanDetailResponse,
    GeneratePlanRequest,
)

router = APIRouter()


@router.post("", response_model=QAPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    payload: GeneratePlanRequest, 
    req: Request, 
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a new Agentic QA Plan and saves it to the database.
    """
    vector_service = req.app.state.vector_service
    qa_graph = req.app.state.qa_graph
    planner_service = PlannerService(db, vector_service, qa_graph)

    plan_id = await planner_service.generate_and_save_plan(
        title=payload.title,
        user_story=payload.user_story,
        acceptance_criteria=payload.acceptance_criteria,
        implementation_summary=payload.implementation_summary,
    )

    result = await db.execute(select(QAPlan).where(QAPlan.id == plan_id))
    plan = result.scalars().first()
    
    if not plan:
        raise HTTPException(status_code=500, detail="Failed to retrieve created QA Plan")

    return plan


@router.get("", response_model=List[QAPlanResponse], status_code=status.HTTP_200_OK)
async def list_plans(db: AsyncSession = Depends(get_db)):
    """
    List all QA Plans (lightweight representation).
    """
    result = await db.execute(select(QAPlan).order_by(QAPlan.created_at.desc()))
    plans = result.scalars().all()

    return plans


@router.get("/{plan_id}", response_model=QAPlanDetailResponse, status_code=status.HTTP_200_OK)
async def get_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a complete QA Plan by ID, eagerly loading all its relationships.
    """
    stmt = (
        select(QAPlan)
        .options(
            selectinload(QAPlan.acceptance_criteria),
            selectinload(QAPlan.test_cases),
            selectinload(QAPlan.execution_logs),
            selectinload(QAPlan.versions),
        )
        .where(QAPlan.id == plan_id)
    )
    result = await db.execute(stmt)
    plan = result.scalars().first()

    if not plan:
        raise HTTPException(status_code=404, detail="QA Plan not found")

    return plan


from app.schemas.plan import UpdatePlanRequest

@router.patch("/{plan_id}", response_model=QAPlanResponse, status_code=status.HTTP_200_OK)
async def update_plan_status(plan_id: uuid.UUID, payload: UpdatePlanRequest, db: AsyncSession = Depends(get_db)):
    """
    Update a QA Plan's overall status (e.g. APPROVED, REJECTED).
    """
    result = await db.execute(select(QAPlan).where(QAPlan.id == plan_id))
    plan = result.scalars().first()

    if not plan:
        raise HTTPException(status_code=404, detail="QA Plan not found")

    plan.status = payload.status.upper()
    await db.commit()
    await db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a QA Plan and all associated test cases, versions, and execution logs (cascading).
    """
    result = await db.execute(select(QAPlan).where(QAPlan.id == plan_id))
    plan = result.scalars().first()

    if not plan:
        raise HTTPException(status_code=404, detail="QA Plan not found")

    await db.delete(plan)
    await db.commit()
