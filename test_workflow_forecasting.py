"""
8.6.5 - Forecasting Agent Workflow Integration Test

This test verifies the Forecasting Agent stage independently.

The test intentionally uses run_forecasting_stage() rather than
run_workflow(), because run_workflow() now executes the complete
eight-agent workflow and therefore ends at the Report Agent.

Complete end-to-end workflow testing is handled separately by:
    test_end_to_end.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from workflow.graph import run_forecasting_stage
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
print("8.6.5 FORECASTING AGENT WORKFLOW INTEGRATION TEST")
print("=" * 70)

df = pd.read_csv(DATASET_PATH)

print()
print("Dataset Shape:", df.shape)

assert not df.empty
assert df.shape == (1000, 16)

print("Dataset Load: PASSED")


# =====================================================================
# 2. CREATE STAGE-SPECIFIC WORKFLOW CONTEXT
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

print()
print("STAGE CONTEXT")
print("Planner Agent:", state.agent_status["Planner Agent"])
print("Semantic Mapping: AVAILABLE")
print("Capabilities: AVAILABLE")
print("Stage Context: CREATED")


# =====================================================================
# 3. RUN FORECASTING STAGE
# =====================================================================

state = run_forecasting_stage(
    state=state,
    horizon=7,
    test_size=30,
    moving_average_window=7,
)


# =====================================================================
# 4. WORKFLOW STAGE
# =====================================================================

print()
print("WORKFLOW STAGE")
print("Current Stage:", state.current_stage)
print("Workflow Status:", state.workflow_status)

assert state.current_stage == "forecasting"

print("Forecasting Stage Execution: PASSED")


# =====================================================================
# 5. FORECASTING ROUTING
# =====================================================================

print()
print("FORECASTING ROUTING")

print(
    "Routing Decision:",
    state.forecasting_decision,
)

print(
    "Forecasting Status:",
    state.forecasting_status,
)

assert state.forecasting_decision == "RUN_FORECASTING"

print("Forecasting Route: RUN_FORECASTING")
print("Forecasting Routing: PASSED")


# =====================================================================
# 6. FORECASTING AGENT STATUS
# =====================================================================

print()
print("AGENT STATUS")

forecasting_agent_status = state.agent_status.get(
    "Forecasting Agent"
)

print(
    "Forecasting Agent:",
    forecasting_agent_status,
)

assert forecasting_agent_status == "completed"

print("Forecasting Agent Status: PASSED")


# =====================================================================
# 7. FORECASTING RESULT
# =====================================================================

print()
print("FORECASTING RESULT")

forecasting_result = state.forecasting_result

assert forecasting_result is not None

print(
    "Result Status:",
    forecasting_result.get("status"),
)

assert forecasting_result.get("status") == "completed"

print("Forecasting Result Stored: PASSED")


# =====================================================================
# 8. BEST MODEL
# =====================================================================

best_model = forecasting_result.get(
    "best_model"
)

best_mae = forecasting_result.get(
    "best_mae"
)

print()
print("BEST MODEL")
print("Best Model:", best_model)
print("Best MAE:", best_mae)

assert best_model is not None
assert best_mae is not None

print("Best Model Integration: PASSED")


# =====================================================================
# 9. FORECAST HORIZON
# =====================================================================

horizon = forecasting_result.get(
    "horizon"
)

print()
print("FORECAST HORIZON")
print("Forecast Horizon:", horizon)

assert horizon == 7

print("Forecast Horizon Integration: PASSED")


# =====================================================================
# 10. FORECAST ELIGIBILITY
# =====================================================================

eligibility = forecasting_result.get(
    "eligibility",
    {},
)

print()
print("FORECAST ELIGIBILITY")

print(
    "Eligible:",
    eligibility.get("eligible"),
)

print(
    "Date Column:",
    eligibility.get("date_column"),
)

print(
    "Sales Column:",
    eligibility.get("sales_column"),
)

print(
    "Observations:",
    eligibility.get("observations"),
)

assert eligibility.get("eligible") is True

assert (
    eligibility.get("date_column")
    == "Date"
)

assert (
    eligibility.get("sales_column")
    == "Total Amount"
)

assert (
    eligibility.get("observations")
    == 1000
)

print("Forecast Eligibility: PASSED")


# =====================================================================
# 11. FORECASTING VALIDATION
# =====================================================================

validation = forecasting_result.get(
    "validation",
    {},
)

print()
print("FORECASTING VALIDATION")

print(
    "Overall Status:",
    validation.get("overall_status"),
)

assert (
    validation.get("overall_status")
    == "PASSED"
)

print("Forecasting Validation: PASSED")


# =====================================================================
# 12. DECISION TRACE
# =====================================================================

print()
print("DECISION TRACE")

assert state.decision_trace

forecasting_trace = [
    entry
    for entry in state.decision_trace
    if entry.get("agent")
    == "Forecasting Agent"
]

assert forecasting_trace

required_trace_fields = {
    "agent",
    "decision",
    "reason",
    "evidence",
    "action",
    "result",
    "validation_status",
}

for entry in forecasting_trace:
    assert required_trace_fields.issubset(
        entry.keys()
    )

for index, decision in enumerate(
    state.decision_trace,
    start=1,
):
    print(
        f"{index}. "
        f"{decision.get('agent')} - "
        f"{decision.get('decision')}"
    )

print("Forecasting Decision Trace: PASSED")


# =====================================================================
# 13. NO WORKFLOW ERRORS
# =====================================================================

print()
print("WORKFLOW ERRORS")
print("Errors:", state.errors)

assert state.errors == []

print("Workflow Errors: PASSED")


# =====================================================================
# 14. SERIALIZATION
# =====================================================================

serialized = state.to_dict()

assert isinstance(
    serialized,
    dict,
)

assert (
    serialized["forecasting_result"]
    is not None
)

assert (
    serialized["agent_status"]
    ["Forecasting Agent"]
    == "completed"
)

print()
print("WORKFLOW SERIALIZATION")
print("Forecasting Result Serialization: PASSED")
print("Agent Status Serialization: PASSED")


# =====================================================================
# FINAL RESULT
# =====================================================================

print()
print("=" * 70)
print(
    "8.6.5 FORECASTING AGENT WORKFLOW "
    "INTEGRATION: PASSED"
)
print("=" * 70)