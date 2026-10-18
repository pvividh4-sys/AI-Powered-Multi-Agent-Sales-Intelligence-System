"""
8.7.6 - Recommendation Agent Workflow Integration Test

This test verifies the Recommendation Agent stage independently.

The test prepares validated EDA evidence and executes the
Forecasting Agent and Insight Agent as upstream dependencies
before executing the Recommendation Agent.

The test intentionally uses run_recommendation_stage() rather
than run_workflow(), because run_workflow() now executes the
complete eight-agent workflow and therefore continues to the
Report Agent.

Complete end-to-end workflow testing is handled separately by:
test_end_to_end.py
"""



from __future__ import annotations
import gc
import tempfile
from pathlib import Path

import pandas as pd
import workflow.graph as workflow_graph

from analytics.recommendation_cache import RecommendationCache

from workflow.graph import (
    run_forecasting_stage,
    run_insight_stage,
    run_recommendation_stage,
)

from workflow.routing import (
    RUN_RECOMMENDATION,
    get_recommendation_route,
)

from workflow.state import create_initial_state


# =====================================================================
# CONFIGURATION
# =====================================================================

DATASET_PATH = Path(
    "data/sample/Retail Sales Dataset.csv"
)


SEMANTIC_MAPPING = {
    "date": {
        "column": "Date",
        "confidence": 0.95,
    },
    "sales": {
        "column": "Total Amount",
        "confidence": 0.95,
    },
    "quantity": {
        "column": "Quantity",
        "confidence": 0.95,
    },
    "product": {
        "column": "Product Category",
        "confidence": 0.95,
    },
    "customer": {
        "column": "Customer ID",
        "confidence": 0.95,
    },
    "region": {
        "column": "City",
        "confidence": 0.95,
    },
    "order_id": {
        "column": "Order ID",
        "confidence": 0.95,
    },
}


CAPABILITIES = {
    "sales_analysis": True,
    "quantity_analysis": True,
    "product_analysis": True,
    "customer_analysis": True,
    "regional_analysis": True,
    "profitability_analysis": False,
    "forecasting": True,
}


# =====================================================================
# 1. LOAD DATASET
# =====================================================================

print("=" * 70)
print(
    "8.7.6 RECOMMENDATION AGENT "
    "WORKFLOW INTEGRATION TEST"
)
print("=" * 70)


df = pd.read_csv(
    DATASET_PATH
)


print()
print(
    "Dataset Shape:",
    df.shape
)


assert not df.empty
assert df.shape == (
    1000,
    16
)


print(
    "Dataset Load: PASSED"
)


# =====================================================================
# 2. VALIDATED EDA RESULTS
# =====================================================================

eda_result = {

    "status": "completed",

    "kpi_results": {

        "total_sales": 476160.0,

        "total_quantity": 2632.0,

        "total_orders": 1000,

        "total_customers": 1000,

        "average_order_value": 476.16,

        "average_quantity_per_order": 2.632,

        "average_selling_price":
            180.91185410334347,
    },


    "trend_results": {

        "monthly_sales": [

            {
                "Date": "2023-01",
                "Total Amount": 38630,
            },

            {
                "Date": "2023-02",
                "Total Amount": 45410,
            },

            {
                "Date": "2023-03",
                "Total Amount": 30330,
            },

            {
                "Date": "2023-04",
                "Total Amount": 38480,
            },

            {
                "Date": "2023-05",
                "Total Amount": 56450,
            },

            {
                "Date": "2023-06",
                "Total Amount": 36715,
            },

            {
                "Date": "2023-07",
                "Total Amount": 35865,
            },

            {
                "Date": "2023-08",
                "Total Amount": 37260,
            },

            {
                "Date": "2023-09",
                "Total Amount": 23620,
            },

            {
                "Date": "2023-10",
                "Total Amount": 50080,
            },

            {
                "Date": "2023-11",
                "Total Amount": 37100,
            },

            {
                "Date": "2023-12",
                "Total Amount": 44690,
            },

            {
                "Date": "2024-01",
                "Total Amount": 1530,
            },
        ]
    },


    "ranking_results": {

        "top_products_by_sales": [

            {
                "Product Category":
                    "Electronics",

                "Total Amount":
                    166955,
            },

            {
                "Product Category":
                    "Clothing",

                "Total Amount":
                    158965,
            },

            {
                "Product Category":
                    "Beauty",

                "Total Amount":
                    150240,
            },
        ],


        "top_regions_by_sales": [

            {
                "City":
                    "San Francisco",

                "Total Amount":
                    71335,
            },

            {
                "City":
                    "Miami",

                "Total Amount":
                    54210,
            },

            {
                "City":
                    "Chicago",

                "Total Amount":
                    49660,
            },
        ],


        "top_customers_by_sales": [

            {
                "Customer ID":
                    "CUST015",

                "Total Amount":
                    5000,
            },

            {
                "Customer ID":
                    "CUST869",

                "Total Amount":
                    4500,
            },

            {
                "Customer ID":
                    "CUST074",

                "Total Amount":
                    4000,
            },
        ],
    },
}


