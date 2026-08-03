from typing import List

from app.graphs.schema import TestCaseSchema


class ValidationService:
    """Handles deterministic validation of test completeness before DB insertion."""

    @staticmethod
    def flag_incomplete_tests(tests: List[TestCaseSchema]) -> List[bool]:
        """
        Returns a list of booleans indicating if a test at the corresponding index
        is considered incomplete.
        
        A test is incomplete if:
        - It lacks actionable steps
        - It lacks a meaningful expected result
        - It lacks a meaningful rationale
        """
        is_incomplete_list = [False] * len(tests)

        for i, test in enumerate(tests):
            if not test.steps or len(test.steps) == 0:
                is_incomplete_list[i] = True
            elif not test.expected_result or len(test.expected_result.strip()) < 5:
                is_incomplete_list[i] = True
            elif not test.rationale or len(test.rationale.strip()) < 5:
                is_incomplete_list[i] = True

        return is_incomplete_list
