"""
8.8.2 Report Agent Test
=======================

Tests the Report Agent independently after the deterministic Report
Generator foundation has passed.

Coverage:
1. Preconditions and validation gates
2. Evidence-source identification
3. Report generation
4. Report validation
5. Section coverage
6. Evidence grounding
7. Limitation handling
8. Decision traceability
9. Serialization
10. Convenience function
11. Failed validation gate protection
12. Optional forecast handling
"""

from __future__ import annotations

from agents.report_agent import (
    ReportAgent,
    ReportAgentResult,
    run_report_agent,
)


# =====================================================================
# FIXTURES
# =====================================================================


def create_eda_result():

    return {
        "dataset": {
            "rows": 1000,
            "columns": 16,
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
        },

        "kpis": {
            "total_sales": 476160.0,
            "total_quantity": 2632.0,
            "total_orders": 1000,
            "total_customers": 1000,
            "average_order_value": 476.16,
            "average_quantity_per_order": 2.632,
            "average_selling_price": 180.91185410334347,
        },

        "trends": {
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "days": 366,
            "observations": 1000,

            "daily": [
                {
                    "date": "2023-01-01",
                    "sales": 500,
                }
            ],

            "monthly": [
                {
                    "month": "2023-01",
                    "sales": 38630,
                }
            ],
        },

        "rankings": {
            "product_sales": [
                {
                    "category": "Electronics",
                    "sales": 166955,
                },
                {
                    "category": "Clothing",
                    "sales": 158965,
                },
                {
                    "category": "Beauty",
                    "sales": 150240,
                },
            ],

            "product_quantity": [
                {
                    "category": "Clothing",
                    "quantity": 939,
                }
            ],

            "regional_sales": [
                {
                    "city": "San Francisco",
                    "sales": 71335,
                }
            ],

            "customer_sales": [
                {
                    "customer_id": "CUST015",
                    "sales": 5000,
                }
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


def create_cleaning_result():

    return {
        "status": "validated",
        "cleaned_rows": 1000,
        "rows_removed": 0,
        "execution_logs": [],
    }


def create_cleaning_validation():

    return {
        "overall_status": "PASSED",
        "total_checks": 9,
        "passed": 9,
        "failed": 0,
        "warnings": 0,
    }


def create_visualization_result():

    return {
        "status": "completed",

        "selection": [
            "kpi_cards",
            "daily_sales",
            "monthly_sales",
            "product_sales",
            "product_quantity",
            "regional_sales",
            "customer_sales",
        ],

        "kpi_cards": [
            {
                "metric": "total_sales",
                "value": 476160.0,
            }
        ],

        "charts": [
            {
                "chart_id": "daily_sales",
                "title": "Daily Sales Trend",
            },
            {
                "chart_id": "monthly_sales",
                "title": "Monthly Sales Trend",
            },
            {
                "chart_id": "product_sales",
                "title": "Sales by Product Category",
            },
            {
                "chart_id": "product_quantity",
                "title": "Quantity by Product Category",
            },
            {
                "chart_id": "regional_sales",
                "title": "Sales by Region",
            },
            {
                "chart_id": "customer_sales",
                "title": "Top Customers by Sales",
            },
        ],

        "total_charts": 6,

        "validation": {
            "overall_status": "PASSED"
        },
    }


def create_forecasting_result():

    return {
        "status": "completed",

        "eligibility": {
            "eligible": True,
            "date_column": "Date",
            "sales_column": "Total Amount",
            "valid_observations": 1000,
        },

        "evaluation": {
            "best_model": "ARIMA",
            "best_mae": 785.3988254596835,
        },

        "forecast_values": [
            500.0,
            510.0,
            520.0,
        ],

        "validation": {
            "overall_status": "PASSED"
        },
    }


def create_insight_result():

    return {
        "status": "completed",

        "insights": [
            {
                "insight_id": "I001",
                "insight_type": "sales_performance",
                "insight": (
                    "Total sales were 476160.0."
                ),
                "evidence_sources": [
                    "validated_kpis"
                ],
                "confidence": 0.95,
            },

            {
                "insight_id": "I002",
                "insight_type": "product_performance",
                "insight": (
                    "Electronics generated the highest "
                    "product-category sales."
                ),
                "evidence_sources": [
                    "validated_rankings"
                ],
                "confidence": 0.95,
            },
        ],

        "validation": {
            "overall_status": "PASSED",
            "total_checks": 12,
            "passed": 12,
            "failed": 0,
            "warnings": 0,
        },
    }


def create_recommendation_result():

    return {
        "status": "completed",

        "recommendations": [
            {
                "recommendation_id": "R001",
                "recommendation_type": "Product",
                "title": (
                    "Focus on leading product category"
                ),

                "evidence": {
                    "source": "validated_rankings"
                },

                "insight": (
                    "Electronics generated the highest "
                    "product-category sales."
                ),

                "business_implication": (
                    "Leading categories can receive "
                    "focused attention."
                ),

                "recommendation": (
                    "Review inventory and promotional "
                    "opportunities for the leading category."
                ),

                "priority": "HIGH",
                "confidence": 0.90,

                "limitations": [],

                "validation_status": "PASSED",
            }
        ],

        "recommendation_validation": {
            "overall_status": "PASSED",
            "total_checks": 6,
            "passed": 6,
            "failed": 0,
            "warnings": 0,
        },
    }


def create_capabilities():

    return {
        "sales_analysis": True,
        "quantity_analysis": True,
        "product_analysis": True,
        "customer_analysis": True,
        "regional_analysis": True,
        "profitability_analysis": False,
        "forecasting": True,
    }


def create_semantic_mapping():

    return {
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


def run_valid_agent():

    return ReportAgent(
        eda_result=create_eda_result(),
        visualization_result=create_visualization_result(),
        forecasting_result=create_forecasting_result(),
        insight_result=create_insight_result(),
        recommendation_result=(
            create_recommendation_result()
        ),

        semantic_mapping=create_semantic_mapping(),
        capabilities=create_capabilities(),

        cleaning_result=create_cleaning_result(),
        cleaning_validation=create_cleaning_validation(),

        eda_validation=(
            create_eda_result()["validation"]
        ),

        visualization_validation={
            "overall_status": "PASSED",
            "total_checks": 4,
            "passed": 4,
            "failed": 0,
            "warnings": 0,
        },

        insight_validation=(
            create_insight_result()["validation"]
        ),

        recommendation_validation=(
            create_recommendation_result()[
                "recommendation_validation"
            ]
        ),
    )


# =====================================================================
# MAIN TEST
# =====================================================================


def main():

    print("=" * 70)
    print("8.8.2 REPORT AGENT TEST")
    print("=" * 70)

    # ---------------------------------------------------------------
    # Preconditions
    # ---------------------------------------------------------------

    agent = run_valid_agent()

    print("\nPRECONDITIONS")

    assert agent.check_preconditions() is True

    print(
        "Report Agent Preconditions: PASSED"
    )

    # ---------------------------------------------------------------
    # Evidence identification
    # ---------------------------------------------------------------

    print("\nEVIDENCE IDENTIFICATION")

    sources = (
        agent.identify_evidence_sources()
    )

    assert "validated_eda" in sources
    assert (
        "validated_visualizations"
        in sources
    )
    assert (
        "validated_forecasting"
        in sources
    )
    assert (
        "validated_insights"
        in sources
    )
    assert (
        "validated_recommendations"
        in sources
    )

    print(
        "Evidence Sources: PASSED"
    )

    print(
        "Sources:",
        sources
    )

    # ---------------------------------------------------------------
    # Report generation
    # ---------------------------------------------------------------

    print("\nREPORT GENERATION")

    result = agent.run()

    assert isinstance(
        result,
        ReportAgentResult
    )

    assert result.status == "completed"

    assert result.report

    assert result.total_sections == 10

    print(
        "Report Agent Status:",
        result.status
    )

    print(
        "Total Sections:",
        result.total_sections
    )

    print(
        "Report Generation: PASSED"
    )

    # ---------------------------------------------------------------
    # Section coverage
    # ---------------------------------------------------------------

    print(
        "\nREPORT SECTION COVERAGE"
    )

    section_ids = {
        section["section_id"]
        for section in result.report[
            "sections"
        ]
    }

    required_sections = {
        "dataset_overview",
        "data_quality",
        "kpis",
        "trends",
        "rankings",
        "visualizations",
        "forecast",
        "insights",
        "recommendations",
        "limitations",
    }

    assert required_sections.issubset(
        section_ids
    )

    print(
        "All 10 Required Sections: PASSED"
    )

    # ---------------------------------------------------------------
    # Report validation
    # ---------------------------------------------------------------

    print("\nREPORT VALIDATION")

    assert (
        result.report_validation[
            "overall_status"
        ]
        == "PASSED"
    )

    assert (
        result.report_validation[
            "failed"
        ]
        == 0
    )

    print(
        "Overall Status:",
        result.report_validation[
            "overall_status"
        ]
    )

    print(
        "Total Checks:",
        result.report_validation[
            "total_checks"
        ]
    )

    print(
        "Passed:",
        result.report_validation[
            "passed"
        ]
    )

    print(
        "Failed:",
        result.report_validation[
            "failed"
        ]
    )

    print(
        "Report Validation: PASSED"
    )

    # ---------------------------------------------------------------
    # Evidence grounding
    # ---------------------------------------------------------------

    print("\nEVIDENCE GROUNDING")

    report_sources = (
        result.report[
            "evidence_sources"
        ]
    )

    assert (
        "validated_kpis"
        in report_sources
    )

    assert (
        "validated_trends"
        in report_sources
    )

    assert (
        "validated_rankings"
        in report_sources
    )

    assert (
        "validated_visualizations"
        in report_sources
    )

    assert (
        "validated_forecasting"
        in report_sources
    )

    assert (
        "validated_insights"
        in report_sources
    )

    assert (
        "validated_recommendations"
        in report_sources
    )

    print(
        "Evidence Source Traceability: PASSED"
    )

    # ---------------------------------------------------------------
    # Limitation handling
    # ---------------------------------------------------------------

    print("\nLIMITATION HANDLING")

    limitations = (
        result.report[
            "limitations"
        ]
    )

    assert any(
        "Profitability analysis is unavailable"
        in limitation
        for limitation in limitations
    )

    print(
        "Profitability Limitation Disclosure: PASSED"
    )

    # ---------------------------------------------------------------
    # Decision trace
    # ---------------------------------------------------------------

    print("\nDECISION TRACE")

    assert len(
        result.decision_trace
    ) >= 4

    required_trace_keys = {
        "decision",
        "reason",
        "evidence",
        "action",
        "result",
        "validation_status",
    }

    assert required_trace_keys.issubset(
        result.decision_trace[0]
    )

    print(
        "Decision Trace Entries:",
        len(result.decision_trace)
    )

    print(
        "Decision Trace: PASSED"
    )

    # ---------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------

    print("\nSERIALIZATION")

    serialized = (
        result.to_dict()
    )

    assert isinstance(
        serialized,
        dict
    )

    assert (
        serialized["status"]
        == "completed"
    )

    assert isinstance(
        serialized["report"],
        dict
    )

    print(
        "Agent Serialization: PASSED"
    )

    # ---------------------------------------------------------------
    # Convenience function
    # ---------------------------------------------------------------

    print(
        "\nCONVENIENCE FUNCTION"
    )

    convenience = run_report_agent(
        eda_result=create_eda_result(),
        visualization_result=(
            create_visualization_result()
        ),
        forecasting_result=(
            create_forecasting_result()
        ),
        insight_result=(
            create_insight_result()
        ),
        recommendation_result=(
            create_recommendation_result()
        ),

        semantic_mapping=(
            create_semantic_mapping()
        ),

        capabilities=(
            create_capabilities()
        ),

        cleaning_result=(
            create_cleaning_result()
        ),

        cleaning_validation=(
            create_cleaning_validation()
        ),

        eda_validation=(
            create_eda_result()[
                "validation"
            ]
        ),

        visualization_validation={
            "overall_status": "PASSED"
        },

        insight_validation=(
            create_insight_result()[
                "validation"
            ]
        ),

        recommendation_validation=(
            create_recommendation_result()[
                "recommendation_validation"
            ]
        ),
    )

    assert (
        convenience.status
        == "completed"
    )

    assert (
        convenience.report_validation[
            "overall_status"
        ]
        == "PASSED"
    )

    print(
        "run_report_agent(): PASSED"
    )

    # ---------------------------------------------------------------
    # Failed validation gate
    # ---------------------------------------------------------------

    print(
        "\nFAILED VALIDATION GATE PROTECTION"
    )

    blocked = run_valid_agent()

    blocked.insight_validation = {
        "overall_status": "FAILED"
    }

    blocked_result = (
        blocked.run()
    )

    assert (
        blocked_result.status
        == "failed"
    )

    assert (
        blocked_result.report
        == {}
    )

    assert blocked_result.errors

    print(
        "Failed Insight Gate Blocks Report: PASSED"
    )

    # ---------------------------------------------------------------
    # Optional forecasting
    # ---------------------------------------------------------------

    print(
        "\nOPTIONAL FORECAST HANDLING"
    )

    no_forecast = run_valid_agent()

    no_forecast.forecasting_result = {}

    no_forecast_result = (
        no_forecast.run()
    )

    assert (
        no_forecast_result.status
        == "completed"
    )

    forecast_section = next(
        section
        for section in no_forecast_result.report[
            "sections"
        ]
        if section["section_id"]
        == "forecast"
    )

    assert (
        forecast_section[
            "content"
        ]["status"]
        == "NOT_AVAILABLE"
    )

    print(
        "Forecast Not Available Handling: PASSED"
    )

    # ---------------------------------------------------------------
    # Final
    # ---------------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "8.8.2 REPORT AGENT TEST: PASSED"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()