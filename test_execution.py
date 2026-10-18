import pandas as pd

from agents.planner_agent import PlannerAgent
from cleaning.detection import DataQualityDetector
from cleaning.decisions import CleaningDecisionEngine
from cleaning.execution import CleaningExecutionEngine


def main():

    print("\n")
    print("=" * 60)
    print("          CLEANING EXECUTION ENGINE TEST")
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
        f"Cleaning Decisions Created: "
        f"{len(decisions)}"
    )

    # =========================================================
    # IMPORTANT:
    # APPROVE ONLY A SAFE TEST DECISION
    # =========================================================

    decision_dicts = []

    for decision in decisions:

        decision_dict = decision.to_dict()

        # -----------------------------------------------------
        # For this test, approve only LOW-risk exact duplicates.
        #
        # We DO NOT automatically approve HIGH-risk
        # outlier deletion.
        # -----------------------------------------------------

        if decision.risk_level == "LOW":

            decision_dict["user_decision"] = "APPROVE"

        else:

            decision_dict["user_decision"] = "SKIP"

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

    # =========================================================
    # RESULT
    # =========================================================

    print("\nCLEANED DATASET")
    print("-" * 60)

    print(
        f"Original Rows: {len(df)}"
    )

    print(
        f"Final Rows: {len(cleaned_df)}"
    )

    print(
        f"Rows Removed: "
        f"{len(df) - len(cleaned_df)}"
    )

    print(
        f"Columns: {len(cleaned_df.columns)}"
    )

    # =========================================================
    # EXECUTION LOG
    # =========================================================

    print("\nEXECUTION LOG")
    print("-" * 60)

    if not execution_logs:

        print("No execution logs generated.")

    else:

        for log in execution_logs:

            print("\n" + "-" * 50)

            print(
                f"Issue ID: "
                f"{log['issue_id']}"
            )

            print(
                f"Issue Type: "
                f"{log['issue_type']}"
            )

            print(
                f"Column: "
                f"{log['column']}"
            )

            print(
                f"Action: "
                f"{log['action']}"
            )

            print(
                f"Status: "
                f"{log['status']}"
            )

            print(
                f"Affected Rows: "
                f"{log['affected_rows']}"
            )

            print(
                f"Message: "
                f"{log['message']}"
            )

    # =========================================================
    # SAFETY CHECK
    # =========================================================

    print("\nSAFETY CHECK")
    print("-" * 60)

    high_risk_skipped = 0

    for decision in decision_dicts:

        if (
            decision["risk_level"] == "HIGH"
            and decision["user_decision"] != "APPROVE"
        ):
            high_risk_skipped += 1

    print(
        f"High-risk decisions not approved: "
        f"{high_risk_skipped}"
    )

    print(
        "\nHigh-risk operations were NOT automatically executed."
    )

    # =========================================================
    # COMPLETE
    # =========================================================

    print("\n")
    print("=" * 60)
    print("       EXECUTION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()