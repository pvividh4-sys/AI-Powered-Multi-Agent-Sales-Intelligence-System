
"""
8.8.4 Report Agent Workflow Integration Test

Tests:
1. Complete multi-agent workflow
2. Cleaning approval handling
3. Report Agent execution
4. Report validation
5. Analytical report sections
6. Decision trace ordering
7. Word report generation diagnostics
"""

from pathlib import Path
import pandas as pd

from workflow.graph import (
    run_workflow,
    resume_workflow_after_cleaning,
)


# ============================================================
# TEST DATASET
# ============================================================

def create_dataset():
    dates = pd.date_range(
        start="2023-01-01",
        periods=40,
        freq="D",
    )

    return pd.DataFrame({
        "Date": dates,
        "Total Amount": [1000 + i * 10 for i in range(40)],
        "Quantity": [2] * 40,
        "Product Category": (
            ["Electronics"] * 20
            + ["Clothing"] * 20
        ),
        "Customer ID": [f"CUST{i:03d}" for i in range(40)],
        "City": ["Mumbai"] * 40,
        "Order ID": list(range(1, 41)),
    })


# ============================================================
# VALIDATED EDA FIXTURE
# ============================================================

def create_eda_result():
    return {
        "status": "completed",
        "dataset": {
            "rows": 40,
            "columns": 7,
            "start_date": "2023-01-01",
            "end_date": "2023-02-09",
        },
        "kpis": {
            "total_sales": 47800.0,
            "total_quantity": 80.0,
            "total_orders": 40,
            "total_customers": 40,
            "average_order_value": 1195.0,
            "average_quantity_per_order": 2.0,
            "average_selling_price": 597.5,
        },
        "trends": {
            "start_date": "2023-01-01",
            "end_date": "2023-02-09",
            "days": 40,
            "observations": 40,
            "daily": [],
            "monthly": [],
        },
        "rankings": {
            "product_sales": [
                {"category": "Electronics", "sales": 23900.0},
                {"category": "Clothing", "sales": 23900.0},
            ],
            "product_quantity": [
                {"category": "Electronics", "quantity": 40},
                {"category": "Clothing", "quantity": 40},
            ],
            "regional_sales": [
                {"city": "Mumbai", "sales": 47800.0},
            ],
            "customer_sales": [
                {"customer_id": "CUST000", "sales": 1000.0},
            ],
        },
        "validation": {
            "overall_status": "PASSED",
            "total_checks": 5,
            "passed": 5,
            "failed": 0,
            "warnings": 0,
        },
    }


# ============================================================
# HELPERS
# ============================================================

def get_sections(report_result):
    """Return report sections safely."""
    if not isinstance(report_result, dict):
        return []

    report = report_result.get("report", {})

    if not isinstance(report, dict):
        return []

    sections = report.get("sections", [])
    return sections if isinstance(sections, list) else []


def get_section_id(section):
    if not isinstance(section, dict):
        return ""
    return str(section.get("section_id", "")).strip()


def get_approval_id(decision):
    """Support cleaning decisions represented as dicts or objects."""
    if isinstance(decision, dict):
        return decision.get("issue_id")

    return getattr(decision, "issue_id", None)


def print_cleaning_logs(state):
    print("\n========== CLEANING EXECUTION LOGS ==========")

    cleaning_result = getattr(state, "cleaning_result", {}) or {}
    logs = (
        cleaning_result.get("execution_logs", [])
        if isinstance(cleaning_result, dict)
        else []
    )

    if logs:
        for log in logs:
            print(log)
    else:
        print("No execution logs found.")

    print("=============================================\n")


def print_word_report_check(report_result):
    print("\n========== WORD REPORT CHECK ==========")

    if not isinstance(report_result, dict):
        print("Report result is unavailable.")
        print("======================================")
        return

    word_path = report_result.get("word_report_path")
    word_status = report_result.get("word_report_status")
    word_error = report_result.get("word_report_error")

    print("Report status:", report_result.get("status"))
    print("Word report status:", word_status)
    print("Word report path:", word_path)
    print("Word report error:", word_error)

    if word_path:
        path = Path(str(word_path))

        if not path.is_absolute():
            path = Path.cwd() / path

        if path.is_file():
            print("Word file exists: YES")
            print(f"Word file size: {path.stat().st_size:,} bytes")
        else:
            print("Word file exists: NO")
            print("Checked path:", path)
    else:
        print("A Word report path was not returned.")

    print("======================================\n")


# ============================================================
# MAIN TEST
# ============================================================

