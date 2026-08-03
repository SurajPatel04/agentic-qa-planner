from typing import Any, Dict

from app.graphs.state import QAState


def validate_tests(state: QAState) -> Dict[str, Any]:
    """
    Node 4: AI Output Validation
    
    Scans the generated test cases for missing required fields (rationale, steps, expected_result).
    Appends any found issues to the state's `errors` list. This can be used in the future
    to trigger a reflection loop, but for now it just logs them into the graph state.
    """
    tests = state.get("test_cases", [])
    errors = []

    for test in tests:
        if not test.rationale or len(test.rationale.strip()) < 5:
            errors.append(f"Test '{test.title}' is missing a clear rationale.")
        if not test.steps or len(test.steps) == 0:
            errors.append(f"Test '{test.title}' is missing actionable steps.")
        if not test.expected_result or len(test.expected_result.strip()) < 5:
            errors.append(f"Test '{test.title}' is missing an expected result.")

    log_entry = {
        "execution_order": 4,
        "node": "Validate Tests",
        "status": "Success" if not errors else "Issues Found",
        "message": f"Found {len(errors)} validation issues."
    }

    return {
        "errors": errors,
        "execution_log": [log_entry]
    }