# =====================================================================
# 3. EDA VALIDATION
# =====================================================================

EDA_VALIDATION = {

    "overall_status": "PASSED",

    "total_checks": 5,

    "passed": 5,

    "warnings": 0,

    "failed": 0,
}


# =====================================================================
# 4. CREATE STAGE-SPECIFIC WORKFLOW CONTEXT
# =====================================================================

state = create_initial_state(
    df
)


state.semantic_mapping = (
    SEMANTIC_MAPPING
)


state.capabilities = (
    CAPABILITIES
)


state.planner_result = {

    "status": "completed",

    "semantic_mapping":
        SEMANTIC_MAPPING,

    "capabilities":
        CAPABILITIES,
}


state.planner_status = (
    "completed"
)


state.agent_status[
    "Planner Agent"
] = "completed"


state.eda_result = (
    eda_result
)


state.eda_validation = (
    EDA_VALIDATION
)


state.eda_status = (
    "completed"
)


state.agent_status[
    "EDA Agent"
] = "completed"


print()
print(
    "STAGE CONTEXT"
)

print(
    "Planner Agent:",
    state.agent_status[
        "Planner Agent"
    ]
)

print(
    "EDA Agent:",
    state.agent_status[
        "EDA Agent"
    ]
)

print(
    "EDA Validation:",
    state.eda_validation[
        "overall_status"
    ]
)

print(
    "Stage Context: CREATED"
)


# =====================================================================
# 5. RUN FORECASTING AS UPSTREAM DEPENDENCY
# =====================================================================

state = run_forecasting_stage(
    state=state,
    horizon=7,
    test_size=30,
    moving_average_window=7,
)


assert (
    state.forecasting_result
    is not None
)


assert (
    state.forecasting_status
    == "completed"
)


assert (
    state.agent_status[
        "Forecasting Agent"
    ]
    == "completed"
)


print()
print(
    "UPSTREAM FORECASTING"
)

print(
    "Forecasting Agent:",
    state.agent_status[
        "Forecasting Agent"
    ]
)

print(
    "Forecasting Result: AVAILABLE"
)

print(
    "Forecasting Dependency: PASSED"
)


# =====================================================================
# 6. RUN INSIGHT AS UPSTREAM DEPENDENCY
# =====================================================================

state = run_insight_stage(
    state=state,
    minimum_confidence=0.80,
)


assert (
    state.insight_result
    is not None
)


assert (
    state.insight_status
    == "completed"
)


assert (
    state.agent_status[
        "Insight Agent"
    ]
    == "completed"
)


assert (
    state.insight_result[
        "status"
    ]
    == "completed"
)


assert (
    state.insight_result[
        "total_insights"
    ]
    >= 10
)


assert (
    state.insight_validation
    is not None
)


assert (
    state.insight_validation[
        "overall_status"
    ]
    == "PASSED"
)


assert (
    state.insight_validation[
        "failed"
    ]
    == 0
)


print()
print(
    "UPSTREAM INSIGHT"
)

print(
    "Insight Agent:",
    state.agent_status[
        "Insight Agent"
    ]
)

print(
    "Total Insights:",
    state.insight_result[
        "total_insights"
    ]
)

print(
    "Insight Validation: PASSED"
)


# =====================================================================
# 7. RECOMMENDATION ROUTING
# =====================================================================
#
# IMPORTANT:
#
# Recommendation routing is checked ONLY AFTER the Insight Agent
# has completed successfully.
#
# Before Insight execution, SKIP_RECOMMENDATION is expected because
# Recommendation requires validated Insight results.
# =====================================================================

route = get_recommendation_route(
    state
)


