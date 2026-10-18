"""
Workflow routing logic.

Controls which agents/stages should execute based on
available validated state and capabilities.

The project contains exactly 8 agents.
"""

from __future__ import annotations

from typing import Any

from workflow.state import WorkflowState


# =====================================================================
# ROUTING CONSTANTS
# =====================================================================

RUN_FORECASTING = "RUN_FORECASTING"
SKIP_FORECASTING = "SKIP_FORECASTING"

RUN_INSIGHT = "RUN_INSIGHT"
SKIP_INSIGHT = "SKIP_INSIGHT"

RUN_RECOMMENDATION = "RUN_RECOMMENDATION"
SKIP_RECOMMENDATION = "SKIP_RECOMMENDATION"


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def _mapping_exists(
    state: WorkflowState,
    semantic_key: str,
) -> bool:
    """
    Check whether a semantic mapping exists and contains a column.
    """

    mapping = state.semantic_mapping.get(semantic_key)

    if not isinstance(mapping, dict):
        return False

    column = mapping.get("column")

    if not column:
        return False

    return True


# =====================================================================
# FORECASTING ROUTING
# =====================================================================

def should_run_forecasting(
    state: WorkflowState,
) -> bool:
    """
    Determine whether the Forecasting Agent should run.
    """

    if not state.capabilities.get("forecasting", False):
        return False

    if not _mapping_exists(state, "date"):
        return False

    if not _mapping_exists(state, "sales"):
        return False

    return True


def get_forecasting_route(
    state: WorkflowState,
) -> str:
    """
    Return the forecasting routing decision.
    """

    if should_run_forecasting(state):
        return RUN_FORECASTING

    return SKIP_FORECASTING


def route_forecasting(
    state: WorkflowState,
) -> str:
    """
    Apply forecasting routing decision to workflow state.
    """

    route = get_forecasting_route(state)

    if route == RUN_FORECASTING:
        state.forecasting_status = "pending"
        state.forecasting_decision = route

        state.add_decision_trace(
            agent="Forecasting Agent",
            decision=route,
            reason=(
                "Forecasting capability is available and "
                "valid date and sales mappings are present."
            ),
            evidence={
                "forecasting_capability": True,
                "date_mapping_available": True,
                "sales_mapping_available": True,
            },
            action="Run Forecasting Agent",
            result="Forecasting Agent scheduled for execution.",
            validation_status="PENDING",
        )

    else:
        state.forecasting_status = "skipped"
        state.forecasting_decision = route

        state.add_decision_trace(
            agent="Forecasting Agent",
            decision=route,
            reason=(
                "Forecasting prerequisites or capability "
                "requirements are not satisfied."
            ),
            evidence={
                "forecasting_capability": state.capabilities.get(
                    "forecasting",
                    False,
                ),
                "date_mapping_available": _mapping_exists(
                    state,
                    "date",
                ),
                "sales_mapping_available": _mapping_exists(
                    state,
                    "sales",
                ),
            },
            action="Skip Forecasting Agent",
            result="Forecasting Agent was not executed.",
            validation_status="NOT_APPLICABLE",
        )

    return route


# =====================================================================
# INSIGHT ROUTING
# =====================================================================

def should_run_insight(
    state: WorkflowState,
) -> bool:
    """
    Determine whether the Insight Agent should run.

    Insight generation requires validated EDA results.
    """

    if state.eda_result is None:
        return False

    if state.eda_validation is not None:
        status = state.eda_validation.get(
            "overall_status"
        )

        if str(status).upper() != "PASSED":
            return False

    return True


def get_insight_route(
    state: WorkflowState,
) -> str:
    """
    Return the Insight routing decision.
    """

    if should_run_insight(state):
        return RUN_INSIGHT

    return SKIP_INSIGHT


