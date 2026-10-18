import pandas as pd

from agents.planner_agent import PlannerAgent
from cleaning.detection import DataQualityDetector
from cleaning.decisions import CleaningDecisionEngine
from cleaning.execution import CleaningExecutionEngine
from cleaning.validation import CleaningValidationEngine


def main():

    print("\n")
    print("=" * 60)
    print("          CLEANING VALIDATION ENGINE TEST")
    print("=" * 60)

    # =========================================================
    # LOAD DATASET
    # =========================================================

    file_path = "data/sample/Retail Sales Dataset.csv"

    df = pd.read_csv(file_path)

    print("\nORIGINAL DATASET")
    print("-" * 60)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # =========================================================
    # PLANNER
    # =========================================================

    print("\nRUNNING PLANNER")
    print("-" * 60)

    planner = PlannerAgent()

    planner_result = planner.run(df)

    semantic_mapping = planner_result.get(
        "semantic_mapping",
        {}
    )

    print(
        f"Planner Status: "
        f"{planner_result.get('status', 'unknown')}"
    )

    # =========================================================
    # DETECTION
    # =========================================================

    print("\nRUNNING DETECTION")
    print("-" * 60)

    detector = DataQualityDetector(
        df=df,
        semantic_mapping=semantic_mapping
    )

    issues = detector.detect_all()

    print(
        f"Detected Issues: {len(issues)}"
    )

    # =========================================================
    # DECISION ENGINE
    # =========================================================

    print("\nRUNNING DECISION ENGINE")
    print("-" * 60)

    decision_engine = CleaningDecisionEngine()

    decisions = decision_engine.create_decisions(
        issues
    )

    print(
        f"Cleaning Decisions: "
        f"{len(decisions)}"
    )

    # =========================================================
    # PREPARE DECISIONS
    # =========================================================

    decision_dicts = []

    for decision in decisions:

        decision_dict = decision.to_dict()

        # HIGH-risk decisions are skipped.
        # LOW-risk decisions would be approved.

        if decision.risk_level == "LOW":

            decision_dict["user_decision"] = "APPROVE"

        else:

            decision_dict["user_decision"] = "SKIP"

        # Preserve detector metadata
        issue = next(
            (
                item
                for item in issues
                if item["issue_id"]
                == decision.issue_id
            ),
            None
        )

        if issue:

            if "lower_bound" in issue:

                decision_dict["lower_bound"] = (
                    issue["lower_bound"]
                )

            if "upper_bound" in issue:

                decision_dict["upper_bound"] = (
                    issue["upper_bound"]
                )

        decision_dicts.append(
            decision_dict
        )

    # =========================================================
    # EXECUTION
    # =========================================================

    print("\nRUNNING EXECUTION ENGINE")
    print("-" * 60)

    execution_engine = CleaningExecutionEngine(
        df
    )

    cleaned_df, execution_logs = (
        execution_engine.execute_decisions(
            decision_dicts
        )
    )

    print(
        f"Execution logs: "
        f"{len(execution_logs)}"
    )

    # =========================================================
    # DATE COLUMN FROM PLANNER
    # =========================================================

    date_column = None

    date_mapping = semantic_mapping.get(
        "date"
    )

    if isinstance(date_mapping, str):

        date_column = date_mapping

    elif isinstance(date_mapping, dict):

        date_column = date_mapping.get(
            "column"
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    print("\nRUNNING VALIDATION ENGINE")
    print("-" * 60)

    validator = CleaningValidationEngine(
        original_df=df,
        cleaned_df=cleaned_df,
        execution_logs=execution_logs,
        semantic_mapping=semantic_mapping
    )

    validation_result = validator.validate_all(
        date_column=date_column
    )

    # =========================================================
    # VALIDATION SUMMARY
    # =========================================================

    print("\nVALIDATION SUMMARY")
    print("-" * 60)

    print(
        f"Overall Status: "
        f"{validation_result['overall_status']}"
    )

    print(
        f"Total Checks: "
        f"{validation_result['total_checks']}"
    )

    print(
        f"Passed: "
        f"{validation_result['passed_checks']}"
    )

    print(
        f"Failed: "
        f"{validation_result['failed_checks']}"
    )

    print(
        f"Warnings: "
        f"{validation_result['warning_checks']}"
    )

    # =========================================================
    # INDIVIDUAL CHECKS
    # =========================================================

    print("\nVALIDATION CHECKS")
    print("-" * 60)

    for check in validation_result["checks"]:

        print("\n" + "-" * 50)

        print(
            f"Check: "
            f"{check['check_name']}"
        )

        print(
            f"Status: "
            f"{check['status']}"
        )

        print(
            f"Message: "
            f"{check['message']}"
        )

        if check["before"] is not None:

            print(
                f"Before: "
                f"{check['before']}"
            )

        if check["after"] is not None:

            print(
                f"After: "
                f"{check['after']}"
            )

    # =========================================================
    # DATASET COMPARISON
    # =========================================================

    print("\nDATASET COMPARISON")
    print("-" * 60)

    print(
        f"Original rows: "
        f"{len(df)}"
    )

    print(
        f"Final rows: "
        f"{len(cleaned_df)}"
    )

    print(
        f"Rows removed: "
        f"{len(df) - len(cleaned_df)}"
    )

    print(
        f"Original missing values: "
        f"{int(df.isna().sum().sum())}"
    )

    print(
        f"Final missing values: "
        f"{int(cleaned_df.isna().sum().sum())}"
    )

    print(
        f"Original duplicate rows: "
        f"{int(df.duplicated().sum())}"
    )

    print(
        f"Final duplicate rows: "
        f"{int(cleaned_df.duplicated().sum())}"
    )

    # =========================================================
    # COMPLETE
    # =========================================================

    print("\n")
    print("=" * 60)
    print("       VALIDATION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()