assert (
    route
    == RUN_RECOMMENDATION
)


print()
print(
    "RECOMMENDATION ROUTING"
)

print(
    "Routing Decision:",
    route
)

print(
    "Recommendation Routing Decision: PASSED"
)


# =====================================================================
# 8. RUN RECOMMENDATION STAGE
# =====================================================================
#
# Do NOT call run_workflow().
#
# The complete workflow would continue to the Report Agent.
#
# This test intentionally stops after Recommendation.
# =====================================================================
# Use an isolated SQLite database for this cache test.
_test_cache_dir = tempfile.TemporaryDirectory()

_test_cache = RecommendationCache(
    Path(_test_cache_dir.name) / "recommendations.sqlite3"
)

_original_recommendation_agent = (
    workflow_graph.RecommendationAgent
)


def _recommendation_agent_with_test_cache(**kwargs):
    return _original_recommendation_agent(
        **kwargs,
        cache=_test_cache,
    )


workflow_graph.RecommendationAgent = (
    _recommendation_agent_with_test_cache
)

state = run_recommendation_stage(
    state=state
)


# =====================================================================
# 9. WORKFLOW STAGE
# =====================================================================

print()
print(
    "WORKFLOW STAGE"
)

print(
    "Current Stage:",
    state.current_stage
)

print(
    "Workflow Status:",
    state.workflow_status
)


assert (
    state.current_stage
    == "recommendation"
)


print(
    "Recommendation Stage Execution: PASSED"
)


# =====================================================================
# 10. RECOMMENDATION AGENT STATUS
# =====================================================================

recommendation_agent_status = (
    state.agent_status.get(
        "Recommendation Agent"
    )
)


assert (
    recommendation_agent_status
    == "completed"
)


assert (
    state.recommendation_status
    == "completed"
)


print()
print(
    "AGENT STATUS"
)

print(
    "Recommendation Agent:",
    recommendation_agent_status
)

print(
    "Recommendation Agent Status: PASSED"
)


# =====================================================================
# 11. RECOMMENDATION RESULT
# =====================================================================

assert (
    state.recommendation_result
    is not None
)


assert (
    state.recommendation_result[
        "status"
    ]
    == "completed"
)


assert (
    state.recommendation_result[
        "total_recommendations"
    ]
    >= 1
)


print()
print(
    "RECOMMENDATION RESULT"
)

print(
    "Result Status:",
    state.recommendation_result[
        "status"
    ]
)

print(
    "Total Recommendations:",
    state.recommendation_result[
        "total_recommendations"
    ]
)

print(
    "Recommendation Result Stored: PASSED"
)


# =====================================================================
# 12. RECOMMENDATION VALIDATION
# =====================================================================

assert (
    state.recommendation_validation
    is not None
)


assert (
    state.recommendation_validation[
        "overall_status"
    ]
    == "PASSED"
)


assert (
    state.recommendation_validation[
        "failed"
    ]
    == 0
)


print()
print(
    "RECOMMENDATION VALIDATION"
)

print(
    "Overall Status:",
    state.recommendation_validation[
        "overall_status"
    ]
)

print(
    "Failed Checks:",
    state.recommendation_validation[
        "failed"
    ]
)

print(
    "Recommendation Validation: PASSED"
)


# =====================================================================
# 13. RECOMMENDATION SCOPE
# =====================================================================

recommendations = (
    state.recommendation_result[
        "recommendations"
    ]
)


assert isinstance(
    recommendations,
    list
)


assert len(
    recommendations
) >= 1


scopes = set()


for recommendation in recommendations:

    assert isinstance(
        recommendation,
        dict
    )

    recommendation_type = (
        recommendation.get(
            "recommendation_type"
        )
    )

    if recommendation_type:

        scopes.add(
            recommendation_type
        )


print()
print(
    "RECOMMENDATION SCOPE"
)

print(
    "Scopes:",
    sorted(scopes)
)

print(
    "Total Recommendations:",
    len(recommendations)
)


# =====================================================================
# 14. RECOMMENDATION SAFETY CHECK
# =====================================================================

safety_check = (
    state.recommendation_result.get(
        "safety_check"
    )
)


if isinstance(
    safety_check,
    dict
):

    safety_status = (
        safety_check.get(
            "overall_status"
        )
    )

    if safety_status is None:

        safety_status = (
            safety_check.get(
                "status"
            )
        )

    if safety_status is not None:

        assert (
            str(
                safety_status
            ).upper()
            == "PASSED"
        )


