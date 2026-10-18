import pandas as pd

from agents.planner_agent import PlannerAgent
from agents.cleaning_agent import CleaningAgent


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = "data/sample/Retail Sales Dataset.csv"


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_value(obj, key, default=None):
    """
    Safely get a value from either:
    - dictionary
    - dataclass/object
    """

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


# ============================================================
# HEADER
# ============================================================

print("\n" + "=" * 60)
print("             DATA CLEANING AGENT TEST")
print("=" * 60)


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("\nLOADING DATASET")
print("-" * 60)

df = pd.read_csv(DATASET_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 2. RUN PLANNER AGENT
# ============================================================

print("\nRUNNING PLANNER")
print("-" * 60)

planner = PlannerAgent()

planner_result = planner.run(df)

print(
    f"Planner Status: "
    f"{planner_result.get('status', 'unknown')}"
)


# ============================================================
# 3. GET SEMANTIC MAPPING
# ============================================================

semantic_mapping = planner_result.get(
    "semantic_mapping",
    {}
)


print("\nSEMANTIC MAPPING")
print("-" * 60)

if semantic_mapping:

    for semantic_type, mapping in semantic_mapping.items():

        if isinstance(mapping, dict):

            column = mapping.get("column")
            confidence = mapping.get("confidence")

            print(
                f"{semantic_type}: "
                f"{column} "
                f"| confidence: {confidence}"
            )

        else:

            print(
                f"{semantic_type}: "
                f"{mapping}"
            )

else:

    print("No semantic mapping returned.")


# ============================================================
# 4. INITIALISE DATA CLEANING AGENT
# ============================================================

print("\nINITIALISING DATA CLEANING AGENT")
print("-" * 60)

cleaning_agent = CleaningAgent(
    df=df,
    semantic_mapping=semantic_mapping
)

print("Cleaning Agent Status: initialized")


# ============================================================
# 5. RUN DETECTION
# ============================================================

print("\nRUNNING DETECTION")
print("-" * 60)

detected_issues = cleaning_agent.detect()

print(
    f"Detected Issues: "
    f"{len(detected_issues)}"
)


# ============================================================
# 6. CREATE CLEANING DECISIONS
# ============================================================

print("\nRUNNING DECISION ENGINE")
print("-" * 60)

cleaning_decisions = (
    cleaning_agent.create_decisions()
)

print(
    f"Cleaning Decisions: "
    f"{len(cleaning_decisions)}"
)


# ============================================================
# 7. DISPLAY CLEANING DECISIONS
# ============================================================

print("\nCLEANING DECISIONS")
print("-" * 60)

if cleaning_decisions:

    for decision in cleaning_decisions:

        print("\n" + "-" * 50)

        print(
            f"Issue ID: "
            f"{get_value(decision, 'issue_id')}"
        )

        print(
            f"Issue Type: "
            f"{get_value(decision, 'issue_type')}"
        )

        print(
            f"Column: "
            f"{get_value(decision, 'column')}"
        )

        print(
            f"Affected Rows: "
            f"{get_value(decision, 'affected_rows')}"
        )

        print(
            f"Recommended Action: "
            f"{get_value(decision, 'recommended_action')}"
        )

        print(
            f"Risk Level: "
            f"{get_value(decision, 'risk_level')}"
        )

        print(
            f"Requires Approval: "
            f"{get_value(decision, 'requires_approval')}"
        )

        print(
            f"User Decision: "
            f"{get_value(decision, 'user_decision')}"
        )

else:

    print("No cleaning decisions created.")


# ============================================================
# 8. RUN APPROVAL + EXECUTION
# ============================================================

print("\nRUNNING APPROVAL + EXECUTION")
print("-" * 60)

# No approvals are supplied.
#
# HIGH-risk decisions therefore remain SKIPPED.
# This verifies that high-risk operations cannot be
# automatically executed.

cleaned_df = cleaning_agent.execute(
    approvals={}
)

print(
    f"Cleaned Rows: "
    f"{len(cleaned_df)}"
)

print(
    f"Rows Removed: "
    f"{len(df) - len(cleaned_df)}"
)


# ============================================================
# 9. EXECUTION LOGS
# ============================================================

execution_logs = (
    cleaning_agent.get_execution_logs()
)

print("\nEXECUTION LOGS")
print("-" * 60)

print(
    f"Execution Logs: "
    f"{len(execution_logs)}"
)

if execution_logs:

    for log in execution_logs:

        print("\n" + "-" * 50)

        print(
            f"Issue ID: "
            f"{get_value(log, 'issue_id')}"
        )

        print(
            f"Action: "
            f"{get_value(log, 'action')}"
        )

        print(
            f"Status: "
            f"{get_value(log, 'status')}"
        )

        print(
            f"Affected Rows: "
            f"{get_value(log, 'affected_rows', 0)}"
        )

        print(
            f"Message: "
            f"{get_value(log, 'message')}"
        )

else:

    print("No execution logs available.")


# ============================================================
# 10. RUN VALIDATION
# ============================================================

print("\nRUNNING VALIDATION")
print("-" * 60)

validation_result = (
    cleaning_agent.validate()
)


# ============================================================
# 11. VALIDATION SUMMARY
# ============================================================

print("\nVALIDATION SUMMARY")
print("-" * 60)

print(
    f"Overall Status: "
    f"{validation_result.get('overall_status', 'unknown')}"
)

print(
    f"Total Checks: "
    f"{validation_result.get('total_checks', 0)}"
)

print(
    f"Passed: "
    f"{validation_result.get('passed', 0)}"
)

print(
    f"Failed: "
    f"{validation_result.get('failed', 0)}"
)

print(
    f"Warnings: "
    f"{validation_result.get('warnings', 0)}"
)


# ============================================================
# 12. DATASET COMPARISON
# ============================================================

print("\nDATASET COMPARISON")
print("-" * 60)

original_rows = len(df)
final_rows = len(cleaned_df)

original_missing = int(
    df.isna().sum().sum()
)

final_missing = int(
    cleaned_df.isna().sum().sum()
)

original_duplicates = int(
    df.duplicated().sum()
)

final_duplicates = int(
    cleaned_df.duplicated().sum()
)

print(
    f"Original Rows: "
    f"{original_rows}"
)

print(
    f"Final Rows: "
    f"{final_rows}"
)

print(
    f"Rows Removed: "
    f"{original_rows - final_rows}"
)

print(
    f"Original Missing Values: "
    f"{original_missing}"
)

print(
    f"Final Missing Values: "
    f"{final_missing}"
)

print(
    f"Original Duplicate Rows: "
    f"{original_duplicates}"
)

print(
    f"Final Duplicate Rows: "
    f"{final_duplicates}"
)


# ============================================================
# 13. SAFETY CHECK
# ============================================================

print("\nSAFETY CHECK")
print("-" * 60)

high_risk_decisions = 0
high_risk_executions = 0

for decision in cleaning_decisions:

    risk_level = str(
        get_value(
            decision,
            "risk_level",
            ""
        )
    ).upper()

    requires_approval = get_value(
        decision,
        "requires_approval",
        False
    )

    user_decision = str(
        get_value(
            decision,
            "user_decision",
            ""
        )
    ).upper()

    if (
        risk_level == "HIGH"
        and requires_approval
    ):

        high_risk_decisions += 1

        if user_decision != "APPROVE":

            print(
                f"Protected: "
                f"{get_value(decision, 'issue_id')} "
                f"was not approved."
            )


for log in execution_logs:

    status = str(
        get_value(
            log,
            "status",
            ""
        )
    ).lower()

    if status != "executed":
        continue

    issue_id = get_value(
        log,
        "issue_id"
    )

    for decision in cleaning_decisions:

        decision_issue_id = get_value(
            decision,
            "issue_id"
        )

        decision_risk = str(
            get_value(
                decision,
                "risk_level",
                ""
            )
        ).upper()

        if (
            decision_issue_id == issue_id
            and decision_risk == "HIGH"
        ):

            high_risk_executions += 1


print(
    f"\nHigh-risk decisions: "
    f"{high_risk_decisions}"
)

print(
    f"High-risk operations executed: "
    f"{high_risk_executions}"
)

if high_risk_executions == 0:

    print(
        "Safety Check: PASSED"
    )

    print(
        "No unapproved high-risk operation "
        "was executed."
    )

else:

    print(
        "Safety Check: FAILED"
    )

    print(
        "A high-risk operation was executed."
    )


# ============================================================
# 14. FINAL AGENT STATUS
# ============================================================

print("\nFINAL AGENT STATUS")
print("-" * 60)

print(
    f"Cleaning Agent Status: "
    f"{cleaning_agent.status}"
)

print(
    f"Validation Status: "
    f"{validation_result.get('overall_status', 'unknown')}"
)


# ============================================================
# 15. FINAL RESULT
# ============================================================

if (
    validation_result.get("overall_status")
    == "PASSED"
    and high_risk_executions == 0
):

    print(
        "\n8.3.5 DATA CLEANING AGENT INTEGRATION: PASSED"
    )

else:

    print(
        "\n8.3.5 DATA CLEANING AGENT INTEGRATION: "
        "REVIEW REQUIRED"
    )


print("\n" + "=" * 60)
print("       CLEANING AGENT TEST COMPLETED")
print("=" * 60)