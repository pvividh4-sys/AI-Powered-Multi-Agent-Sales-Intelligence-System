
"""
Negative test for cleaning execution and validation.

A numeric conversion is deliberately requested for a
non-existent column. The test verifies that the failure
is logged and the validation gate does not pass silently.
"""

import pandas as pd

from cleaning.execution import CleaningExecutionEngine
from cleaning.validation import CleaningValidationEngine


def main():
    print("=" * 65)
    print("CLEANING FAILURE-HANDLING TEST")
    print("=" * 65)

    original_df = pd.DataFrame({
        "Transaction_ID": [101, 102, 103],
        "Sales": [100.0, 200.0, 300.0],
    })

    # Deliberately invalid: Missing_Column does not exist.
    invalid_decision = {
        "issue_id": "TEST_INVALID_COLUMN",
        "issue_type": "numeric_conversion",
        "column": "Missing_Column",
        "requires_approval": True,
        "user_decision": "APPROVE",
        "execution_strategy": "median",
    }

    engine = CleaningExecutionEngine(original_df)

    cleaned_df = engine.execute_decisions(
        [invalid_decision]
    )
    logs = engine.get_execution_logs()

    print("\nExecution log:")
    for log in logs:
        print(log)

    # 1. The invalid operation must be logged as failed.
    assert len(logs) == 1, (
        "Expected one execution log."
    )

    assert logs[0]["status"] == "failed", (
        "The invalid operation was not logged as failed."
    )

    # 2. The original data must remain unchanged.
    pd.testing.assert_frame_equal(
        cleaned_df,
        original_df,
    )

    print("\nInvalid operation correctly rejected — PASSED")
    print("Dataset preserved — PASSED")

    # 3. Run the cleaning validation gate.
    validator = CleaningValidationEngine(
        original_df=original_df,
        cleaned_df=cleaned_df,
        execution_logs=logs,
        semantic_mapping={},
    )

    validation = validator.validate_all()

    print("\nValidation result:")
    print(validation)

    # A failed execution must not be reported as a clean pass.
    assert validation.get("overall_status") != "PASSED", (
        "FAILURE: Validation passed despite a failed execution."
    )

    execution_check = next(
        (
            check
            for check in validation.get("checks", [])
            if check.get("check_name") == "execution_logs"
        ),
        None,
    )

    assert execution_check is not None, (
        "The execution_logs validation check was not found."
    )

    assert execution_check.get("status") != "PASSED", (
        "The execution_logs check passed despite a failed operation."
    )

    print("\nValidation gate rejected failed execution — PASSED")

    print("\n" + "=" * 65)
    print("CLEANING FAILURE-HANDLING TEST: PASSED")
    print("=" * 65)


if __name__ == "__main__":
    main()
