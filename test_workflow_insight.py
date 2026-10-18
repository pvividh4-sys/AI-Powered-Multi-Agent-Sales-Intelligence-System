"""
8.7.3 - Insight Agent Workflow Integration Test

This test verifies the Insight Agent stage independently.

The test prepares validated EDA evidence and executes the
Forecasting Agent as an upstream dependency before executing
the Insight Agent.

The test intentionally uses run_insight_stage() rather than
run_workflow(), because run_workflow() now executes the complete
eight-agent workflow and therefore continues to the Report Agent.

Complete end-to-end workflow testing is handled separately by:
    test_end_to_end.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from workflow.graph import (
    run_forecasting_stage,
    run_insight_stage,
)
from workflow.routing import (
    RUN_INSIGHT,
    get_insight_route,
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
print("8.7.3 INSIGHT AGENT WORKFLOW INTEGRATION TEST")
print("=" * 70)

df = pd.read_csv(DATASET_PATH)

print()
print("Dataset Shape:", df.shape)

assert not df.empty
assert df.shape == (1000, 16)

print("Dataset Load: PASSED")


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
        "average_selling_price": 180.91185410334347,
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
                "Product Category": "Electronics",
                "Total Amount": 166955,
            },
            {
                "Product Category": "Clothing",
                "Total Amount": 158965,
            },
            {
                "Product Category": "Beauty",
                "Total Amount": 150240,
            },
        ],

        "top_regions_by_sales": [
            {
                "City": "San Francisco",
                "Total Amount": 71335,
            },
            {
                "City": "Miami",
                "Total Amount": 54210,
            },
            {
                "City": "Chicago",
                "Total Amount": 49660,
            },
        ],

        "top_customers_by_sales": [
            {
                "Customer ID": "CUST015",
                "Total Amount": 5000,
            },
            {
                "Customer ID": "CUST869",
                "Total Amount": 4500,
            },
            {
                "Customer ID": "CUST074",
                "Total Amount": 4000,
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

state = create_initial_state(df)

state.semantic_mapping = SEMANTIC_MAPPING
state.capabilities = CAPABILITIES

state.planner_result = {
    "status": "completed",
    "semantic_mapping": SEMANTIC_MAPPING,
    "capabilities": CAPABILITIES,
}

state.planner_status = "completed"

state.agent_status["Planner Agent"] = "completed"

state.eda_result = eda_result
state.eda_validation = EDA_VALIDATION
state.eda_status = "completed"

state.agent_status["EDA Agent"] = "completed"

print()
print("STAGE CONTEXT")
print("Planner Agent:", state.agent_status["Planner Agent"])
print("EDA Agent:", state.agent_status["EDA Agent"])
print("EDA Validation:", state.eda_validation["overall_status"])
print("Stage Context: CREATED")


# =====================================================================
# 5. INSIGHT ROUTING CHECK
# =====================================================================

route = get_insight_route(state)

assert route == RUN_INSIGHT

print()
print("INSIGHT ROUTING")
print("Routing Decision:", route)
print("Insight Routing Decision: PASSED")


# =====================================================================
# 6. RUN FORECASTING AS UPSTREAM DEPENDENCY
# =====================================================================

state = run_forecasting_stage(
    state=state,
    horizon=7,
    test_size=30,
    moving_average_window=7,
)

assert state.forecasting_result is not None

assert (
    state.forecasting_status
    == "completed"
)

assert (
    state.agent_status["Forecasting Agent"]
    == "completed"
)

print()
print("UPSTREAM FORECASTING")
print(
    "Forecasting Agent:",
    state.agent_status["Forecasting Agent"],
)
print("Forecasting Result: AVAILABLE")
print("Forecasting Dependency: PASSED")


# =====================================================================
# 7. RUN INSIGHT STAGE
# =====================================================================

state = run_insight_stage(
    state=state,
    minimum_confidence=0.80,
)


# =====================================================================
# 8. WORKFLOW STAGE
# =====================================================================

print()
print("WORKFLOW STAGE")
print("Current Stage:", state.current_stage)
print("Workflow Status:", state.workflow_status)

assert state.current_stage == "insight"

print("Insight Stage Execution: PASSED")


# =====================================================================
# 9. INSIGHT AGENT STATUS
# =====================================================================

insight_agent_status = state.agent_status.get(
    "Insight Agent"
)

assert insight_agent_status == "completed"

print()
print("AGENT STATUS")
print(
    "Insight Agent:",
    insight_agent_status,
)
print("Insight Agent Status: PASSED")


# =====================================================================
# 10. INSIGHT RESULT
# =====================================================================

assert state.insight_result is not None

assert (
    state.insight_result["status"]
    == "completed"
)

assert (
    state.insight_result["total_insights"]
    >= 10
)

print()
print("INSIGHT RESULT")

print(
    "Result Status:",
    state.insight_result["status"],
)

print(
    "Total Insights:",
    state.insight_result["total_insights"],
)

print("Insight Result Stored: PASSED")


# =====================================================================
# 11. INSIGHT VALIDATION
# =====================================================================

assert state.insight_validation is not None

assert (
    state.insight_validation["overall_status"]
    == "PASSED"
)

assert (
    state.insight_validation["failed"]
    == 0
)

print()
print("INSIGHT VALIDATION")

print(
    "Overall Status:",
    state.insight_validation[
        "overall_status"
    ],
)

print(
    "Failed Checks:",
    state.insight_validation[
        "failed"
    ],
)

print("Insight Validation: PASSED")


# =====================================================================
# 12. EVIDENCE SOURCES
# =====================================================================

evidence_sources = set(
    state.insight_result[
        "evidence_sources"
    ]
)

assert "validated_kpis" in evidence_sources
assert "validated_trends" in evidence_sources
assert "validated_rankings" in evidence_sources
assert "validated_forecasting" in evidence_sources

print()
print("EVIDENCE SOURCES")
print(
    "Sources:",
    sorted(evidence_sources),
)
print("Evidence Integration: PASSED")


# =====================================================================
# 13. GROUNDED INSIGHT EVIDENCE
# =====================================================================

insights = state.insight_result[
    "insights"
]


# ---------------------------------------------------------------------
# Product Evidence
# ---------------------------------------------------------------------

top_product = next(
    insight
    for insight in insights
    if insight["insight_type"]
    == "product_performance"
)

assert (
    top_product["evidence"]["category"]
    == "Electronics"
)

assert (
    top_product["value"]
    == 166955.0
)


# ---------------------------------------------------------------------
# Regional Evidence
# ---------------------------------------------------------------------

top_region = next(
    insight
    for insight in insights
    if insight["insight_type"]
    == "regional_performance"
)

assert (
    top_region["evidence"]["region"]
    == "San Francisco"
)

assert (
    top_region["value"]
    == 71335.0
)


# ---------------------------------------------------------------------
# Forecast Evidence
# ---------------------------------------------------------------------

forecast_insight = next(
    insight
    for insight in insights
    if insight["insight_type"]
    == "forecast_performance"
)

assert (
    "best_model"
    in forecast_insight["evidence"]
)

assert (
    forecast_insight["evidence"]
    ["best_model"]
    == state.forecasting_result[
        "best_model"
    ]
)

assert (
    forecast_insight["evidence"]
    ["best_mae"]
    == state.forecasting_result[
        "best_mae"
    ]
)

assert (
    forecast_insight["evidence"]
    ["horizon"]
    == state.forecasting_result[
        "horizon"
    ]
)


print()
print("GROUNDED INSIGHT EVIDENCE")

print("Top Product: PASSED")
print("Top Region: PASSED")

print(
    "Forecast Model:",
    forecast_insight["evidence"]
    ["best_model"],
    "- PASSED",
)

print(
    "Forecast MAE:",
    f"{forecast_insight['evidence']['best_mae']:.4f}",
    "- PASSED",
)

print(
    "Forecast Horizon:",
    forecast_insight["evidence"]
    ["horizon"],
    "- PASSED",
)


# =====================================================================
# 14. DECISION TRACE
# =====================================================================

assert state.decision_trace

insight_trace = [
    entry
    for entry in state.decision_trace
    if entry.get("agent")
    == "Insight Agent"
]

assert insight_trace

required_trace_fields = {
    "agent",
    "decision",
    "reason",
    "evidence",
    "action",
    "result",
    "validation_status",
}

for entry in insight_trace:
    assert required_trace_fields.issubset(
        entry.keys()
    )

print()
print("DECISION TRACE")
print(
    "Insight Trace Entries:",
    len(insight_trace),
)
print("Insight Decision Trace: PASSED")


# =====================================================================
# 15. WORKFLOW ERRORS
# =====================================================================

assert state.errors == []

print()
print("WORKFLOW ERRORS")
print("Errors:", state.errors)
print("Workflow Errors: PASSED")


# =====================================================================
# 16. SERIALIZATION
# =====================================================================

serialized = state.to_dict()

assert isinstance(
    serialized,
    dict,
)

assert (
    serialized["insight_result"]
    is not None
)

assert (
    serialized["agent_status"]
    ["Insight Agent"]
    == "completed"
)

print()
print("WORKFLOW SERIALIZATION")
print("Insight Result Serialization: PASSED")
print("Agent Status Serialization: PASSED")


# =====================================================================
# 17. FORECASTING REGRESSION CHECK
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
    state.agent_status["Forecasting Agent"]
    == "completed"
)

print()
print("FORECASTING REGRESSION CHECK")
print("Forecasting Result: PASSED")
print("Forecasting Agent Status: PASSED")
print("8.6.5 Regression Protection: PASSED")


# =====================================================================
# FINAL RESULT
# =====================================================================

print()
print("=" * 70)
print(
    "8.7.3 INSIGHT AGENT WORKFLOW "
    "INTEGRATION: PASSED"
)
print("=" * 70)