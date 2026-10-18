
"""
End-to-end integration test for the
AI-Powered Multi-Agent Sales Intelligence System.

This test uses explicit SKIP approvals for cleaning decisions
so detected outliers are preserved rather than automatically removed.
"""

from pathlib import Path

import pandas as pd

from workflow.graph import run_workflow


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "Retail Sales Dataset.csv"
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def print_section(title):
    """Print a clearly separated terminal section."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def load_dataset():
    """Load the sample retail sales dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}\n"
            "Check DATASET_PATH in test_end_to_end.py."
        )

    df = pd.read_csv(DATASET_PATH)

    if df.empty:
        raise ValueError("The dataset contains no rows.")

    print(f"Dataset: {DATASET_PATH}")
    print(f"Dataset shape: {df.shape}")
    print("Dataset load: PASSED")

    return df


def get_cleaning_approvals(state):
    """
    Build explicit SKIP approvals from CleaningDecision objects.

    Supports both dictionaries and objects with an issue_id
    attribute. SKIP preserves detected outliers.
    """

    decisions = state.cleaning_decision or []
    approvals = {}

    if isinstance(decisions, dict):
        decisions = decisions.get(
            "decisions",
            decisions.get("cleaning_decisions", []),
        )

    for decision in decisions:
        if isinstance(decision, dict):
            issue_id = decision.get("issue_id")
        else:
            issue_id = getattr(
                decision,
                "issue_id",
                None,
            )

        if issue_id:
            approvals[str(issue_id)] = "SKIP"

    return approvals


# =========================================================
# MAIN TEST
# =========================================================

def main():
    print_section(
        "AI-POWERED MULTI-AGENT SALES INTELLIGENCE SYSTEM"
    )

    df = load_dataset()

    # -----------------------------------------------------
    # 1. CLEANING APPROVAL DISCOVERY
    # -----------------------------------------------------

    print_section("1. CLEANING APPROVAL DISCOVERY")

    initial_state = run_workflow(df.copy())

    if initial_state is None:
        raise AssertionError("Workflow returned None.")

    print("Initial status:", initial_state.workflow_status)
    print("Cleaning status:", initial_state.cleaning_status)

    # If approval is required, discover the actual decision IDs
    # and rerun the workflow with explicit test approvals.
    if initial_state.workflow_status == "awaiting_approval":
        approvals = get_cleaning_approvals(initial_state)

        print(
            "Cleaning decisions:",
            len(initial_state.cleaning_decision or []),
        )
        print("Approvals prepared:", approvals)

        if (
            initial_state.cleaning_decision
            and not approvals
        ):
            raise AssertionError(
                "Cleaning decisions exist, but approval keys "
                "could not be generated."
            )

        print(
            "\nRe-running workflow with explicit SKIP approvals."
        )

        state = run_workflow(
            df.copy(),
            approvals=approvals,
        )

    else:
        state = initial_state

    if state is None:
        raise AssertionError("Workflow returned None.")

    # -----------------------------------------------------
    # 2. AGENT STATUS
    # -----------------------------------------------------

    print_section("2. AGENT STATUS")

    expected_agents = [
        "Planner Agent",
        "Data Cleaning Agent",
        "EDA Agent",
        "Visualization Agent",
        "Forecasting Agent",
        "Insight Agent",
        "Recommendation Agent",
        "Report Agent",
    ]

    accepted_statuses = {
        "Planner Agent": {"completed"},
        "Data Cleaning Agent": {"validated"},
        "EDA Agent": {
            "completed",
            "completed_with_warnings",
        },
        "Visualization Agent": {
            "completed",
            "completed_with_warnings",
        },
        "Forecasting Agent": {
            "completed",
            "skipped",
        },
        "Insight Agent": {"completed"},
        "Recommendation Agent": {"completed"},
        "Report Agent": {"completed"},
    }

    all_agents_completed = True

    for name in expected_agents:
        status = state.agent_status.get(
            name,
            "missing",
        )

        print(f"{name}: {status}")

        if status not in accepted_statuses[name]:
            all_agents_completed = False

    # -----------------------------------------------------
    # 3. VALIDATION SUMMARY
    # -----------------------------------------------------

    print_section("3. VALIDATION SUMMARY")

    validations = {
        "Cleaning": state.cleaning_validation,
        "EDA": state.eda_validation,
        "Visualization": state.visualization_validation,
        "Insight": state.insight_validation,
        "Recommendation": state.recommendation_validation,
        "Report": state.report_validation,
    }

    validation_failures = []

    for name, result in validations.items():
        if not isinstance(result, dict):
            print(f"{name}: unavailable")
            validation_failures.append(name)
            continue

        status = str(
            result.get(
                "overall_status",
                result.get("status", "UNKNOWN"),
            )
        ).upper()

        print(f"{name}: {status}")

        if status not in {
            "PASSED",
            "PASS",
            "COMPLETED",
        }:
            validation_failures.append(name)

    # -----------------------------------------------------
    # 4. FINAL WORKFLOW STATUS
    # -----------------------------------------------------

    print_section("4. END-TO-END RESULT")

    errors = getattr(state, "errors", []) or []

    print("Workflow status:", state.workflow_status)
    print("Current stage:", state.current_stage)
    print("Cleaning status:", state.cleaning_status)
    print("Errors:", errors)

    # -----------------------------------------------------
    # 5. FINAL ASSERTIONS
    # -----------------------------------------------------

    if state.workflow_status != "completed":
        raise AssertionError(
            f"Workflow did not complete: "
            f"{state.workflow_status}; "
            f"stage={state.current_stage}; "
            f"errors={errors}"
        )

    if not all_agents_completed:
        raise AssertionError(
            "One or more agents did not reach their expected status."
        )

    if validation_failures:
        raise AssertionError(
            "Validation failed or was unavailable for: "
            + ", ".join(validation_failures)
        )

    if errors:
        raise AssertionError(
            f"Workflow errors: {errors}"
        )

    print("\nAll eight agents passed their status checks.")
    print("All required validation checks passed.")
    print("END-TO-END TEST: PASSED")


if __name__ == "__main__":
    main()