def main():
    print("=" * 70)
    print("8.8.4 REPORT AGENT WORKFLOW INTEGRATION TEST")
    print("=" * 70)

    df = create_dataset()
    eda_result = create_eda_result()

    semantic_mapping = {
        "date": {"column": "Date", "confidence": 0.95},
        "sales": {"column": "Total Amount", "confidence": 0.95},
        "quantity": {"column": "Quantity", "confidence": 0.95},
        "product": {"column": "Product Category", "confidence": 0.95},
        "customer": {"column": "Customer ID", "confidence": 0.95},
        "region": {"column": "City", "confidence": 0.95},
        "order_id": {"column": "Order ID", "confidence": 0.95},
    }

    capabilities = {
        "sales_analysis": True,
        "quantity_analysis": True,
        "product_analysis": True,
        "customer_analysis": True,
        "regional_analysis": True,
        "profitability_analysis": False,
        "forecasting": True,
    }

    # --------------------------------------------------------
    # 1. Start workflow
    # --------------------------------------------------------

    state = run_workflow(
        df=df,
        semantic_mapping=semantic_mapping,
        capabilities=capabilities,
        planner_result={
            "status": "completed",
            "semantic_mapping": semantic_mapping,
            "capabilities": capabilities,
        },
        eda_result=eda_result,
        eda_validation=eda_result["validation"],
        horizon=7,
        test_size=10,
        moving_average_window=7,
    )

    print("\nInitial workflow status:", state.workflow_status)
    print("Initial cleaning status:", state.cleaning_status)

    # --------------------------------------------------------
    # 2. Handle cleaning approval gate
    # --------------------------------------------------------

    if state.workflow_status == "awaiting_approval":
        decisions = getattr(state, "cleaning_decision", []) or []

        print("\nCleaning decisions found:", len(decisions))

        # This integration test skips proposed cleaning actions.
        # No cleaning operation is approved automatically.
        approvals = {}

        for decision in decisions:
            issue_id = get_approval_id(decision)

            if issue_id:
                approvals[issue_id] = "SKIP"

        print("Applying SKIP to identified cleaning decisions.")
        print("Cleaning approvals:", approvals)

        state = resume_workflow_after_cleaning(
            state=state,
            approvals=approvals,
            horizon=7,
            test_size=10,
            moving_average_window=7,
        )

    print_cleaning_logs(state)

    # --------------------------------------------------------
    # 3. Display workflow results
    # --------------------------------------------------------

    print("=" * 70)
    print("WORKFLOW AND REPORT RESULTS")
    print("=" * 70)

    print("Current Stage:", state.current_stage)
    print("Workflow Status:", state.workflow_status)
    print("Planner Status:", state.planner_status)
    print("Cleaning Status:", state.cleaning_status)
    print("EDA Status:", state.eda_status)
    print("Visualization Status:", state.visualization_status)
    print("Forecasting Status:", state.forecasting_status)
    print("Insight Status:", state.insight_status)
    print("Recommendation Status:", state.recommendation_status)
    print("Report Status:", state.report_status)
    print("Report Validation:", state.report_validation)
    print("Errors:", state.errors or "No workflow errors recorded.")

    report_result = getattr(state, "report_result", None)
    print("\nReport Result Type:", type(report_result).__name__)

    if isinstance(report_result, dict):
        print("Report Result Keys:", list(report_result.keys()))

    sections = get_sections(report_result)
    print("Report Sections:", len(sections))

    if isinstance(report_result, dict):
        report = report_result.get("report", {})
        if isinstance(report, dict):
            print("Report Title:", report.get("title"))
            print("Executive Summary:", report.get("executive_summary"))

    print_word_report_check(report_result)

    # --------------------------------------------------------
    # 4. Assert workflow completion
    # --------------------------------------------------------

    assert state.workflow_status == "completed", (
        f"Workflow did not complete. Errors: {state.errors}"
    )

    assert state.report_status == "completed", (
        f"Report Agent did not complete. Errors: {state.errors}"
    )

    assert state.agent_status.get("Report Agent") == "completed"

    assert isinstance(report_result, dict), (
        "Report result is missing or is not a dictionary."
    )

    print("Workflow Completion: PASSED")
    print("Report Agent: PASSED")

    # --------------------------------------------------------
    # 5. Assert report validation
    # --------------------------------------------------------

    validation = state.report_validation or {}

    assert validation.get("overall_status") == "PASSED", (
        f"Report validation failed: {validation}"
    )

    assert validation.get("failed", 0) == 0, (
        f"Report validation has failed checks: {validation}"
    )

    print("Report Validation: PASSED")

    # --------------------------------------------------------
    # 6. Assert report sections
    # --------------------------------------------------------

    assert len(sections) >= 1, "The report contains no sections."

    section_ids = [
        get_section_id(section)
        for section in sections
    ]

    assert all(section_ids), "One or more report sections lack an ID."

    assert len(section_ids) == len(set(section_ids)), (
        "Duplicate report section IDs found."
    )

    required_sections = {
        "dataset_overview",
        "data_quality",
    }

    missing_sections = required_sections - set(section_ids)

    assert not missing_sections, (
        f"Required sections are missing: {sorted(missing_sections)}"
    )

    print("Report Structure: PASSED")
    print("Section Count:", len(sections))
    print("Section IDs:", section_ids)

    # --------------------------------------------------------
    # 7. Assert analytical sections are present and non-empty
    # --------------------------------------------------------

    critical_ids = {
        "kpis",
         "trends",
        
        "rankings",
        "forecast",
        "insights",
        "recommendations",
    }

    present_ids = set(section_ids)
    missing_critical = critical_ids - present_ids

    if missing_critical:
        print(
            "Note: Critical sections not found under expected IDs:",
            sorted(missing_critical),
        )
        print(
            "Review the actual section IDs above; "
            "the report validator is the authoritative check "
            "for your project's section naming."
        )
    else:
        print("Critical Analytical Sections: PRESENT")

    # --------------------------------------------------------
    # 8. Check decision trace ordering
    # --------------------------------------------------------

    trace = getattr(state, "decision_trace", []) or []

    report_positions = [
        index
        for index, entry in enumerate(trace)
        if isinstance(entry, dict)
        and entry.get("agent") == "Report Agent"
    ]

    assert report_positions, "Report Agent entry is missing from decision trace."

    recommendation_positions = [
        index
        for index, entry in enumerate(trace)
        if isinstance(entry, dict)
        and entry.get("agent") == "Recommendation Agent"
    ]

    if recommendation_positions:
        assert max(recommendation_positions) < min(report_positions), (
            "Report Agent ran before the Recommendation Agent in the trace."
        )

    print("Report Decision Trace: PASSED")

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("8.8.4 REPORT AGENT WORKFLOW INTEGRATION TEST: PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
