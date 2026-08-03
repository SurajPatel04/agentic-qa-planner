from fastapi import APIRouter

from app.api.v1 import health, plans, test_cases, versions

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(plans.router, prefix="/plans", tags=["QA Plans"])
api_router.include_router(test_cases.router, prefix="/test-cases", tags=["Test Cases"])
# Versions routes are nested under /plans/{id}/versions, but the router itself can be prefixed with /plans
api_router.include_router(versions.router, prefix="/plans", tags=["Versions"])
