import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.db import engine
from app.services.planner_service import PlannerService

AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)

async def main():
    print("Testing end-to-end AI QA Planner Graph Workflow...")
    
    # Mock Input Data
    title = "Authentication - Password Reset Flow"
    user_story = "As a user who forgot their password, I want to request a password reset link to my email so that I can regain access to my account."
    acs = [
        "User receives an email with a secure, one-time reset token.",
        "The reset token expires after 15 minutes.",
        "Attempting to use an expired or invalid token returns a clear error message.",
        "Password must meet complexity requirements (8 chars, 1 number, 1 special)."
    ]
    summary = "Added a new POST /api/v1/auth/forgot-password endpoint and a POST /api/v1/auth/reset-password endpoint. Uses SendGrid for emails."
    
    async with AsyncSessionLocal() as db:
        service = PlannerService(db)
        
        try:
            print("Invoking PlannerService...")
            plan_id = await service.generate_and_save_plan(
                title=title,
                user_story=user_story,
                acceptance_criteria=acs,
                implementation_summary=summary
            )
            print("="*50)
            print(f"✅ Successfully generated and saved QA Plan!\nPlan ID: {plan_id}")
            print("="*50)
        except Exception as e:
            print(f"❌ Failed during generation: {e}")
            raise e
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
