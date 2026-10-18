"""
Complete workflow execution graph.

Eight-agent execution order:

1. Planner Agent
2. Data Cleaning Agent
3. EDA Agent
4. Visualization Agent
5. Forecasting Agent
6. Insight Agent
7. Recommendation Agent
8. Report Agent

Human approval is required at the Data Cleaning stage for
risk-sensitive cleaning operations.

Workflow:

    Raw Dataset
         ↓
    Planner
         ↓
    Cleaning Detection + Decisions
         ↓
    HUMAN APPROVAL
         ↓
    Cleaning Execution
         ↓
    Cleaning Validation
         ↓
    EDA
         ↓
    Visualization
         ↓
    Forecasting
         ↓
    Insight
         ↓
    Recommendation
         ↓
    Report
         ↓
    Final Validation
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from agents.planner_agent import PlannerAgent
from agents.cleaning_agent import CleaningAgent
from agents.eda_agent import EDAAgent
from agents.visualization_agent import VisualizationAgent
from agents.forecasting_agent import ForecastingAgent
from agents.insight_agent import InsightAgent
from agents.recommendation_agent import RecommendationAgent
from agents.report_agent import ReportAgent

from workflow.routing import (
    RUN_FORECASTING,
    RUN_INSIGHT,
    RUN_RECOMMENDATION,
    route_forecasting,
    route_insight,
    route_recommendation,
)

from workflow.state import (
    WorkflowState,
    create_initial_state,
)


# =====================================================================
# HELPERS
# =====================================================================

def _status_passed(
    validation: Optional[Dict[str, Any]],
) -> bool:
    """
    Return True when a validation dictionary passed.
    """

    if not isinstance(validation, dict):
        return False

    return (
        validation.get("overall_status")
        == "PASSED"
    )


def _append_stage_trace(
    state: WorkflowState,
    agent: str,
    decision: str,
    reason: str,
    evidence: Any,
    action: str,
    result: Any,
    validation_status: str,
) -> None:
    """
    Add a standard workflow decision-trace entry.
    """

    state.add_decision_trace(
        agent=agent,
        decision=decision,
        reason=reason,
        evidence=evidence,
        action=action,
        result=result,
        validation_status=validation_status,
    )


# =====================================================================
# PLANNER NODE
# =====================================================================

def planner_node(
    state: WorkflowState,
) -> WorkflowState:
    """
    Execute the Planner Agent.

    Responsibilities:

    - Inspect schema
    - Detect semantic mappings
    - Determine analytical capabilities
    - Create analysis plan
    - Determine forecasting eligibility
    """

    state.current_stage = "planner"

    state.set_agent_status(
        "Planner Agent",
        "running",
    )

    try:

        df = state.df

        if df is None or df.empty:
            raise ValueError(
                "Planner Agent cannot process an empty dataset."
            )

        agent = PlannerAgent()

        result = agent.run(df)

        if not isinstance(result, dict):
            raise TypeError(
                "Planner Agent must return a dictionary."
            )

        if result.get("status") != "completed":
            raise RuntimeError(
                result.get(
                    "error",
                    "Planner Agent failed.",
                )
            )

        state.planner_result = result

        state.semantic_mapping = result.get(
            "semantic_mapping",
            result.get(
                "mapping",
                {},
            ),
        )

        state.capabilities = result.get(
            "capabilities",
            {},
        )

        state.execution_plan = result.get(
            "analysis_plan",
            result.get(
                "execution_plan",
                [],
            ),
        )

        state.planner_status = "completed"

        state.set_agent_status(
            "Planner Agent",
            "completed",
        )

        _append_stage_trace(
            state=state,
            agent="Planner Agent",
            decision="Execute Planner Agent",
            reason=(
                "Planner Agent inspects the raw dataset and "
                "determines the available analytical capabilities."
            ),
            evidence={
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
                "column_names": list(df.columns),
            },
            action=(
                "Detect semantic mappings, capabilities and "
                "the analytical execution plan."
            ),
            result={
                "status": "completed",
                "semantic_mapping": state.semantic_mapping,
                "capabilities": state.capabilities,
            },
            validation_status="COMPLETED",
        )

    except Exception as exc:

        state.planner_status = "failed"

        state.set_agent_status(
            "Planner Agent",
            "failed",
        )

        state.add_error(
            f"Planner Agent failed: {exc}"
        )

    return state


# =====================================================================
# CLEANING NODE
# =====================================================================


def cleaning_node(
    state: WorkflowState,
    approvals: Optional[Dict[str, str]] = None,
) -> WorkflowState:
    """
    Execute the Data Cleaning Agent.

    Without approvals, pause for human review.
    With approvals, execute cleaning and explicitly validate
    the resulting dataset before allowing the workflow to continue.
    """

    state.current_stage = "cleaning"

    state.set_agent_status(
        "Data Cleaning Agent",
        "running",
    )

    try:
        df = state.get_analysis_df()

        if df is None or df.empty:
            raise ValueError(
                "Data Cleaning Agent cannot process an empty dataset."
            )

        agent = CleaningAgent(
            df=df,
            semantic_mapping=state.semantic_mapping,
        )

        # Step 1: Detect data quality issues.
        detected_issues = agent.detect()

        # Step 2: Generate cleaning decisions.
        decisions = agent.create_decisions()

        state.cleaning_decision = decisions

        # Step 3: Pause when approvals have not been supplied.
        if approvals is None:
            state.cleaned_df = df.copy()

            state.cleaning_result = {
                "agent": "Data Cleaning Agent",
                "status": "awaiting_approval",
                "original_rows": int(df.shape[0]),
                "original_columns": int(df.shape[1]),
                "detected_issues": detected_issues,
                "cleaning_decisions": decisions,
                "execution_logs": [],
                "validation": {},
                "cleaned_df": df.copy(),
            }

            state.cleaning_status = "awaiting_approval"

            state.set_agent_status(
                "Data Cleaning Agent",
                "awaiting_approval",
            )

            _append_stage_trace(
                state=state,
                agent="Data Cleaning Agent",
                decision="Pause for Human Approval",
                reason=(
                    "Cleaning decisions require review before "
                    "risk-sensitive operations are executed."
                ),
                evidence={
                    "detected_issues": len(detected_issues or []),
                    "cleaning_decisions": len(decisions or []),
                    "approval_required": True,
                },
                action="Wait for explicit cleaning approvals.",
                result={
                    "status": "awaiting_approval",
                    "rows": int(df.shape[0]),
                    "decisions": len(decisions or []),
                },
                validation_status="PENDING_APPROVAL",
            )

            return state

        # Step 4: Execute decisions using the supplied approvals.
        agent.execute(approvals=approvals)

        # Step 5: Explicitly run validation.
        # Do not rely on get_validation_result() to execute validation.
        validation_result = agent.validate()

        # Step 6: Store all outputs in the workflow state.
        state.cleaning_validation = validation_result
        state.cleaning_decision = agent.get_cleaning_decisions()
        state.cleaned_df = agent.get_cleaned_data()
        state.cleaning_result = agent.get_result()

        state.cleaning_status = state.cleaning_result.get(
            "status",
            "unknown",
        )

        # Step 7: Print detailed validation diagnostics.
        print("\n" + "=" * 72)
        print("DATA CLEANING VALIDATION DETAILS")
        print("=" * 72)
        print(f"Overall status: {validation_result.get('overall_status')}")

        for key, value in validation_result.items():
            print(f"{key}: {value}")

        print("=" * 72 + "\n")

        # Step 8: Enforce the validation gate.
        if not _status_passed(validation_result):
            state.cleaning_status = "validation_failed"

            state.set_agent_status(
                "Data Cleaning Agent",
                "failed",
            )

            state.add_error(
                "Data Cleaning Agent validation failed. "
                f"Validation details: {validation_result}"
            )

            return state

        # Step 9: Mark cleaning as validated.
        state.cleaning_status = "validated"

        state.set_agent_status(
            "Data Cleaning Agent",
            "validated",
        )

        _append_stage_trace(
            state=state,
            agent="Data Cleaning Agent",
            decision="Execute Approved Cleaning Actions",
            reason=(
                "Cleaning decisions were processed using explicit "
                "approvals, and the cleaned dataset passed validation."
            ),
            evidence={
                "semantic_mapping": state.semantic_mapping,
                "original_rows": int(df.shape[0]),
                "cleaned_rows": int(state.cleaned_df.shape[0]),
                "detected_issues": len(detected_issues or []),
                "approvals": approvals,
            },
            action=(
                "Execute permitted cleaning operations and validate "
                "the resulting dataset."
            ),
            result={
                "status": state.cleaning_status,
                "cleaned_rows": int(state.cleaned_df.shape[0]),
                "execution_logs": len(
                    state.cleaning_result.get("execution_logs", [])
                ),
            },
            validation_status=validation_result.get(
                "overall_status",
                "UNKNOWN",
            ),
        )

    except Exception as exc:
        state.cleaning_status = "failed"

        state.set_agent_status(
            "Data Cleaning Agent",
            "failed",
        )

        state.add_error(
            f"Data Cleaning Agent failed: {exc}"
        )

    return state


# =====================================================================
# RESUME WORKFLOW AFTER HUMAN APPROVAL
# =====================================================================

def resume_workflow_after_cleaning(
    state: WorkflowState,
    approvals: Dict[str, str],
    horizon: int = 7,
    test_size: int = 30,
    moving_average_window: int = 7,
    frequency: Optional[str] = None,
    minimum_confidence: float = 0.80,
) -> WorkflowState:
    """
    Resume the workflow after the user has approved or skipped
    Data Cleaning decisions.
    """

    if not isinstance(state, WorkflowState):
        raise TypeError("state must be a WorkflowState instance.")

    if not isinstance(approvals, dict):
        raise TypeError("approvals must be a dictionary.")

    # Validate workflow state
    if state.planner_status != "completed":
        state.add_error(
            "Workflow cannot resume because Planner Agent has not completed."
        )
        state.workflow_status = "failed"
        return state

    if state.cleaning_status not in (
        "awaiting_approval",
        "approval_processed",
        "validated",
    ):
        state.add_error(
            "Workflow cannot resume because the Data Cleaning stage "
            "is not waiting for approval."
        )
        state.workflow_status = "failed"
        return state

    try:
        original_df = state.df

        if original_df is None or original_df.empty:
            raise ValueError("Original workflow dataset is empty.")

        agent = CleaningAgent(
            df=original_df.copy(),
            semantic_mapping=state.semantic_mapping,
        )

        # 1. Detect issues and generate cleaning decisions.
        agent.detect()
        agent.create_decisions()

        # 2. Preserve IQR boundaries from detected issues.
        detected_issues = agent.get_detected_issues()
        decisions = agent.get_cleaning_decisions()

        issue_lookup = {
            issue["issue_id"]: issue
            for issue in (detected_issues or [])
            if isinstance(issue, dict) and issue.get("issue_id")
        }

        for decision in decisions or []:
            if isinstance(decision, dict):
                issue_id = decision.get("issue_id")
            else:
                issue_id = getattr(decision, "issue_id", None)

            issue = issue_lookup.get(issue_id)
            if not issue:
                continue

            for field in ("lower_bound", "upper_bound"):
                detected_value = issue.get(field)
                if detected_value is None:
                    continue

                if isinstance(decision, dict):
                    if decision.get(field) is None:
                        decision[field] = detected_value
                elif getattr(decision, field, None) is None:
                    setattr(decision, field, detected_value)

        # 3. Apply approvals and execute permitted actions.
        agent.execute(approvals=approvals)

        # 4. Run validation explicitly.
        validation_result = agent.validate()

        # 5. Store validation and cleaning outputs.
        state.cleaning_validation = validation_result
        state.cleaning_decision = agent.get_cleaning_decisions()
        state.cleaned_df = agent.get_cleaned_data()
        state.cleaning_result = agent.get_result()

        # Debug: display actual cleaning execution logs in the terminal.
        print("\\n========== CLEANING EXECUTION LOGS ==========")
        execution_logs = state.cleaning_result.get("execution_logs", [])

        if execution_logs:
            for log in execution_logs:
                print(log)
        else:
            print("No execution logs found.")

        print("=============================================\\n")

        state.cleaning_status = state.cleaning_result.get(
            "status",
            "unknown",
        )

        # Cleaning validation gate.
        if not isinstance(validation_result, dict):
            state.cleaning_status = "validation_failed"
            state.set_agent_status("Data Cleaning Agent", "failed")
            state.add_error(
                "Cleaning validation did not return a valid result dictionary."
            )
            return state

        if not _status_passed(validation_result):
            state.cleaning_status = "validation_failed"
            state.set_agent_status("Data Cleaning Agent", "failed")
            state.add_error(
                "Data Cleaning Agent validation failed after human approval. "
                f"Validation details: {validation_result}"
            )
            return state

        # Cleaning validation succeeded.
        state.cleaning_status = "validated"
        state.set_agent_status("Data Cleaning Agent", "validated")

        _append_stage_trace(
            state=state,
            agent="Data Cleaning Agent",
            decision="Resume After Human Approval",
            reason=(
                "The user explicitly approved or skipped the proposed "
                "cleaning actions."
            ),
            evidence={
                "approvals": approvals,
                "original_rows": int(original_df.shape[0]),
                "cleaned_rows": int(state.cleaned_df.shape[0]),
                "detected_issues": len(
                    state.cleaning_result.get("detected_issues", [])
                ),
            },
            action=(
                "Execute approved cleaning actions, preserve skipped actions, "
                "and validate the cleaned dataset."
            ),
            result={
                "status": state.cleaning_status,
                "cleaned_rows": int(state.cleaned_df.shape[0]),
                "execution_logs": len(
                    state.cleaning_result.get("execution_logs", [])
                ),
            },
            validation_status=validation_result.get(
                "overall_status",
                "UNKNOWN",
            ),
        )

    except Exception as exc:
        state.cleaning_status = "failed"
        state.set_agent_status("Data Cleaning Agent", "failed")
        state.add_error(f"Failed to resume Data Cleaning Agent: {exc}")
        return state

    # EDA
    state = eda_node(state)
    if state.eda_status not in ("completed", "completed_with_warnings"):
        return finalize_workflow(state)

    # Visualization
    state = visualization_node(state)
    if state.visualization_status not in (
        "completed",
        "completed_with_warnings",
    ):
        return finalize_workflow(state)

    # Forecasting
    state = run_forecasting_stage(
        state=state,
        horizon=horizon,
        test_size=test_size,
        moving_average_window=moving_average_window,
        frequency=frequency,
    )
    if state.forecasting_status == "failed":
        return finalize_workflow(state)

    # Insight
    state = run_insight_stage(
        state=state,
        minimum_confidence=minimum_confidence,
    )
    if state.insight_status != "completed":
        return finalize_workflow(state)

    # Recommendation
    state = run_recommendation_stage(state=state)
    if state.recommendation_status != "completed":
        return finalize_workflow(state)

    # Report
    state = run_report_stage(state=state)
    if state.report_status != "completed":
        return finalize_workflow(state)

    return finalize_workflow(state)


def eda_node(
    state: WorkflowState,
    top_n: int = 10,
) -> WorkflowState:
    """
    Execute the EDA Agent on the latest validated dataset.
    """

    state.current_stage = "eda"

    state.set_agent_status(
        "EDA Agent",
        "running",
    )

    try:

        df = state.get_analysis_df()

        if df is None or df.empty:
            raise ValueError(
                "EDA Agent cannot process an empty dataset."
            )

        if state.cleaning_validation is not None:

            if not _status_passed(
                state.cleaning_validation
            ):

                raise RuntimeError(
                    "EDA Agent requires passed cleaning validation."
                )

        agent = EDAAgent(
            df=df,
            semantic_mapping=state.semantic_mapping,
            cleaning_validation=state.cleaning_validation,
        )

        result = agent.run(
            top_n=top_n
        )

        if not isinstance(result, dict):
            raise TypeError(
                "EDA Agent must return a dictionary."
            )

        state.eda_result = result

        # -------------------------------------------------------------
        # Support current and legacy key names
        # -------------------------------------------------------------

        kpis = result.get(
            "kpis"
        )

        trends = result.get(
            "trends"
        )

        rankings = result.get(
            "rankings"
        )

        if kpis is None:
            kpis = result.get(
                "kpi_results"
            )

        if trends is None:
            trends = result.get(
                "trend_results"
            )

        if rankings is None:
            rankings = result.get(
                "ranking_results"
            )

        state.eda_result["kpi_results"] = kpis
        state.eda_result["trend_results"] = trends
        state.eda_result["ranking_results"] = rankings

        state.eda_validation = result.get(
            "validation",
            {},
        )

        state.eda_status = result.get(
            "status",
            "unknown",
        )

        if state.eda_status not in (
            "completed",
            "completed_with_warnings",
        ):

            state.set_agent_status(
                "EDA Agent",
                "failed",
            )

            state.add_error(
                "EDA Agent did not complete successfully."
            )

            return state

        if not _status_passed(
            state.eda_validation
        ):

            state.set_agent_status(
                "EDA Agent",
                "failed",
            )

            state.add_error(
                "EDA Agent validation failed."
            )

            return state

        state.set_agent_status(
            "EDA Agent",
            "completed",
        )

        _append_stage_trace(
            state=state,
            agent="EDA Agent",
            decision="Execute EDA Agent",
            reason=(
                "Validated cleaned data is available for "
                "deterministic exploratory analysis."
            ),
            evidence={
                "cleaning_validation": state.cleaning_validation,
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
            },
            action=(
                "Calculate KPIs, trends and business rankings "
                "using deterministic analytical modules."
            ),
            result={
                "status": state.eda_status,
                "kpis_available": bool(kpis),
                "trends_available": bool(trends),
                "rankings_available": bool(rankings),
            },
            validation_status=(
                state.eda_validation.get(
                    "overall_status",
                    "UNKNOWN",
                )
            ),
        )

    except Exception as exc:

        state.eda_status = "failed"

        state.set_agent_status(
            "EDA Agent",
            "failed",
        )

        state.add_error(
            f"EDA Agent failed: {exc}"
        )

    return state


# =====================================================================
# VISUALIZATION NODE
# =====================================================================

def visualization_node(
    state: WorkflowState,
    output_dir: str = "outputs/visualizations",
) -> WorkflowState:
    """
    Execute the Visualization Agent using validated EDA results.
    """

    state.current_stage = "visualization"

    state.set_agent_status(
        "Visualization Agent",
        "running",
    )

    try:

        if state.eda_result is None:
            raise RuntimeError(
                "Visualization Agent requires EDA results."
            )

        if not _status_passed(
            state.eda_validation
        ):

            raise RuntimeError(
                "Visualization Agent requires passed EDA validation."
            )

        agent = VisualizationAgent(
            eda_result=state.eda_result,
            output_dir=output_dir,
        )

        result = agent.run()

        if not isinstance(result, dict):
            raise TypeError(
                "Visualization Agent must return a dictionary."
            )

        state.visualization_result = result

        state.visualization_validation = result.get(
            "validation",
            {},
        )

        state.visualization_status = result.get(
            "status",
            "unknown",
        )

        if state.visualization_status not in (
            "completed",
            "completed_with_warnings",
        ):

            state.set_agent_status(
                "Visualization Agent",
                "failed",
            )

            state.add_error(
                "Visualization Agent did not complete successfully."
            )

            return state

        if not _status_passed(
            state.visualization_validation
        ):

            state.set_agent_status(
                "Visualization Agent",
                "failed",
            )

            state.add_error(
                "Visualization Agent validation failed."
            )

            return state

        state.set_agent_status(
            "Visualization Agent",
            "completed",
        )

        _append_stage_trace(
            state=state,
            agent="Visualization Agent",
            decision="Execute Visualization Agent",
            reason=(
                "Validated EDA results are available for "
                "data-driven visualization selection."
            ),
            evidence={
                "eda_validation": state.eda_validation,
                "eda_available": state.eda_result is not None,
            },
            action=(
                "Select appropriate visualizations and generate "
                "validated charts from EDA results."
            ),
            result={
                "status": state.visualization_status,
                "total_charts": result.get(
                    "total_charts",
                    len(
                        result.get(
                            "charts",
                            [],
                        )
                    ),
                ),
            },
            validation_status=(
                state.visualization_validation.get(
                    "overall_status",
                    "UNKNOWN",
                )
            ),
        )

    except Exception as exc:

        state.visualization_status = "failed"

        state.set_agent_status(
            "Visualization Agent",
            "failed",
        )

        state.add_error(
            f"Visualization Agent failed: {exc}"
        )

    return state


# =====================================================================
# FORECASTING NODE
# =====================================================================

def forecasting_node(
    state: WorkflowState,
    horizon: int = 7,
    test_size: int = 30,
    moving_average_window: int = 7,
    frequency: Optional[str] = None,
) -> WorkflowState:
    """
    Execute the Forecasting Agent.

    Forecasting is conditionally routed by Planner mapping.
    """

    state.current_stage = "forecasting"

    route = route_forecasting(
        state
    )

    # -------------------------------------------------------------
    # Forecasting skipped
    # -------------------------------------------------------------

    if route != RUN_FORECASTING:

        state.forecasting_status = "skipped"

        state.set_agent_status(
            "Forecasting Agent",
            "skipped",
        )

        state.forecasting_decision = (
            "SKIP_FORECASTING"
        )

        state.add_warning(
            "Forecasting was skipped because "
            "forecasting prerequisites were not satisfied."
        )

        _append_stage_trace(
            state=state,
            agent="Forecasting Agent",
            decision="Skip Forecasting Agent",
            reason=(
                "Forecasting routing determined that the "
                "required forecasting conditions were not satisfied."
            ),
            evidence={
                "semantic_mapping": state.semantic_mapping,
                "capabilities": state.capabilities,
            },
            action=(
                "Do not execute forecasting models."
            ),
            result={
                "status": "skipped",
            },
            validation_status="NOT_APPLICABLE",
        )

        return state

    state.set_agent_status(
        "Forecasting Agent",
        "running",
    )

    try:

        df = state.get_analysis_df()

        if df is None or df.empty:
            raise ValueError(
                "Forecasting Agent cannot process an empty dataset."
            )

        agent = ForecastingAgent(
            horizon=horizon,
            test_size=test_size,
            moving_average_window=moving_average_window,
        )

        result = agent.run(
            df=df,
            semantic_mapping=state.semantic_mapping,
        )

        state.forecasting_result = result.to_dict()

        state.forecasting_status = result.status

        if result.status == "completed":

            state.forecasting_decision = (
                "RUN_FORECASTING"
            )

            state.set_agent_status(
                "Forecasting Agent",
                "completed",
            )

            validation = (
                state.forecasting_result.get(
                    "validation",
                    {},
                )
            )

            _append_stage_trace(
                state=state,
                agent="Forecasting Agent",
                decision="Execute Forecasting Agent",
                reason=(
                    "Date and sales mappings are available and "
                    "forecasting routing selected execution."
                ),
                evidence={
                    "date_mapping": state.semantic_mapping.get(
                        "date"
                    ),
                    "sales_mapping": state.semantic_mapping.get(
                        "sales"
                    ),
                },
                action=(
                    "Evaluate forecasting models using "
                    "chronological validation."
                ),
                result={
                    "status": "completed",
                    "best_model": state.forecasting_result.get(
                        "best_model"
                    ),
                    "best_mae": state.forecasting_result.get(
                        "best_mae"
                    ),
                },
                validation_status=validation.get(
                    "overall_status",
                    "UNKNOWN",
                ),
            )

        elif result.status == "not_eligible":

            state.forecasting_status = "skipped"

            state.set_agent_status(
                "Forecasting Agent",
                "skipped",
            )

            state.add_warning(
                result.message
            )

            _append_stage_trace(
                state=state,
                agent="Forecasting Agent",
                decision="Skip Forecasting Agent",
                reason=(
                    "Forecasting Agent determined that the "
                    "dataset was not eligible."
                ),
                evidence={
                    "eligibility": state.forecasting_result.get(
                        "eligibility"
                    ),
                },
                action=(
                    "Do not generate a forecast for this dataset."
                ),
                result={
                    "status": "not_eligible",
                    "message": result.message,
                },
                validation_status="NOT_APPLICABLE",
            )

        else:

            state.forecasting_status = "failed"

            state.set_agent_status(
                "Forecasting Agent",
                "failed",
            )

            state.add_error(
                result.message
            )

    except Exception as exc:

        state.forecasting_status = "failed"

        state.set_agent_status(
            "Forecasting Agent",
            "failed",
        )

        state.add_error(
            f"Forecasting Agent failed: {exc}"
        )

    return state


# =====================================================================
# INSIGHT NODE
# =====================================================================

def insight_node(
    state: WorkflowState,
    minimum_confidence: float = 0.80,
) -> WorkflowState:
    """
    Execute the Insight Agent using validated EDA evidence.
    """

    state.current_stage = "insight"

    route = route_insight(
        state
    )

    if route != RUN_INSIGHT:

        state.insight_status = "failed"

        state.set_agent_status(
            "Insight Agent",
            "failed",
        )

        state.add_error(
            "Insight Agent routing did not permit execution."
        )

        return state

    state.set_agent_status(
        "Insight Agent",
        "running",
    )

    if state.eda_result is None:

        state.insight_status = "failed"

        state.set_agent_status(
            "Insight Agent",
            "failed",
        )

        state.add_error(
            "Insight Agent requires EDA results."
        )

        return state

    try:

        eda_result = state.eda_result

        kpi_results = eda_result.get(
            "kpi_results"
        )

        if kpi_results is None:
            kpi_results = eda_result.get(
                "kpis"
            )

        trend_results = eda_result.get(
            "trend_results"
        )

        if trend_results is None:
            trend_results = eda_result.get(
                "trends"
            )

        ranking_results = eda_result.get(
            "ranking_results"
        )

        if ranking_results is None:
            ranking_results = eda_result.get(
                "rankings"
            )

        forecasting_validation = None

        if isinstance(
            state.forecasting_result,
            dict,
        ):

            forecasting_validation = (
                state.forecasting_result.get(
                    "validation"
                )
            )

        agent = InsightAgent(
            minimum_confidence=minimum_confidence
        )

        result = agent.run(
            kpi_results=kpi_results,
            trend_results=trend_results,
            ranking_results=ranking_results,
            forecasting_result=state.forecasting_result,
            eda_validation=state.eda_validation,
            forecasting_validation=forecasting_validation,
        )

        state.insight_result = result.to_dict()

        state.insight_status = result.status

        state.insight_validation = result.validation

        state.agent_status[
            "Insight Agent"
        ] = result.status

        if result.status != "completed":

            state.add_error(
                "Insight Agent did not complete successfully."
            )

            return state

        if not _status_passed(
            state.insight_validation
        ):

            state.set_agent_status(
                "Insight Agent",
                "failed",
            )

            state.add_error(
                "Insight Agent validation failed."
            )

            return state

        state.set_agent_status(
            "Insight Agent",
            "completed",
        )

        _append_stage_trace(
            state=state,
            agent="Insight Agent",
            decision="Execute Insight Agent",
            reason=(
                "Validated EDA results are available and "
                "Insight routing selected execution."
            ),
            evidence={
                "validated_eda": True,
                "forecasting_available": (
                    state.forecasting_result is not None
                ),
            },
            action=(
                "Generate grounded insights from validated "
                "analytical and forecasting evidence."
            ),
            result={
                "status": result.status,
                "total_insights": result.total_insights,
            },
            validation_status=(
                result.validation.get(
                    "overall_status",
                    "UNKNOWN",
                )
            ),
        )

    except Exception as exc:

        state.insight_status = "failed"

        state.set_agent_status(
            "Insight Agent",
            "failed",
        )

        state.add_error(
            f"Insight Agent failed: {exc}"
        )

    return state


# =====================================================================
# RECOMMENDATION NODE
# =====================================================================
#######

# =====================================================================
# RECOMMENDATION NODE
# =====================================================================

def recommendation_node(
    state: WorkflowState,
) -> WorkflowState:
    """
    Execute the Recommendation Agent.
    """

    state.current_stage = "recommendation"

    route = route_recommendation(state)

    if route != RUN_RECOMMENDATION:
        state.recommendation_status = "failed"
        state.set_agent_status(
            "Recommendation Agent",
            "failed",
        )
        state.add_error(
            "Recommendation Agent routing did not permit execution."
        )
        return state

    state.set_agent_status(
        "Recommendation Agent",
        "running",
    )

    if state.insight_result is None:
        state.recommendation_status = "failed"
        state.set_agent_status(
            "Recommendation Agent",
            "failed",
        )
        state.add_error(
            "Recommendation Agent requires Insight Agent results."
        )
        return state

    try:
        insights = state.insight_result.get(
            "insights",
            [],
        )

        if not isinstance(insights, list):
            raise TypeError(
                "Insight Agent result must contain an 'insights' list."
            )

        if not insights:
            raise ValueError(
                "Recommendation Agent requires at least one insight."
            )

        # Get the latest analysed DataFrame for cache identity.
        analysis_df = state.get_analysis_df()

        # Create the Recommendation Agent with cache support.
        agent = RecommendationAgent(
            insights=insights,
            insight_validation=state.insight_validation,
            forecast_result=state.forecasting_result,
            analysis_df=analysis_df,
        )

        # Execute the Recommendation Agent.
        result = agent.run()

        # Store the result in workflow state.
        state.recommendation_result = result.to_dict()

        state.recommendation_status = result.status

        state.recommendation_validation = (
            result.recommendation_validation
        )

        state.agent_status[
            "Recommendation Agent"
        ] = result.status

        if result.status != "completed":
            state.add_error(
                "Recommendation Agent did not complete successfully."
            )
            return state

        # Require successful recommendation validation.
        if not _status_passed(
            state.recommendation_validation
        ):
            state.set_agent_status(
                "Recommendation Agent",
                "failed",
            )

            state.add_error(
                "Recommendation Agent validation failed."
            )
            return state

        state.set_agent_status(
            "Recommendation Agent",
            "completed",
        )

        # Record the workflow decision trace.
        _append_stage_trace(
            state=state,
            agent="Recommendation Agent",
            decision="Execute Recommendation Agent",
            reason=(
                "Validated grounded insights are available "
                "for evidence-based recommendations."
            ),
            evidence={
                "insight_validation": state.insight_validation,
                "total_insights": len(insights),
            },
            action=(
                "Generate evidence-based recommendations "
                "with limitations and validation."
            ),
            result={
                "status": result.status,
                "total_recommendations": (
                    result.total_recommendations
                ),
            },
            validation_status=(
                result.recommendation_validation.get(
                    "overall_status",
                    "UNKNOWN",
                )
            ),
        )

    except Exception as exc:
        state.recommendation_status = "failed"

        state.set_agent_status(
            "Recommendation Agent",
            "failed",
        )

        state.add_error(
            f"Recommendation Agent failed: {exc}"
        )

    return state


# =====================================================================
# REPORT NODE
# =====================================================================

def report_node(
    state: WorkflowState,
) -> WorkflowState:
    """
    Execute the Report Agent.

    Report generation is the final analytical stage.
    """

    state.current_stage = "report"

    state.set_agent_status(
        "Report Agent",
        "running",
    )

    # -------------------------------------------------------------
    # Preconditions
    # -------------------------------------------------------------

    if state.eda_result is None:

        state.report_status = "failed"

        state.set_agent_status(
            "Report Agent",
            "failed",
        )

        state.add_error(
            "Report Agent requires EDA results."
        )

        return state

    if state.visualization_result is None:

        state.report_status = "failed"

        state.set_agent_status(
            "Report Agent",
            "failed",
        )

        state.add_error(
            "Report Agent requires Visualization results."
        )

        return state

    if state.insight_result is None:

        state.report_status = "failed"

        state.set_agent_status(
            "Report Agent",
            "failed",
        )

        state.add_error(
            "Report Agent requires Insight results."
        )

        return state

    if state.recommendation_result is None:

        state.report_status = "failed"

        state.set_agent_status(
            "Report Agent",
            "failed",
        )

        state.add_error(
            "Report Agent requires Recommendation results."
        )

        return state

    # -------------------------------------------------------------
    # Validation gates
    # -------------------------------------------------------------

    required_validations = {
        "EDA Agent": state.eda_validation,
        "Visualization Agent": state.visualization_validation,
        "Insight Agent": state.insight_validation,
        "Recommendation Agent": state.recommendation_validation,
    }

    for agent_name, validation in (
        required_validations.items()
    ):

        if not _status_passed(
            validation
        ):

            state.report_status = "failed"

            state.set_agent_status(
                "Report Agent",
                "failed",
            )

            state.add_error(
                f"Report Agent requires passed validation from "
                f"{agent_name}."
            )

            return state

    try:

        agent = ReportAgent(
            eda_result=state.eda_result,
            visualization_result=state.visualization_result,
            forecasting_result=state.forecasting_result,
            insight_result=state.insight_result,
            recommendation_result=(
                state.recommendation_result
            ),
            semantic_mapping=state.semantic_mapping,
            capabilities=state.capabilities,
            cleaning_result=state.cleaning_result,
            cleaning_validation=state.cleaning_validation,
            eda_validation=state.eda_validation,
            visualization_validation=(
                state.visualization_validation
            ),
            insight_validation=state.insight_validation,
            recommendation_validation=(
                state.recommendation_validation
            ),
        )

        result = agent.run()

        if hasattr(
            result,
            "to_dict",
        ):

            report_result = result.to_dict()

        else:

            report_result = result

        if not isinstance(
            report_result,
            dict,
        ):

            raise TypeError(
                "Report Agent must return a dictionary-compatible result."
            )

        state.report_result = report_result

        state.report_validation = report_result.get(
            "report_validation",
            report_result.get(
                "validation",
                {},
            ),
        )

        state.report_status = report_result.get(
            "status",
            "unknown",
        )

        if state.report_status != "completed":

            state.set_agent_status(
                "Report Agent",
                "failed",
            )

            state.add_error(
                "Report Agent did not complete successfully."
            )

            return state

        if not _status_passed(
            state.report_validation
        ):

            state.set_agent_status(
                "Report Agent",
                "failed",
            )

            state.add_error(
                "Report Agent validation failed."
            )

            return state

        state.set_agent_status(
            "Report Agent",
            "completed",
        )

        _append_stage_trace(
            state=state,
            agent="Report Agent",
            decision="Execute Report Agent",
            reason=(
                "All required upstream analytical outputs and "
                "validation gates have passed."
            ),
            evidence={
                "eda_validated": True,
                "visualization_validated": True,
                "insight_validated": True,
                "recommendation_validated": True,
                "forecast_available": (
                    state.forecasting_result is not None
                ),
            },
            action=(
                "Consolidate validated analytical results, "
                "insights and recommendations into the final report."
            ),
            result={
                "status": state.report_status,
                "total_sections": report_result.get(
                    "total_sections",
                    len(
                        report_result.get(
                            "report",
                            {},
                        ).get(
                            "sections",
                            [],
                        )
                    )
                    if isinstance(
                        report_result.get(
                            "report"
                        ),
                        dict,
                    )
                    else 0,
                ),
            },
            validation_status=(
                state.report_validation.get(
                    "overall_status",
                    "UNKNOWN",
                )
            ),
        )

    except Exception as exc:

        state.report_status = "failed"

        state.set_agent_status(
            "Report Agent",
            "failed",
        )

        state.add_error(
            f"Report Agent failed: {exc}"
        )

    return state


# =====================================================================
# STAGE ROUTER FUNCTIONS
# =====================================================================

def run_forecasting_stage(
    state: WorkflowState,
    horizon: int = 7,
    test_size: int = 30,
    moving_average_window: int = 7,
    frequency: Optional[str] = None,
) -> WorkflowState:
    """
    Route and execute the Forecasting Agent.
    """

    return forecasting_node(
        state=state,
        horizon=horizon,
        test_size=test_size,
        moving_average_window=moving_average_window,
        frequency=frequency,
    )


def run_insight_stage(
    state: WorkflowState,
    minimum_confidence: float = 0.80,
) -> WorkflowState:
    """
    Route and execute the Insight Agent.
    """

    return insight_node(
        state=state,
        minimum_confidence=minimum_confidence,
    )


def run_recommendation_stage(
    state: WorkflowState,
) -> WorkflowState:
    """
    Route and execute the Recommendation Agent.
    """

    return recommendation_node(
        state
    )


def run_report_stage(
    state: WorkflowState,
) -> WorkflowState:
    """
    Execute the Report Agent stage.
    """

    return report_node(
        state
    )


# =====================================================================
# FINAL WORKFLOW VALIDATION
# =====================================================================

def finalize_workflow(
    state: WorkflowState,
) -> WorkflowState:
    """
    Final workflow gate.

    Successful completion requires:

    - no errors
    - Planner completed
    - Cleaning validated
    - EDA completed
    - Visualization completed
    - Forecasting completed or skipped
    - Insight completed
    - Recommendation completed
    - Report completed
    - all required validations passed
    """

    # -------------------------------------------------------------
    # IMPORTANT:
    # Awaiting human approval is NOT a workflow failure.
    # -------------------------------------------------------------

    if state.cleaning_status == "awaiting_approval":

        state.current_stage = "cleaning"

        state.workflow_status = "awaiting_approval"

        return state

    # -------------------------------------------------------------
    # Existing errors
    # -------------------------------------------------------------

    if state.errors:

        state.workflow_status = "failed"

        return state

    # -------------------------------------------------------------
    # Required agent states
    # -------------------------------------------------------------

    required_statuses = {
        "Planner Agent": "completed",
        "Data Cleaning Agent": "validated",
        "EDA Agent": "completed",
        "Visualization Agent": "completed",
        "Insight Agent": "completed",
        "Recommendation Agent": "completed",
        "Report Agent": "completed",
    }

    for agent_name, expected_status in (
        required_statuses.items()
    ):

        actual_status = state.agent_status.get(
            agent_name
        )

        if actual_status != expected_status:

            state.workflow_status = "failed"

            state.add_error(
                f"{agent_name} did not reach required status "
                f"'{expected_status}'. Actual status: "
                f"'{actual_status}'."
            )

            return state

    # -------------------------------------------------------------
    # Forecasting can be completed or skipped.
    # -------------------------------------------------------------

    if state.agent_status.get(
        "Forecasting Agent"
    ) not in (
        "completed",
        "skipped",
    ):

        state.workflow_status = "failed"

        state.add_error(
            "Forecasting Agent did not complete or skip successfully."
        )

        return state

    # -------------------------------------------------------------
    # Validation gates
    # -------------------------------------------------------------

    validations = {
        "Cleaning": state.cleaning_validation,
        "EDA": state.eda_validation,
        "Visualization": state.visualization_validation,
        "Insight": state.insight_validation,
        "Recommendation": state.recommendation_validation,
        "Report": state.report_validation,
    }

    for stage_name, validation in (
        validations.items()
    ):

        if not _status_passed(
            validation
        ):

            state.workflow_status = "failed"

            state.add_error(
                f"{stage_name} validation did not pass."
            )

            return state

    # -------------------------------------------------------------
    # Final state
    # -------------------------------------------------------------

    state.current_stage = "report"

    state.workflow_status = "completed"

    return state


# =====================================================================
# COMPLETE EIGHT-AGENT WORKFLOW
# =====================================================================

def run_workflow(
    df: pd.DataFrame,
    semantic_mapping: Optional[
        Dict[str, Any]
    ] = None,
    capabilities: Optional[
        Dict[str, Any]
    ] = None,
    planner_result: Optional[
        Dict[str, Any]
    ] = None,
    eda_result: Optional[
        Dict[str, Any]
    ] = None,
    eda_validation: Optional[
        Dict[str, Any]
    ] = None,
    horizon: int = 7,
    test_size: int = 30,
    moving_average_window: int = 7,
    frequency: Optional[str] = None,
    minimum_confidence: float = 0.80,
    approvals: Optional[Dict[str, str]] = None,
) -> WorkflowState:
    """
    Execute the complete eight-agent workflow.

    IMPORTANT:

    When approvals=None, the workflow intentionally stops after
    the Cleaning Agent creates its cleaning decisions.

    This allows Streamlit to display:

        Issue
        Column
        Risk
        Affected Rows
        Recommendation
        Decision

    and wait for human approval.

    To execute the entire workflow programmatically:

        state = run_workflow(
            df,
            approvals={
                "OUTLIER_Total Amount": "SKIP",
                "OUTLIER_Quantity": "SKIP",
            }
        )

    For Streamlit, the recommended workflow is:

        state = run_workflow(df)

        # display state.cleaning_decision

        state = resume_workflow_after_cleaning(
            state,
            approvals
        )
    """

    # -------------------------------------------------------------
    # Initial state
    # -------------------------------------------------------------

    state = create_initial_state(
        df
    )

    # -------------------------------------------------------------
    # Optional compatibility context
    # -------------------------------------------------------------

    if semantic_mapping is not None:

        state.semantic_mapping = (
            semantic_mapping
        )

    if capabilities is not None:

        state.capabilities = (
            capabilities
        )

    # =================================================================
    # 1. PLANNER
    # =================================================================

    if planner_result is not None:

        state.planner_result = (
            planner_result
        )

        state.semantic_mapping = (
            planner_result.get(
                "semantic_mapping",
                state.semantic_mapping,
            )
        )

        state.capabilities = (
            planner_result.get(
                "capabilities",
                state.capabilities,
            )
        )

        state.execution_plan = (
            planner_result.get(
                "analysis_plan",
                planner_result.get(
                    "execution_plan",
                    [],
                ),
            )
        )

        state.planner_status = planner_result.get(
            "status",
            "completed",
        )

        state.set_agent_status(
            "Planner Agent",
            state.planner_status,
        )

    else:

        state = planner_node(
            state
        )

    if state.planner_status != "completed":

        return finalize_workflow(
            state
        )

    # =================================================================
    # 2. DATA CLEANING
    # =================================================================

    state = cleaning_node(
        state,
        approvals=approvals,
    )

    # -------------------------------------------------------------
    # IMPORTANT:
    # Stop here until Streamlit provides human approval.
    # -------------------------------------------------------------

    if state.cleaning_status == "awaiting_approval":

        state.workflow_status = "awaiting_approval"

        return state

    if state.cleaning_status in (
        "failed",
        "validation_failed",
    ):

        return finalize_workflow(
            state
        )

    # =================================================================
    # 3. EDA
    # =================================================================

    if eda_result is not None:

        state.eda_result = eda_result

        state.eda_validation = (
            eda_validation
            if eda_validation is not None
            else eda_result.get(
                "validation",
                {},
            )
        )

        state.eda_result["kpi_results"] = (
            state.eda_result.get(
                "kpi_results",
                state.eda_result.get(
                    "kpis"
                ),
            )
        )

        state.eda_result["trend_results"] = (
            state.eda_result.get(
                "trend_results",
                state.eda_result.get(
                    "trends"
                ),
            )
        )

        state.eda_result["ranking_results"] = (
            state.eda_result.get(
                "ranking_results",
                state.eda_result.get(
                    "rankings"
                ),
            )
        )

        state.eda_status = eda_result.get(
            "status",
            "completed",
        )

        state.set_agent_status(
            "EDA Agent",
            "completed",
        )

    else:

        state = eda_node(
            state
        )

    if state.eda_status not in (
        "completed",
        "completed_with_warnings",
    ):

        return finalize_workflow(
            state
        )

    # =================================================================
    # 4. VISUALIZATION
    # =================================================================

    state = visualization_node(
        state
    )

    if state.visualization_status not in (
        "completed",
        "completed_with_warnings",
    ):

        return finalize_workflow(
            state
        )

    # =================================================================
    # 5. FORECASTING
    # =================================================================

    state = run_forecasting_stage(
        state=state,
        horizon=horizon,
        test_size=test_size,
        moving_average_window=moving_average_window,
        frequency=frequency,
    )

    if state.forecasting_status == "failed":

        return finalize_workflow(
            state
        )

    # =================================================================
    # 6. INSIGHT
    # =================================================================

    state = run_insight_stage(
        state=state,
        minimum_confidence=minimum_confidence,
    )

    if state.insight_status != "completed":

        return finalize_workflow(
            state
        )

    # =================================================================
    # 7. RECOMMENDATION
    # =================================================================

    state = run_recommendation_stage(
        state=state
    )

    if state.recommendation_status != "completed":

        return finalize_workflow(
            state
        )

    # =================================================================
    # 8. REPORT
    # =================================================================

    state = run_report_stage(
        state=state
    )

    if state.report_status != "completed":

        return finalize_workflow(
            state
        )

    # =================================================================
    # FINAL VALIDATION
    # =================================================================

    state = finalize_workflow(
        state
    )

    return state


# =====================================================================
# SERIALIZATION
# =====================================================================

def serialize_workflow_state(
    state: WorkflowState,
) -> Dict[str, Any]:
    """
    Serialize the complete workflow state.
    """

    return state.to_dict()
