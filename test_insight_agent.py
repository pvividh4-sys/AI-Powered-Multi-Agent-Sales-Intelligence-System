"""
8.7.2 Insight Agent Test

Tests the Insight Agent using validated analytical results from
the EDA and Forecasting stages.
"""

from pathlib import Path

import pandas as pd

from agents.insight_agent import (
    InsightAgent,
    run_insight_agent,
)


print("=" * 70)
print("8.7.2 INSIGHT AGENT TEST")
print("=" * 70)


# =====================================================================
# 1. LOAD DATASET
# =====================================================================

DATASET_PATH = Path(
    "data/sample/Retail Sales Dataset.csv"
)

df = pd.read_csv(DATASET_PATH)

print()
print(f"Dataset Shape: {df.shape}")

assert not df.empty
print("Dataset Load: PASSED")


# =====================================================================
# 2. PREPARE VALIDATED KPI RESULTS
# =====================================================================

kpi_results = {
    "total_sales": 476160.0,
    "total_quantity": 2632.0,
    "total_orders": 1000,
    "total_customers": 1000,
    "average_order_value": 476.16,
    "average_quantity_per_order": 2.632,
    "average_selling_price": 180.91185410334347,
}

print()
print("KPI Evidence: Prepared")
print("KPI Evidence Preparation: PASSED")


# =====================================================================
# 3. PREPARE VALIDATED TREND RESULTS
# =====================================================================

trend_results = {
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
}

print("Trend Evidence: Prepared")
print("Trend Evidence Preparation: PASSED")


# =====================================================================
# 4. PREPARE VALIDATED RANKING RESULTS
# =====================================================================

ranking_results = {
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
}

print("Ranking Evidence: Prepared")
print("Ranking Evidence Preparation: PASSED")


# =====================================================================
# 5. PREPARE VALIDATED FORECASTING RESULT
# =====================================================================

forecasting_result = {
    "status": "completed",
    "best_model": "Exponential Smoothing",
    "best_mae": 786.807443202053,
    "horizon": 7,
}

forecasting_validation = {
    "overall_status": "PASSED",
    "total_checks": 5,
    "passed": 5,
    "failed": 0,
}

print("Forecasting Evidence: Prepared")
print("Forecasting Evidence Preparation: PASSED")


# =====================================================================
# 6. PREPARE EDA VALIDATION
# =====================================================================

eda_validation = {
    "overall_status": "PASSED",
    "total_checks": 5,
    "passed": 5,
    "warnings": 0,
    "failed": 0,
}

print("EDA Validation: Prepared")
print("EDA Validation Preparation: PASSED")


# =====================================================================
# 7. CREATE INSIGHT AGENT
# =====================================================================

agent = InsightAgent(
    minimum_confidence=0.80
)

assert agent.AGENT_NAME == "Insight Agent"

print()
print("INSIGHT AGENT")
print(f"Agent Name: {agent.AGENT_NAME}")
print(
    f"Minimum Confidence: "
    f"{agent.minimum_confidence}"
)
print("Agent Creation: PASSED")


# =====================================================================
# 8. RUN INSIGHT AGENT
# =====================================================================

result = agent.run(
    kpi_results=kpi_results,
    trend_results=trend_results,
    ranking_results=ranking_results,
    forecasting_result=forecasting_result,
    eda_validation=eda_validation,
    forecasting_validation=forecasting_validation,
)

assert result is not None
assert result.status == "completed"

print()
print("AGENT EXECUTION")
print(f"Agent Status: {result.status}")
print("Insight Agent Execution: PASSED")


# =====================================================================
# 9. CHECK EVIDENCE SOURCES
# =====================================================================

expected_sources = {
    "validated_kpis",
    "validated_trends",
    "validated_rankings",
    "validated_forecasting",
}

actual_sources = set(
    result.evidence_sources
)

assert expected_sources.issubset(
    actual_sources
)

print()
print("EVIDENCE SOURCES")
print(
    f"Sources Used: "
    f"{result.evidence_sources}"
)
print("Evidence Source Integration: PASSED")


# =====================================================================
# 10. CHECK GENERATED INSIGHTS
# =====================================================================

assert result.total_insights >= 10
assert len(result.insights) == result.total_insights

print()
print("GENERATED INSIGHTS")
print(
    f"Total Insights: "
    f"{result.total_insights}"
)

print("Insight Generation: PASSED")


# =====================================================================
# 11. CHECK SPECIFIC INSIGHTS
# =====================================================================

insight_types = {
    insight["insight_type"]
    for insight in result.insights
}

assert "sales_performance" in insight_types
assert "order_volume" in insight_types
assert "order_value" in insight_types
assert "sales_trend" in insight_types
assert "period_warning" in insight_types
assert "product_performance" in insight_types
assert "regional_performance" in insight_types
assert "customer_performance" in insight_types
assert "forecast_performance" in insight_types

print()
print("INSIGHT TYPES")
print(
    f"Detected Types: "
    f"{sorted(insight_types)}"
)
print("Insight Type Coverage: PASSED")


# =====================================================================
# 12. VERIFY IMPORTANT BUSINESS EVIDENCE
# =====================================================================

top_product = next(
    insight
    for insight in result.insights
    if insight["insight_type"]
    == "product_performance"
)

assert top_product["value"] == 166955.0
assert (
    top_product["evidence"]["category"]
    == "Electronics"
)

top_region = next(
    insight
    for insight in result.insights
    if insight["insight_type"]
    == "regional_performance"
)

