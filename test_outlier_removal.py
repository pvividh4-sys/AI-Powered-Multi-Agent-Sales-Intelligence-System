
import pandas as pd

from cleaning.execution import CleaningExecutionEngine


def main():
    print("=" * 65)
    print("OUTLIER REMOVAL APPROVAL TEST")
    print("=" * 65)

    # Small synthetic dataset with one known outlier.
    original_df = pd.DataFrame({
        "Transaction_ID": [101, 102, 103, 104, 105],
        "Sales": [10.0, 11.0, 12.0, 13.0, 100.0],
    })

    lower_bound = 8.0
    upper_bound = 15.0

    print("\nOriginal dataset:")
    print(original_df)

    # --------------------------------------------------
    # Test 1: No approval must prevent removal.
    # --------------------------------------------------
    unapproved_decision = {
        "issue_id": "TEST_OUTLIER_Sales",
        "issue_type": "statistical_outlier",
        "column": "Sales",
        "requires_approval": True,
        "user_decision": "SKIP",
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
    }

    engine_without_approval = CleaningExecutionEngine(
        original_df
    )

    unchanged_df = engine_without_approval.execute_decisions(
        [unapproved_decision]
    )

    assert len(unchanged_df) == 5
    assert unchanged_df["Sales"].tolist() == [
        10.0, 11.0, 12.0, 13.0, 100.0
    ]

    assert (
        engine_without_approval.get_execution_logs()[0]["status"]
        == "skipped"
    )

    print("\nTest 1: Unapproved removal blocked — PASSED")

    # --------------------------------------------------
    # Test 2: Explicit approval permits removal.
    # --------------------------------------------------
    approved_decision = {
        "issue_id": "TEST_OUTLIER_Sales",
        "issue_type": "statistical_outlier",
        "column": "Sales",
        "requires_approval": True,
        "user_decision": "APPROVE",
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
    }

    engine_with_approval = CleaningExecutionEngine(
        original_df
    )

    cleaned_df = engine_with_approval.execute_decisions(
        [approved_decision]
    )

    logs = engine_with_approval.get_execution_logs()

    print("\nCleaned dataset:")
    print(cleaned_df)

    print("\nExecution logs:")
    for log in logs:
        print(log)

    # Only Sales=100.0 should be removed.
    assert len(cleaned_df) == 4
    assert 100.0 not in cleaned_df["Sales"].tolist()
    assert cleaned_df["Sales"].tolist() == [
        10.0, 11.0, 12.0, 13.0
    ]

    assert len(logs) == 1
    assert logs[0]["status"] == "executed"
    assert logs[0]["affected_rows"] == 1

    # The original data must remain untouched.
    assert len(original_df) == 5
    assert 100.0 in original_df["Sales"].tolist()

    print("\nTest 2: Approved removal executed correctly — PASSED")
    print("Original dataset preserved — PASSED")

    print("\n" + "=" * 65)
    print("OUTLIER REMOVAL APPROVAL TEST: PASSED")
    print("=" * 65)


if __name__ == "__main__":
    main()
