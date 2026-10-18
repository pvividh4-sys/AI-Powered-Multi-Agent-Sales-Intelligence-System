"""
8.7.1 Insight Logic / Analytical Insight Functions Test
"""

from pathlib import Path

import pandas as pd

from analytics.insights import (
    generate_all_insights,
    generate_sales_insights,
    generate_trend_insights,
    generate_product_insights,
    generate_regional_insights,
    generate_customer_insights,
    generate_forecast_insights,
    validate_insights,
)


print("=" * 70)
print("8.7.1 INSIGHT LOGIC TEST")
print("=" * 70)


# ---------------------------------------------------------------------
# Load dataset
# ---------------------------------------------------------------------

DATASET_PATH = Path(
    "data/sample/Retail Sales Dataset.csv"
)

df = pd.read_csv(DATASET_PATH)

print()
print(f"Dataset Shape: {df.shape}")

assert not df.empty
print("Dataset Load: PASSED")


# ---------------------------------------------------------------------
# Prepare validated analytical results
# ---------------------------------------------------------------------

kpi_results = {
    "total_sales": 476160.0,
    "total_quantity": 2632.0,
    "total_orders": 1000,
    "total_customers": 1000,
    "average_order_value": 476.16,
    "average_quantity_per_order": 2.632,
    "average_selling_price": 180.91185410334347,
}


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


forecasting_result = {
    "status": "completed",
    "best_model": "Exponential Smoothing",
    "best_mae": 786.807443202053,
    "horizon": 7,
}


# ---------------------------------------------------------------------
# Sales insights
# ---------------------------------------------------------------------

sales_insights = generate_sales_insights(
    kpi_results
)

assert len(sales_insights) >= 3

print()
print("SALES INSIGHTS")
print(f"Generated: {len(sales_insights)}")
print("Sales Insight Generation: PASSED")


# ---------------------------------------------------------------------
# Trend insights
# ---------------------------------------------------------------------

trend_insights = generate_trend_insights(
    trend_results
)

assert len(trend_insights) >= 3

highest = [
    insight
    for insight in trend_insights
    if insight.insight_type == "sales_trend"
    and insight.title == "Highest Sales Period"
]

assert highest
assert highest[0].value == 56450.0

partial_warning = [
    insight
    for insight in trend_insights
    if insight.insight_type == "period_warning"
]

assert partial_warning

print()
print("TREND INSIGHTS")
print(f"Generated: {len(trend_insights)}")
print("Highest Sales Period: PASSED")
print("Partial Period Protection: PASSED")


# ---------------------------------------------------------------------
# Product insights
# ---------------------------------------------------------------------

product_insights = generate_product_insights(
    ranking_results
)

assert len(product_insights) >= 1
assert product_insights[0].value == 166955.0

print()
print("PRODUCT INSIGHTS")
print(f"Generated: {len(product_insights)}")
print("Top Product Detection: PASSED")


# ---------------------------------------------------------------------
# Regional insights
# ---------------------------------------------------------------------

regional_insights = generate_regional_insights(
    ranking_results
)

assert len(regional_insights) >= 1
assert regional_insights[0].value == 71335.0

print()
print("REGIONAL INSIGHTS")
print(f"Generated: {len(regional_insights)}")
print("Top Region Detection: PASSED")


# ---------------------------------------------------------------------
# Customer insights
# ---------------------------------------------------------------------

customer_insights = generate_customer_insights(
    ranking_results
)

assert len(customer_insights) >= 1
assert customer_insights[0].value == 5000.0

print()
print("CUSTOMER INSIGHTS")
print(f"Generated: {len(customer_insights)}")
print("Top Customer Detection: PASSED")


# ---------------------------------------------------------------------
# Forecast insights
# ---------------------------------------------------------------------

forecast_insights = generate_forecast_insights(
    forecasting_result
)

assert len(forecast_insights) >= 1
assert forecast_insights[0].value == 786.807443202053

print()
print("FORECAST INSIGHTS")
print(f"Generated: {len(forecast_insights)}")
print("Best Forecast Model Integration: PASSED")


# ---------------------------------------------------------------------
# Combined insight generation
# ---------------------------------------------------------------------

all_insights = generate_all_insights(
    kpi_results=kpi_results,
    trend_results=trend_results,
    ranking_results=ranking_results,
    forecasting_result=forecasting_result,
)

assert len(all_insights) >= 10

print()
print("COMBINED INSIGHTS")
print(f"Total Insights: {len(all_insights)}")
print("Insight Integration: PASSED")


# ---------------------------------------------------------------------
# Insight validation
# ---------------------------------------------------------------------

validation = validate_insights(
    all_insights
)

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

assert validation["overall_status"] == "PASSED"
assert validation["failed"] == 0

print("Insight Validation: PASSED")


# ---------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------

serialized = [
    insight.to_dict()
    for insight in all_insights
]

assert serialized
assert isinstance(serialized[0], dict)
assert "statement" in serialized[0]
assert "evidence" in serialized[0]

print()
print("SERIALIZATION")
print("Insight Serialization: PASSED")


# ---------------------------------------------------------------------
# Final result
# ---------------------------------------------------------------------

print()
print("=" * 70)
print("8.7.1 INSIGHT LOGIC TEST: PASSED")
print("=" * 70)