import logging
import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.graphs.workflow import build_qa_planner_graph
from app.models.acceptance_criteria import AcceptanceCriteria
from app.models.enums import PlanStatus, TestCategory, TestType
from app.models.execution_log import ExecutionLog
from app.models.qa_plan import QAPlan
from app.models.qa_plan_version import QAPlanVersion
from app.models.test_case import TestCase
from app.services.coverage_service import CoverageService
from app.services.duplicate_service import DuplicateService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class PlannerService:
    def __init__(self, db: AsyncSession, vector_service, qa_graph):
        self.db = db
        self.vector_service = vector_service
        self.graph = qa_graph

    async def generate_and_save_plan(
        self,
        title: str,
        user_story: str,
        acceptance_criteria: List[str],
        implementation_summary: str,
    ) -> uuid.UUID:
        """
        Orchestrates the AI workflow (LangGraph) and the deterministic
        business logic (Coverage, Duplicates) to generate a QA Plan.
        """
        logger.info(f"Generating AI QA plan for: {title}")

        # 1. Initialize LangGraph State
        state = {
            "user_story": user_story,
            # Pass ACs with explicit identifiers so the LLM can reference them cleanly
            "acceptance_criteria": [f"AC{idx+1}: {ac}" for idx, ac in enumerate(acceptance_criteria)],
            "implementation_summary": implementation_summary,
            "retrieved_docs": [],
            "user_flows": [],
            "test_cases": [],
            "assumptions": [],
            "risks": [],
            "errors": [],
            "execution_log": [],
        }

        # 2. Invoke AI Graph (Retrieve -> Analyze -> Generate -> Validate)
        final_state = await self.graph.ainvoke(state)
        
        generated_tests = final_state.get("test_cases", [])
        
        # 3. Deterministic Logic using standalone services
        coverage_summary = CoverageService.calculate_coverage(generated_tests, acceptance_criteria)
        is_duplicate_list = DuplicateService.detect_duplicates(generated_tests)
        is_incomplete_list = ValidationService.flag_incomplete_tests(generated_tests)

        # 4. Save to Database
        # Create QA Plan Parent
        qa_plan = QAPlan(
            title=title,
            requirement_or_user_story=user_story,
            implementation_summary=implementation_summary,
            assumptions=final_state.get("assumptions", []),
            status=PlanStatus.DRAFT,
            coverage_summary=coverage_summary,
            current_version=1,
        )
        self.db.add(qa_plan)
        await self.db.flush()

        # Create Acceptance Criteria Records
        ac_records = []
        for idx, ac_text in enumerate(acceptance_criteria, start=1):
            ac_record = AcceptanceCriteria(
                qa_plan_id=qa_plan.id,
                identifier=f"AC{idx}",
                text=ac_text,
            )
            ac_records.append(ac_record)
        self.db.add_all(ac_records)
        await self.db.flush()

        # Create Test Cases
        test_records = []
        for i, t in enumerate(generated_tests):
            is_dup = is_duplicate_list[i]
            is_inc = is_incomplete_list[i]
            
            # Safely map LLM enums to SQLAlchemy Enums
            try:
                t_type = TestType[t.test_type.upper().replace(" ", "_")]
            except KeyError:
                t_type = TestType.MANUAL
                
            try:
                t_cat = TestCategory[t.category.upper().replace(" ", "_")]
            except KeyError:
                t_cat = TestCategory.HAPPY_PATH

            # Build flag reason
            flag_reason = None
            if is_inc:
                flag_reason = "Test is missing actionable steps, rationale, or expected results."
            elif is_dup:
                flag_reason = "Test is very similar to another generated test."

            tc_record = TestCase(
                qa_plan_id=qa_plan.id,
                title=t.title,
                description=t.description,
                test_type=t_type,
                category=t_cat,
                acceptance_criteria_ids=t.covered_acceptance_criteria,
                rationale=t.rationale,
                steps=t.steps,
                expected_result=t.expected_result,
                is_duplicate=is_dup,
                is_incomplete=is_inc,
                flag_reason=flag_reason,
            )
            test_records.append(tc_record)
        
        self.db.add_all(test_records)
        
        # Create Version History Snapshot
        version_record = QAPlanVersion(
            qa_plan_id=qa_plan.id,
            version_number=1,
            change_summary="Initial AI-generated QA Plan",
            snapshot={
                "user_story": user_story,
                "acceptance_criteria": acceptance_criteria,
                "implementation_summary": implementation_summary,
                "assumptions": qa_plan.assumptions,
                "risks": final_state.get("risks", []),
                "coverage": coverage_summary,
                "test_cases": [t.model_dump() for t in generated_tests],
                "graph_errors": final_state.get("errors", [])
            },
        )
        self.db.add(version_record)
        
        # Save Execution Logs
        graph_logs = final_state.get("execution_log", [])
        log_records = []
        for log_entry in graph_logs:
            record = ExecutionLog(
                qa_plan_id=qa_plan.id,
                node=log_entry.get("node", "Unknown Node"),
                status=log_entry.get("status", "INFO"),
                message=log_entry.get("message", ""),
                details={
                    "execution_order": log_entry.get("execution_order"),
                    "sources": log_entry.get("sources", [])
                }
            )
            log_records.append(record)
            
        if log_records:
            self.db.add_all(log_records)
        
        await self.db.commit()
        return qa_plan.id
