from typing import Any, Dict, List

from app.graphs.schema import TestCaseSchema


class CoverageService:
    """Handles deterministic calculation of test coverage against Acceptance Criteria."""

    @staticmethod
    def calculate_coverage(
        generated_tests: List[TestCaseSchema], acceptance_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates coverage by strictly intersecting LLM-provided AC IDs with valid AC IDs.
        """
        total_ac = len(acceptance_criteria)
        # Assuming ACs are passed as simple strings and we assign AC1, AC2, etc.
        valid_ac_ids = {f"AC{idx+1}" for idx in range(total_ac)}

        covered_acs = set()

        for test in generated_tests:
            for covered_id in test.covered_acceptance_criteria:
                clean_id = covered_id.strip().upper()
                # Only count it if it actually exists in our valid set
                if clean_id in valid_ac_ids:
                    covered_acs.add(clean_id)

        covered_count = len(covered_acs)
        coverage_percentage = (covered_count / total_ac * 100) if total_ac > 0 else 100.0

        uncovered_criteria = [
            ac_id for ac_id in sorted(list(valid_ac_ids)) if ac_id not in covered_acs
        ]

        return {
            "total_criteria_count": total_ac,
            "covered_criteria_count": covered_count,
            "coverage_percentage": round(coverage_percentage, 2),
            "uncovered_criteria": uncovered_criteria,
        }
