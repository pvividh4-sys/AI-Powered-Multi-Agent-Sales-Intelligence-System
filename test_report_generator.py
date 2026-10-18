"""
8.8.1 Report Generator Test
===========================

Tests the deterministic Report Generator foundation.

The test verifies:

1. Input preparation
2. Individual section builders
3. Complete report generation
4. Required report sections
5. Evidence grounding
6. Unsupported-claim protection
7. Report validation
8. Serialization
9. Convenience pipeline
10. Optional forecast handling

This test does not execute the Report Agent.
It tests only reporting/report_generator.py.
"""

from __future__ import annotations

from pathlib import Path
import sys


# =====================================================================
# PROJECT ROOT
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =====================================================================
# IMPORTS
# =====================================================================

from reporting.report_generator import (
    build_executive_summary,
    build_dataset_overview,
    build_data_quality_section,
    build_kpi_section,
    build_trend_section,
    build_ranking_section,
    build_visualization_section,
    build_forecast_section,
    build_insights_section,
    build_recommendations_section,
    build_limitations,
    generate_report,
    validate_report,
    serialize_report,
    build_report,
)


# =====================================================================
# TEST DATA
# =====================================================================

EDA_RESULT = {
    "status": "completed",

    "dataset": {
        "rows": 1000,
        "columns": 16,
    },

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
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "days": 366,
        "observations": 1000,
        "daily_rows": 345,
        "monthly_rows": 13,

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
        ],
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

        "top_products_by_quantity": [
            {
                "Product Category": "Clothing",
                "Quantity": 939,
            },
            {
                "Product Category": "Electronics",
                "Quantity": 882,
            },
            {
                "Product Category": "Beauty",
                "Quantity": 811,
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


EDA_VALIDATION = {
    "overall_status": "PASSED",
    "total_checks": 5,
    "passed": 5,
    "warnings": 0,
    "failed": 0,
}


CLEANING_RESULT = {
    "status": "validated",
    "cleaned_rows": 1000,
    "rows_removed": 0,
    "execution_logs": 3,
}


CLEANING_VALIDATION = {
    "overall_status": "PASSED",
    "total_checks": 9,
    "passed": 9,
    "warnings": 0,
    "failed": 0,
}


VISUALIZATION_RESULT = {
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
        "total_sales",
        "total_quantity",
        "total_orders",
        "total_customers",
        "average_order_value",
        "average_quantity_per_order",
        "average_selling_price",
    ],

    "charts": [
        {
            "chart_id": "daily_sales",
            "title": "Daily Sales Trend",
            "chart_type": "line",
        },
        {
            "chart_id": "monthly_sales",
            "title": "Monthly Sales Trend",
            "chart_type": "line",
        },
        {
            "chart_id": "product_sales",
            "title": "Sales by Product Category",
            "chart_type": "bar",
        },
        {
            "chart_id": "product_quantity",
            "title": "Quantity by Product Category",
            "chart_type": "bar",
        },
        {
            "chart_id": "regional_sales",
            "title": "Sales by Region",
            "chart_type": "horizontal_bar",
        },
        {
            "chart_id": "customer_sales",
            "title": "Top Customers by Sales",
            "chart_type": "horizontal_bar",
        },
    ],

    "total_charts": 6,

    "validation": {
        "overall_status": "PASSED",
    },
}


VISUALIZATION_VALIDATION = {
    "overall_status": "PASSED",
    "total_checks": 4,
    "passed": 4,
    "warnings": 0,
    "failed": 0,
}


FORECASTING_RESULT = {
    "status": "completed",

    "eligibility": {
        "eligible": True,
        "date_column": "Date",
        "sales_column": "Total Amount",
        "observations": 1000,
        "unique_dates": 345,
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "frequency": "D",
        "date_valid": True,
        "sales_valid": True,
        "sufficient_history": True,
        "consistent_series": True,
        "acceptable_quality": True,
        "reasons": [
            "Dataset satisfies the minimum forecasting eligibility criteria."
        ],
    },

    "evaluation": {
        "frequency": "D",
        "test_size": 30,

        "results": {
            "naive": {
                "model_name": "Naive",
                "status": "completed",
                "mae": 1678.3333333333333,
                "rmse": 1871.4922744519502,
                "mape": 451.423574637261,
            },

            "moving_average": {
                "model_name": "Moving Average",
                "status": "completed",
                "mae": 805.7619047619047,
                "rmse": 1038.9390519859653,
                "mape": 147.47554269285817,
            },

            "exponential_smoothing": {
                "model_name": "Exponential Smoothing",
                "status": "completed",
                "mae": 786.807443202053,
                "rmse": 1001.4497865090984,
                "mape": 164.09613308666513,
            },

            "arima": {
                "model_name": "ARIMA",
                "status": "completed",
                "mae": 785.3988254596835,
                "rmse": 995.0,
                "mape": 160.0,
            },
        },

        "best_model": "ARIMA",
        "best_mae": 785.3988254596835,
    },

    "forecast_values": [
        {
            "date": "2024-01-02",
            "forecast": 1500.0,
        },
        {
            "date": "2024-01-03",
            "forecast": 1510.0,
        },
        {
            "date": "2024-01-04",
            "forecast": 1520.0,
        },
    ],

    "validation": {
        "overall_status": "PASSED",
        "total_checks": 5,
        "passed": 5,
        "warnings": 0,
        "failed": 0,
    },
}


INSIGHT_RESULT = {
    "status": "completed",

    "insights": [
        {
            "insight_type": "sales_performance",
            "title": "Overall Sales Performance",
            "statement": (
                "Total sales were 476160.0 across the observed dataset."
            ),
            "evidence": {
                "source": "validated_kpis",
                "metric": "total_sales",
                "value": 476160.0,
            },
            "confidence": 0.95,
        },

        {
            "insight_type": "product_performance",
            "title": "Leading Product Category",
            "statement": (
                "Electronics generated the highest observed sales "
                "among the product categories."
            ),
            "evidence": {
                "source": "validated_rankings",
                "category": "Electronics",
                "sales": 166955,
            },
            "confidence": 0.95,
        },

        {
            "insight_type": "regional_performance",
            "title": "Leading Region",
            "statement": (
                "San Francisco recorded the highest observed regional sales."
            ),
            "evidence": {
                "source": "validated_rankings",
                "region": "San Francisco",
                "sales": 71335,
            },
            "confidence": 0.95,
        },

        {
            "insight_type": "customer_concentration",
            "title": "High-Value Customer",
            "statement": (
                "CUST015 was the highest-sales customer in the observed data."
            ),
            "evidence": {
                "source": "validated_rankings",
                "customer": "CUST015",
                "sales": 5000,
            },
            "confidence": 0.90,
        },

        {
            "insight_type": "forecast_performance",
            "title": "Forecast Model Performance",
            "statement": (
                "ARIMA achieved the lowest MAE among the evaluated "
                "forecasting models."
            ),
            "evidence": {
                "source": "validated_forecasting",
                "best_model": "ARIMA",
                "best_mae": 785.3988254596835,
            },
            "confidence": 0.85,
        },
    ],
}


INSIGHT_VALIDATION = {
    "overall_status": "PASSED",
    "total_checks": 12,
    "passed": 12,
    "warnings": 0,
    "failed": 0,
}


RECOMMENDATION_RESULT = {
    "status": "completed",

    "recommendations": [
        {
            "recommendation_id": "REC-PRODUCT-001",
            "recommendation_type": "Product",
            "title": "Review Electronics Performance",
            "evidence": {
                "source": "validated_rankings",
                "sales": 166955,
            },
            "insight": (
                "Electronics generated the highest observed sales."
            ),
            "business_implication": (
                "The category represents an important observed "
                "sales contributor."
            ),
            "recommendation": (
                "Review demand, inventory availability and continued "
                "sales performance for Electronics."
            ),
            "priority": "HIGH",
            "confidence": 0.95,
            "limitations": [],
            "validation_status": "PASSED",
        },

        {
            "recommendation_id": "REC-CUSTOMER-002",
            "recommendation_type": "Customer",
            "title": "Prioritise High-Value Customer Retention",
            "evidence": {
                "source": "validated_rankings",
                "customer": "CUST015",
                "sales": 5000,
            },
            "insight": (
                "CUST015 was the highest-sales customer."
            ),
            "business_implication": (
                "High-value customers may warrant focused engagement."
            ),
            "recommendation": (
                "Prioritise retention and engagement strategies for "
                "consistently high-value customers."
            ),
            "priority": "HIGH",
            "confidence": 0.90,
            "limitations": [],
            "validation_status": "PASSED",
        },

        {
            "recommendation_id": "REC-REGIONAL-003",
            "recommendation_type": "Regional",
            "title": "Review Regional Performance",
            "evidence": {
                "source": "validated_rankings",
                "region": "San Francisco",
                "sales": 71335,
            },
            "insight": (
                "San Francisco recorded the highest regional sales."
            ),
            "business_implication": (
                "The region is a strong observed sales market."
            ),
            "recommendation": (
                "Review factors associated with strong regional "
                "performance and consider whether successful practices "
                "can be applied to other regions."
            ),
            "priority": "HIGH",
            "confidence": 0.95,
            "limitations": [],
            "validation_status": "PASSED",
        },

        {
            "recommendation_id": "REC-FORECAST-004",
            "recommendation_type": "Forecast",
            "title": "Use Forecast for Planning",
            "evidence": {
                "source": "validated_forecasting",
                "best_model": "ARIMA",
                "best_mae": 785.3988254596835,
            },
            "insight": (
                "ARIMA achieved the lowest MAE."
            ),
            "business_implication": (
                "The validated forecast can support planning decisions."
            ),
            "recommendation": (
                "Use the forecast as a planning input and review "
                "inventory, staffing and operational capacity."
            ),
            "priority": "MEDIUM",
            "confidence": 0.85,
            "limitations": [],
            "validation_status": "PASSED",
        },
    ],
}


RECOMMENDATION_VALIDATION = {
    "overall_status": "PASSED",
    "total_checks": 56,
    "passed": 56,
    "warnings": 0,
    "failed": 0,
}


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
# TEST UTILITIES
# =====================================================================

def check(condition: bool, message: str) -> None:
    """Raise AssertionError with a readable message."""
    if not condition:
        raise AssertionError(message)


def print_pass(label: str) -> None:
    print(f"{label}: PASSED")


# =====================================================================
# MAIN TEST
# =====================================================================

def main() -> None:

    print("=" * 70)
    print("8.8.1 REPORT GENERATOR TEST")
    print("=" * 70)
    print()

    # ---------------------------------------------------------------
    # INPUT PREPARATION
    # ---------------------------------------------------------------

    print("INPUT PREPARATION")

    check(
        isinstance(EDA_RESULT, dict),
        "EDA result must be a dictionary.",
    )
    print_pass("EDA Result")

    check(
        isinstance(VISUALIZATION_RESULT, dict),
        "Visualization result must be a dictionary.",
    )
    print_pass("Visualization Result")

    check(
        isinstance(FORECASTING_RESULT, dict),
        "Forecasting result must be a dictionary.",
    )
    print_pass("Forecasting Result")

    check(
        isinstance(INSIGHT_RESULT, dict),
        "Insight result must be a dictionary.",
    )
    print_pass("Insight Result")

    check(
        isinstance(RECOMMENDATION_RESULT, dict),
        "Recommendation result must be a dictionary.",
    )
    print_pass("Recommendation Result")

    print()

    # ---------------------------------------------------------------
    # INDIVIDUAL SECTION BUILDERS
    # ---------------------------------------------------------------

    print("SECTION BUILDERS")

    executive_summary = build_executive_summary(
        eda_result=EDA_RESULT,
        forecasting_result=FORECASTING_RESULT,
        insight_result=INSIGHT_RESULT,
        recommendation_result=RECOMMENDATION_RESULT,
    )

    check(
        isinstance(executive_summary, str)
        and bool(executive_summary.strip()),
        "Executive summary was not generated.",
    )
    print_pass("Executive Summary")

    dataset_overview = build_dataset_overview(
        EDA_RESULT,
        SEMANTIC_MAPPING,
    )

    check(
        dataset_overview.get("rows") == 1000,
        "Dataset row count is incorrect.",
    )
    check(
        dataset_overview.get("columns") == 16,
        "Dataset column count is incorrect.",
    )
    print_pass("Dataset Overview")

    data_quality = build_data_quality_section(
        CLEANING_RESULT,
        CLEANING_VALIDATION,
    )

    check(
        isinstance(data_quality, dict),
        "Data quality section is invalid.",
    )
    print_pass("Data Quality Section")

    kpis = build_kpi_section(
        EDA_RESULT
    )

    check(
        kpis.get("total_sales") == 476160.0,
        "Total sales KPI is incorrect.",
    )
    check(
        kpis.get("total_orders") == 1000,
        "Total orders KPI is incorrect.",
    )
    print_pass("KPI Section")

    trends = build_trend_section(
        EDA_RESULT
    )

    check(
        isinstance(trends, dict),
        "Trend section is invalid.",
    )
    check(
        len(trends.get("monthly_sales", [])) == 13,
        "Monthly trend result count is incorrect.",
    )
    print_pass("Trend Section")

    rankings = build_ranking_section(
        EDA_RESULT
    )

    check(
        "top_products_by_sales" in rankings,
        "Product ranking is missing.",
    )
    check(
        "top_regions_by_sales" in rankings,
        "Regional ranking is missing.",
    )
    check(
        "top_customers_by_sales" in rankings,
        "Customer ranking is missing.",
    )
    print_pass("Ranking Section")

    visualizations = build_visualization_section(
        VISUALIZATION_RESULT
    )

    check(
        visualizations.get("total_charts") == 6,
        "Chart count is incorrect.",
    )
    print_pass("Visualization Section")

    forecast = build_forecast_section(
        FORECASTING_RESULT
    )

    check(
        forecast.get("status") == "completed",
        "Forecast status is incorrect.",
    )
    check(
        forecast.get("evaluation", {}).get("best_model")
        == "ARIMA",
        "Best forecasting model is incorrect.",
    )
    print_pass("Forecast Section")

    insights = build_insights_section(
        INSIGHT_RESULT
    )

    check(
        len(insights) == 5,
        "Insight count is incorrect.",
    )
    print_pass("Insight Section")

    recommendations = build_recommendations_section(
        RECOMMENDATION_RESULT
    )

    check(
        len(recommendations) == 4,
        "Recommendation count is incorrect.",
    )
    print_pass("Recommendation Section")

    limitations = build_limitations(
        capabilities=CAPABILITIES,
        forecasting_result=FORECASTING_RESULT,
        visualization_result=VISUALIZATION_RESULT,
        eda_result=EDA_RESULT,
    )

    check(
        isinstance(limitations, list),
        "Limitations must be a list.",
    )
    print_pass("Limitations")

    print()

    # ---------------------------------------------------------------
    # COMPLETE REPORT GENERATION
    # ---------------------------------------------------------------

    print("REPORT GENERATION")

    report = generate_report(
        eda_result=EDA_RESULT,
        visualization_result=VISUALIZATION_RESULT,
        forecasting_result=FORECASTING_RESULT,
        insight_result=INSIGHT_RESULT,
        recommendation_result=RECOMMENDATION_RESULT,
        semantic_mapping=SEMANTIC_MAPPING,
        capabilities=CAPABILITIES,
        cleaning_result=CLEANING_RESULT,
        cleaning_validation=CLEANING_VALIDATION,
        eda_validation=EDA_VALIDATION,
        visualization_validation=VISUALIZATION_VALIDATION,
        insight_validation=INSIGHT_VALIDATION,
        recommendation_validation=RECOMMENDATION_VALIDATION,
    )

    check(
        isinstance(report, dict),
        "Generated report must be a dictionary.",
    )

    sections = report.get("sections", [])

    print(f"Total Sections: {len(sections)}")

    check(
        len(sections) == 10,
        "Report must contain exactly 10 sections.",
    )

    print_pass("Report Section Count")

    print()

    # ---------------------------------------------------------------
    # REPORT SECTION COVERAGE
    # ---------------------------------------------------------------

    print("REPORT SECTION COVERAGE")

    section_ids = {
        section.get("section_id")
        for section in sections
        if isinstance(section, dict)
    }

    expected_sections = {
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

    check(
        expected_sections.issubset(section_ids),
        (
            "Missing report sections: "
            f"{sorted(expected_sections - section_ids)}"
        ),
    )

    section_labels = {
        "dataset_overview": "Dataset Overview",
        "data_quality": "Data Quality",
        "kpis": "KPIs",
        "trends": "Trends",
        "rankings": "Rankings",
        "visualizations": "Visualizations",
        "forecast": "Forecast",
        "insights": "Insights",
        "recommendations": "Recommendations",
        "limitations": "Limitations",
    }

    for section_id, label in section_labels.items():
        if section_id in section_ids:
            print_pass(label)

    print()

    # ---------------------------------------------------------------
    # EVIDENCE GROUNDING
    # ---------------------------------------------------------------

    print("EVIDENCE GROUNDING")

    evidence_sources = set(
        report.get("evidence_sources", [])
    )

    required_sources = {
        "validated_eda",
        "validated_cleaning",
        "validated_kpis",
        "validated_trends",
        "validated_rankings",
        "validated_visualizations",
        "validated_forecasting",
        "validated_insights",
        "validated_recommendations",
        "workflow_context",
    }

    check(
        required_sources.issubset(evidence_sources),
        (
            "Missing evidence sources: "
            f"{sorted(required_sources - evidence_sources)}"
        ),
    )

    print_pass("Evidence Source Traceability")

    forecast_section = next(
        section
        for section in sections
        if section.get("section_id") == "forecast"
    )

    check(
        forecast_section.get("evidence_source")
        == "validated_forecasting",
        "Forecast evidence is not correctly traced.",
    )

    print_pass("Forecast Evidence")

    insight_section = next(
        section
        for section in sections
        if section.get("section_id") == "insights"
    )

    check(
        insight_section.get("evidence_source")
        == "validated_insights",
        "Insight evidence is not correctly traced.",
    )

    print_pass("Insight Evidence")

    recommendation_section = next(
        section
        for section in sections
        if section.get("section_id") == "recommendations"
    )

    check(
        recommendation_section.get("evidence_source")
        == "validated_recommendations",
        "Recommendation evidence is not correctly traced.",
    )

    print_pass("Recommendation Evidence")

    print()

    # ---------------------------------------------------------------
    # UNSUPPORTED CLAIM PROTECTION
    # ---------------------------------------------------------------

    print("UNSUPPORTED CLAIM PROTECTION")

    limitations_text = " ".join(
        str(item)
        for item in report.get("limitations", [])
    ).lower()

    check(
        "profitability analysis is unavailable"
        in limitations_text,
        "Missing profitability limitation disclosure.",
    )

    print_pass("No Invented Profitability Metric")

    check(
        CAPABILITIES["profitability_analysis"] is False,
        "Profitability capability test setup is incorrect.",
    )

    print_pass("Capability Limitation Disclosure")

    # The report must not create a profit/profitability KPI.
    report_text = str(report).lower()

    check(
        "profit" not in report.get(
            "executive_summary",
            ""
        ).lower(),
        "Unsupported profitability claim found in executive summary.",
    )

    print_pass("Unsupported Profit Claim Protection")

    print()

    # ---------------------------------------------------------------
    # REPORT VALIDATION
    # ---------------------------------------------------------------

    print("REPORT VALIDATION")

    validation = validate_report(
        report
    )

    check(
        validation.get("overall_status") == "PASSED",
        (
            "Report validation failed: "
            f"{validation}"
        ),
    )

    print(
        f"Overall Status: {validation.get('overall_status')}"
    )
    print(
        f"Total Checks: {validation.get('total_checks')}"
    )
    print(
        f"Passed: {validation.get('passed')}"
    )
    print(
        f"Failed: {validation.get('failed')}"
    )
    print(
        f"Warnings: {validation.get('warnings')}"
    )

    print_pass("Report Validation")

    print()

    # ---------------------------------------------------------------
    # SERIALIZATION
    # ---------------------------------------------------------------

    print("SERIALIZATION")

    serialized = serialize_report(
        report
    )

    check(
        isinstance(serialized, dict),
        "Serialized report must be a dictionary.",
    )

    check(
        serialized.get("title")
        == "Sales Intelligence Report",
        "Serialized report title is incorrect.",
    )

    print_pass("Report Serialization")

    print()

    # ---------------------------------------------------------------
    # CONVENIENCE PIPELINE
    # ---------------------------------------------------------------

    print("CONVENIENCE PIPELINE")

    pipeline_report = build_report(
        eda_result=EDA_RESULT,
        visualization_result=VISUALIZATION_RESULT,
        forecasting_result=FORECASTING_RESULT,
        insight_result=INSIGHT_RESULT,
        recommendation_result=RECOMMENDATION_RESULT,
        semantic_mapping=SEMANTIC_MAPPING,
        capabilities=CAPABILITIES,
        cleaning_result=CLEANING_RESULT,
        cleaning_validation=CLEANING_VALIDATION,
        eda_validation=EDA_VALIDATION,
        visualization_validation=VISUALIZATION_VALIDATION,
        insight_validation=INSIGHT_VALIDATION,
        recommendation_validation=RECOMMENDATION_VALIDATION,
    )

    check(
        isinstance(pipeline_report, dict),
        "build_report() must return a dictionary.",
    )

    check(
        pipeline_report.get("validation_status")
        == "PASSED",
        "build_report() validation did not pass.",
    )

    print_pass("build_report()")
    print(
        "Validation Status:",
        pipeline_report.get("validation_status"),
    )
    print_pass("Convenience Pipeline")

    print()

    # ---------------------------------------------------------------
    # OPTIONAL FORECAST HANDLING
    # ---------------------------------------------------------------

    print("OPTIONAL FORECAST HANDLING")

    report_without_forecast = generate_report(
        eda_result=EDA_RESULT,
        visualization_result=VISUALIZATION_RESULT,
        forecasting_result=None,
        insight_result=INSIGHT_RESULT,
        recommendation_result=RECOMMENDATION_RESULT,
        semantic_mapping=SEMANTIC_MAPPING,
        capabilities=CAPABILITIES,
        cleaning_result=CLEANING_RESULT,
        cleaning_validation=CLEANING_VALIDATION,
        eda_validation=EDA_VALIDATION,
        visualization_validation=VISUALIZATION_VALIDATION,
        insight_validation=INSIGHT_VALIDATION,
        recommendation_validation=RECOMMENDATION_VALIDATION,
    )

    forecast_without_result = next(
        section
        for section in report_without_forecast["sections"]
        if section.get("section_id") == "forecast"
    )

    check(
        forecast_without_result["content"]["status"]
        == "NOT_AVAILABLE",
        "Optional forecast handling failed.",
    )

    print_pass("Forecast Not Available Handling")

    print()

    # ---------------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------------

    print("=" * 70)
    print("8.8.1 REPORT GENERATOR TEST: PASSED")
    print("=" * 70)


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    main()