def route_insight(
    state: WorkflowState,
) -> str:
    """
    Apply Insight routing decision to workflow state.
    """

    route = get_insight_route(state)

    if route == RUN_INSIGHT:
        state.insight_status = "pending"
        state.insight_decision = route

        state.add_decision_trace(
            agent="Insight Agent",
            decision=route,
            reason=(
                "Validated EDA results are available "
                "for evidence-grounded insight generation."
            ),
            evidence={
                "eda_result_available": True,
                "eda_validation_status": (
                    state.eda_validation.get(
                        "overall_status"
                    )
                    if state.eda_validation
                    else "NOT_PROVIDED"
                ),
            },
            action="Run Insight Agent",
            result="Insight Agent scheduled for execution.",
            validation_status="PENDING",
        )

    else:
        state.insight_status = "skipped"
        state.insight_decision = route

        state.add_decision_trace(
            agent="Insight Agent",
            decision=route,
            reason=(
                "Validated EDA results are not available."
            ),
            evidence={
                "eda_result_available": (
                    state.eda_result is not None
                ),
                "eda_validation_status": (
                    state.eda_validation.get(
                        "overall_status"
                    )
                    if state.eda_validation
                    else None
                ),
            },
            action="Skip Insight Agent",
            result="Insight Agent was not executed.",
            validation_status="NOT_APPLICABLE",
        )

    return route


# =====================================================================
# RECOMMENDATION ROUTING
# =====================================================================

def should_run_recommendation(
    state: WorkflowState,
) -> bool:
    """
    Determine whether the Recommendation Agent should run.

    Recommendation generation requires completed, validated
    Insight Agent output.
    """

    if state.insight_result is None:
        return False

    if not isinstance(
        state.insight_result,
        dict,
    ):
        return False

    if state.insight_result.get("status") != "completed":
        return False

    insights = state.insight_result.get(
        "insights"
    )

    if not isinstance(insights, list):
        return False

    if len(insights) == 0:
        return False

    if state.insight_validation is not None:
        status = state.insight_validation.get(
            "overall_status"
        )

        if str(status).upper() != "PASSED":
            return False

    return True


def get_recommendation_route(
    state: WorkflowState,
) -> str:
    """
    Return the Recommendation routing decision.
    """

    if should_run_recommendation(state):
        return RUN_RECOMMENDATION

    return SKIP_RECOMMENDATION


def route_recommendation(
    state: WorkflowState,
) -> str:
    """
    Apply Recommendation routing decision to workflow state.
    """

    route = get_recommendation_route(state)

    if route == RUN_RECOMMENDATION:
        state.recommendation_status = "pending"
        state.recommendation_decision = route

        state.add_decision_trace(
            agent="Recommendation Agent",
            decision=route,
            reason=(
                "Completed and validated Insight Agent "
                "results containing structured insights "
                "are available."
            ),
            evidence={
                "insight_result_available": True,
                "insight_status": state.insight_result.get(
                    "status"
                ),
                "total_insights": len(
                    state.insight_result.get(
                        "insights",
                        [],
                    )
                ),
                "insight_validation_status": (
                    state.insight_validation.get(
                        "overall_status"
                    )
                    if state.insight_validation
                    else "NOT_PROVIDED"
                ),
            },
            action="Run Recommendation Agent",
            result=(
                "Recommendation Agent scheduled "
                "for execution."
            ),
            validation_status="PENDING",
        )

    else:
        state.recommendation_status = "skipped"
        state.recommendation_decision = route

        state.add_decision_trace(
            agent="Recommendation Agent",
            decision=route,
            reason=(
                "Completed and validated insights "
                "are not available."
            ),
            evidence={
                "insight_result_available": (
                    state.insight_result is not None
                ),
                "insight_status": (
                    state.insight_result.get("status")
                    if isinstance(
                        state.insight_result,
                        dict,
                    )
                    else None
                ),
                "insight_validation_status": (
                    state.insight_validation.get(
                        "overall_status"
                    )
                    if state.insight_validation
                    else None
                ),
            },
            action="Skip Recommendation Agent",
            result=(
                "Recommendation Agent was not executed."
            ),
            validation_status="NOT_APPLICABLE",
        )

    return route