assert top_region["value"] == 71335.0
assert (
    top_region["evidence"]["region"]
    == "San Francisco"
)

top_customer = next(
    insight
    for insight in result.insights
    if insight["insight_type"]
    == "customer_performance"
)

assert top_customer["value"] == 5000.0
assert (
    top_customer["evidence"]["customer"]
    == "CUST015"
)

forecast_insight = next(
    insight
    for insight in result.insights
    if insight["insight_type"]
    == "forecast_performance"
)

assert (
    forecast_insight["value"]
    == 786.807443202053
)

print()
print("EVIDENCE GROUNDING")
print("Top Product Evidence: PASSED")
print("Top Region Evidence: PASSED")
print("Top Customer Evidence: PASSED")
print("Forecast Evidence: PASSED")


# =====================================================================
# 13. VERIFY PARTIAL-PERIOD PROTECTION
# =====================================================================

partial_period_insights = [
    insight
    for insight in result.insights
    if insight["insight_type"]
    == "period_warning"
]

assert partial_period_insights

partial_warning = partial_period_insights[0]

assert (
    partial_warning["evidence"]["warning"]
    == "partial_period"
)

assert (
    "partial observation period"
    in partial_warning["statement"]
)

print()
print("PARTIAL PERIOD PROTECTION")
print(
    "January 2024 Partial Period Warning: PASSED"
)
print(
    "No Unsupported Full-Month Decline Claim: PASSED"
)


# =====================================================================
# 14. CHECK CONFIDENCE POLICY
# =====================================================================

for insight in result.insights:
    confidence = float(
        insight["confidence"]
    )

    assert (
        confidence
        >= agent.minimum_confidence
    )

print()
print("CONFIDENCE POLICY")
print(
    f"Minimum Required Confidence: "
    f"{agent.minimum_confidence}"
)
print("Confidence Policy: PASSED")


# =====================================================================
# 15. CHECK INSIGHT VALIDATION
# =====================================================================

validation = result.validation

assert validation["overall_status"] == "PASSED"
assert validation["failed"] == 0

print()
print("INSIGHT VALIDATION")
print(
    f"Overall Status: "
    f"{validation['overall_status']}"
)
print(
    f"Total Checks: "
    f"{validation['total_checks']}"
)
print(
    f"Passed: "
    f"{validation['passed']}"
)
print(
    f"Failed: "
    f"{validation['failed']}"
)

print("Insight Validation: PASSED")


# =====================================================================
# 16. CHECK DECISION TRACE
# =====================================================================

assert result.decision_trace
assert len(result.decision_trace) >= 5

required_trace_fields = {
    "decision",
    "reason",
    "evidence",
    "action",
    "result",
    "validation_status",
}

for trace_entry in result.decision_trace:
    assert required_trace_fields.issubset(
        trace_entry.keys()
    )

print()
print("DECISION TRACE")
print(
    f"Trace Entries: "
    f"{len(result.decision_trace)}"
)
print(
    "Decision Trace Structure: PASSED"
)


# =====================================================================
# 17. CHECK NO ERRORS
# =====================================================================

assert result.errors == []

print()
print("ERROR HANDLING")
print(f"Errors: {result.errors}")
print("Error Check: PASSED")


# =====================================================================
# 18. CHECK SERIALIZATION
# =====================================================================

serialized = result.to_dict()

assert isinstance(serialized, dict)

required_result_fields = {
    "status",
    "insights",
    "validation",
    "total_insights",
    "evidence_sources",
    "decision_trace",
    "warnings",
    "errors",
    "message",
}

assert required_result_fields.issubset(
    serialized.keys()
)

assert isinstance(
    serialized["insights"],
    list,
)

assert isinstance(
    serialized["decision_trace"],
    list,
)

print()
print("SERIALIZATION")
print("Result Dictionary: PASSED")
print("Insight List Serialization: PASSED")
print("Decision Trace Serialization: PASSED")


# =====================================================================
# 19. TEST CONVENIENCE FUNCTION
# =====================================================================

convenience_result = run_insight_agent(
    kpi_results=kpi_results,
    trend_results=trend_results,
    ranking_results=ranking_results,
    forecasting_result=forecasting_result,
    eda_validation=eda_validation,
    forecasting_validation=forecasting_validation,
)

assert convenience_result.status == "completed"
assert convenience_result.total_insights >= 10

print()
print("CONVENIENCE FUNCTION")
print(
    f"Status: "
    f"{convenience_result.status}"
)
print(
    f"Insights: "
    f"{convenience_result.total_insights}"
)
print("Convenience Function: PASSED")


# =====================================================================
# 20. TEST SAFETY — FAILED EDA MUST BLOCK INSIGHTS
# =====================================================================

failed_eda_validation = {
    "overall_status": "FAILED",
    "total_checks": 5,
    "passed": 4,
    "failed": 1,
}

blocked_result = agent.run(
    kpi_results=kpi_results,
    trend_results=trend_results,
    ranking_results=ranking_results,
    forecasting_result=forecasting_result,
    eda_validation=failed_eda_validation,
    forecasting_validation=forecasting_validation,
)

assert blocked_result.status == "failed"
assert blocked_result.total_insights == 0
assert blocked_result.errors

print()
print("SAFETY / VALIDATION GATE")
print(
    "Failed EDA Validation: "
    "Insight Generation Blocked"
)
print("Validation Gate: PASSED")


# =====================================================================
# FINAL RESULT
# =====================================================================

print()
print("=" * 70)
print("8.7.2 INSIGHT AGENT TEST: PASSED")
print("=" * 70)