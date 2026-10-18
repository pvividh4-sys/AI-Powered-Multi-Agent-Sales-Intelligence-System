
"""
Test an explicitly approved data-cleaning operation.

Scenario:
- One missing categorical value exists in Region.
- The operation requires explicit approval.
- The approved operation fills the missing value with "Unknown".
- Execution logs and cleaning validation are checked.
"""

import pandas as pd

from cleaning.decisions import CleaningDecision
from cleaning.execution import CleaningExecutionEngine
from cleaning.validation import CleaningValidationEngine


def main():
    print("=" * 65)
    print("APPROVED CLEANING OPERATION TEST")
    print("=" * 65)

    # 1. Create controlled test data.
    original_df = pd.DataFrame({
        "Transaction_ID": [101, 102, 103],
        "Region": ["West", None, "North"],
        "Sales": [1200.0, 950.0, 1500.0],
    })

    print("\nOriginal data:")
    print(original_df)

    assert original_df["Region"].isna().sum() == 1

    # 2. Create an explicitly approved cleaning decision.
    decision = CleaningDecision(
        issue_id="TEST_MISSING_Region",
        issue_type="missing_values",
        column="Region",
        affected_rows=1,
        evidence="One missing value in Region.",
        detected_by="Test",
        llm_reasoning=(
            "A missing categorical value is present."
        ),
        recommended_action=(
            "Fill missing categorical values with 'Unknown'"
        ),
        alternative_actions=[
            "Keep missing value",
            "Review manually",
        ],
        confidence=1.0,
        risk_level="MEDIUM",
        requires_approval=True,
        user_decision="APPROVE",
    )

    # 3. Execute the approved decision.
    engine = CleaningExecutionEngine(original_df)

    cleaned_df = engine.execute_decisions([decision])
    execution_logs = engine.get_execution_logs()

    print("\nCleaned data:")
    print(cleaned_df)

    print("\nExecution logs:")
    for log in execution_logs:
        print(log)

    # 4. Verify the exact transformation.
    assert len(cleaned_df) == len(original_df), (
        "Unexpected row-count change."
    )

    assert cleaned_df["Region"].isna().sum() == 0, (
        "The missing Region value was not filled."
    )

    assert cleaned_df.loc[1, "Region"] == "Unknown", (
        "The expected replacement value was not applied."
    )

    assert original_df["Region"].isna().sum() == 1, (
        "The original DataFrame was unexpectedly modified."
    )

    assert len(execution_logs) == 1, (
        "Expected exactly one execution log."
    )

    assert execution_logs[0]["status"] == "executed", (
        "The operation was not logged as executed."
    )

    assert execution_logs[0]["affected_rows"] == 1, (
        "The execution log reports an incorrect affected-row count."
    )

    print("\nTransformation assertions: PASSED")

    # 5. Validate the cleaned dataset.
    validator = CleaningValidationEngine(
        original_df=original_df,
        cleaned_df=cleaned_df,
        execution_logs=execution_logs,
        semantic_mapping={},
    )

    validation = validator.validate_all()

    print("\nCleaning validation:")
    print(validation)

    assert validation.get("overall_status") == "PASSED", (
        "Cleaning validation failed: "
        f"{validation}"
    )

    print("\n" + "=" * 65)
    print("APPROVED CLEANING OPERATION TEST: PASSED")
    print("=" * 65)


if __name__ == "__main__":
    main()