print(
    "Recommendation Safety Check: PASSED"
)


# =====================================================================
# 15. DECISION TRACE
# =====================================================================

assert (
    state.decision_trace
)


recommendation_trace = [

    entry

    for entry in state.decision_trace

    if entry.get("agent")
    == "Recommendation Agent"
]


assert (
    recommendation_trace
)


required_trace_fields = {

    "agent",

    "decision",

    "reason",

    "evidence",

    "action",

    "result",

    "validation_status",
}


for entry in recommendation_trace:

    assert (
        required_trace_fields.issubset(
            entry.keys()
        )
    )


print()
print(
    "DECISION TRACE"
)

print(
    "Recommendation Trace Entries:",
    len(recommendation_trace)
)

print(
    "Recommendation Decision Trace: PASSED"
)


# =====================================================================
# 16. WORKFLOW ERRORS
# =====================================================================

assert (
    state.errors == []
)


print()
print(
    "WORKFLOW ERRORS"
)

print(
    "Errors:",
    state.errors
)

print(
    "Workflow Errors: PASSED"
)


# =====================================================================
# 17. SERIALIZATION
# =====================================================================

serialized = (
    state.to_dict()
)


assert isinstance(
    serialized,
    dict
)


assert (
    serialized[
        "recommendation_result"
    ]
    is not None
)


assert (
    serialized[
        "agent_status"
    ][
        "Recommendation Agent"
    ]
    == "completed"
)


print()
print(
    "WORKFLOW SERIALIZATION"
)

print(
    "Recommendation Result Serialization: PASSED"
)

print(
    "Agent Status Serialization: PASSED"
)


# =====================================================================
# 18. UPSTREAM REGRESSION CHECK
# =====================================================================

assert (
    state.forecasting_result
    is not None
)


assert (
    state.forecasting_status
    == "completed"
)


assert (
    state.agent_status[
        "Forecasting Agent"
    ]
    == "completed"
)


assert (
    state.insight_result
    is not None
)


assert (
    state.insight_status
    == "completed"
)


assert (
    state.agent_status[
        "Insight Agent"
    ]
    == "completed"
)


print()
print(
    "UPSTREAM REGRESSION CHECK"
)

print(
    "Forecasting Result: PASSED"
)

print(
    "Forecasting Agent Status: PASSED"
)

print(
    "Insight Result: PASSED"
)

print(
    "Insight Agent Status: PASSED"
)

print(
    "8.6.5 + 8.7.3 Regression Protection: PASSED"
)


# =====================================================================
# 19. STAGE ISOLATION
# =====================================================================

assert state.current_stage == "recommendation"

report_status = state.agent_status.get("Report Agent")

assert report_status in ("pending", None)

print()
print("STAGE ISOLATION")
print("Report Agent was not executed.")
print("Stage Isolation: PASSED")


# =====================================================================
# RECOMMENDATION CACHE-HIT TEST
# =====================================================================

print()
print("RECOMMENDATION CACHE-HIT TEST")

# Run the same recommendation stage again with identical inputs.
state = run_recommendation_stage(state=state)

assert state.recommendation_status == "completed"

cache_trace = state.recommendation_result.get(
    "decision_trace", []
)

assert any(
    "loaded from SQLite cache" in str(entry)
    for entry in cache_trace
), "Second run did not report a recommendation cache hit."

assert state.recommendation_result["total_recommendations"] > 0

print("Second recommendation run: PASSED")
print("SQLite cache hit: CONFIRMED")


# =====================================================================
# CLEAN UP TEMPORARY SQLITE CACHE
# =====================================================================

# Restore the original class before releasing the test cache.
workflow_graph.RecommendationAgent = _original_recommendation_agent

# Release references that may keep the SQLite cache alive.
del _recommendation_agent_with_test_cache
del _test_cache

gc.collect()

# Delete the temporary directory after releasing the cache.
_test_cache_dir.cleanup()

print("Temporary SQLite cache cleanup: PASSED")


# =====================================================================
# FINAL RESULT
# =====================================================================

print()
print("=" * 70)
print("8.7.6 RECOMMENDATION AGENT WORKFLOW INTEGRATION: PASSED")
print("RECOMMENDATION CACHE-HIT TEST: PASSED")
print("=" * 70)
