from difflib import SequenceMatcher
from typing import List

from app.graphs.schema import TestCaseSchema


class DuplicateService:
    """Handles deterministic detection of duplicate test cases."""

    @staticmethod
    def _calculate_similarity(a: str, b: str) -> float:
        """Calculates a simple string similarity ratio between 0 and 1."""
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def detect_duplicates(tests: List[TestCaseSchema]) -> List[bool]:
        """
        Returns a list of booleans indicating if a test at the corresponding index
        is considered a duplicate of an earlier test.
        
        Detection relies on matching `test_type`, `category`, and high title similarity.
        """
        is_duplicate_list = [False] * len(tests)

        for i in range(len(tests)):
            if is_duplicate_list[i]:
                continue  # Already flagged

            for j in range(i + 1, len(tests)):
                if is_duplicate_list[j]:
                    continue

                t1 = tests[i]
                t2 = tests[j]

                # Check if they fall in the same functional bucket
                if (
                    t1.test_type.upper() == t2.test_type.upper()
                    and t1.category.upper() == t2.category.upper()
                ):
                    sim = DuplicateService._calculate_similarity(t1.title, t2.title)
                    if sim > 0.85:
                        is_duplicate_list[j] = True

        return is_duplicate_list
