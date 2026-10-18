import pandas as pd

from cleaning.detection import DataQualityDetector
from cleaning.decisions import CleaningDecisionEngine
from cleaning.execution import CleaningExecutionEngine
from cleaning.validation import CleaningValidationEngine


def main():
    # 1. Create a small dataset containing calculation inconsistencies
    df = pd.DataFrame({
        "Quantity": [1, 2, 2],
        "Price per Unit": [50, 25, 30],
        "Total Amount": [0, 0, 60],
        "Total Price": [0, 0, 60],
    })

    print("=" * 60)
    print("TEST: CALCULATION MISMATCH DETECTION AND CORRECTION")
    print("=" * 60)

    print("\nOriginal Dataset:")
    print(df.to_string(index=False))

    # 2. Detect data quality issues
    print("\n[STEP 1] Detecting calculation mismatches...")

    detector = DataQualityDetector(df)
    issues = detector.detect_all()

    calculation_issues = [
        issue
        for issue in issues
        if issue.get("issue_type") == "calculation_mismatch"
    ]

    if not calculation_issues:
        print("No calculation mismatches detected.")
        print("Check whether detect_calculation_mismatches()")
        print("has been implemented and called inside detect_all().")
        return

    print(f"Detected {len(calculation_issues)} calculation issue(s):")

    for issue in calculation_issues:
        print(
            f"  Column: {issue.get('column')}, "
            f"Affected rows: {issue.get('affected_rows')}"
        )

    # 3. Generate cleaning decisions
    print("\n[STEP 2] Generating cleaning decisions...")

    decision_engine = CleaningDecisionEngine()
    decisions = decision_engine.create_decisions(calculation_issues)

    print(f"Generated {len(decisions)} cleaning decision(s).")

    # 4. Approve corrections for this isolated test only
    print("\n[STEP 3] Approving corrections for this test...")

    for decision in decisions:
        if isinstance(decision, dict):
            decision["user_decision"] = "APPROVE"
        else:
            decision.user_decision = "APPROVE"

    # 5. Execute the approved cleaning decisions
    print("\n[STEP 4] Executing approved corrections...")

    executor = CleaningExecutionEngine(df)
    cleaned_df = executor.execute_decisions(decisions)

    print("\nCleaned Dataset:")
    print(cleaned_df.to_string(index=False))

    # 6. Validate the cleaned dataset
    print("\n[STEP 5] Validating the cleaned dataset...")

    validator = CleaningValidationEngine(
        original_df=df,
        cleaned_df=cleaned_df,
        execution_logs=executor.get_execution_logs(),
    )

    validation_result = validator.validate_all()

    print("\nValidation Result:")
    print(validation_result)

    # 7. Check the expected values
    print("\n[STEP 6] Checking expected results...")

    expected_total_amount = [50, 50, 60]
    expected_total_price = [50, 50, 60]

    amount_correct = (
        cleaned_df["Total Amount"].tolist() == expected_total_amount
    )
    price_correct = (
        cleaned_df["Total Price"].tolist() == expected_total_price
    )

    if amount_correct and price_correct:
        print("PASS: Total Amount and Total Price are correct.")
    else:
        print("FAIL: The calculated totals do not match expectations.")
        print("Expected Total Amount:", expected_total_amount)
        print("Actual Total Amount:  ", cleaned_df["Total Amount"].tolist())
        print("Expected Total Price: ", expected_total_price)
        print("Actual Total Price:  ", cleaned_df["Total Price"].tolist())

    # 8. Print the overall validation status
    overall_status = validation_result.get("overall_status")

    print("\nOverall Validation Status:", overall_status)
    print("=" * 60)


if __name__ == "__main__":
    main()