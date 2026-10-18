"""
Test Trend Analytics
"""

import pandas as pd

from agents.planner_agent import PlannerAgent
from analytics.trends import TrendAnalyzer


DATASET_PATH = (
    "data/sample/Retail Sales Dataset.csv"
)


def get_value(obj, key, default=None):

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(
        obj,
        key,
        default
    )


print("=" * 60)
print("                TREND ANALYTICS TEST")
print("=" * 60)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("\nLOADING DATASET")
print("-" * 60)

df = pd.read_csv(
    DATASET_PATH
)

print(
    f"Rows: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)


# ---------------------------------------------------------
# Planner
# ---------------------------------------------------------

print("\nRUNNING PLANNER")
print("-" * 60)

planner = PlannerAgent()

planner_result = planner.run(df)

semantic_mapping = get_value(
    planner_result,
    "semantic_mapping",
    {}
)

print(
    "Planner Status:",
    get_value(
        planner_result,
        "status"
    )
)


# ---------------------------------------------------------
# Trend Analyzer
# ---------------------------------------------------------

print("\nINITIALISING TREND ANALYZER")
print("-" * 60)

analyzer = TrendAnalyzer(
    df=df,
    semantic_mapping=semantic_mapping
)


# ---------------------------------------------------------
# Date coverage
# ---------------------------------------------------------

print("\nDATE COVERAGE")
print("-" * 60)

coverage = analyzer.date_coverage()

for key, value in coverage.items():
    print(
        f"{key}: {value}"
    )


# ---------------------------------------------------------
# Daily sales
# ---------------------------------------------------------

print("\nDAILY SALES")
print("-" * 60)

daily_sales = analyzer.daily_sales()

print(
    f"Rows: {len(daily_sales)}"
)

print(
    daily_sales.head(10).to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Daily quantity
# ---------------------------------------------------------

print("\nDAILY QUANTITY")
print("-" * 60)

daily_quantity = analyzer.daily_quantity()

print(
    f"Rows: {len(daily_quantity)}"
)

print(
    daily_quantity.head(10).to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Monthly sales
# ---------------------------------------------------------

print("\nMONTHLY SALES")
print("-" * 60)

monthly_sales = (
    analyzer.monthly_sales_with_change()
)

print(
    f"Rows: {len(monthly_sales)}"
)

print(
    monthly_sales.to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Monthly quantity
# ---------------------------------------------------------

print("\nMONTHLY QUANTITY")
print("-" * 60)

monthly_quantity = (
    analyzer.monthly_quantity()
)

print(
    f"Rows: {len(monthly_quantity)}"
)

print(
    monthly_quantity.to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Complete analysis
# ---------------------------------------------------------

print("\nRUNNING COMPLETE TREND ANALYSIS")
print("-" * 60)

result = analyzer.analyze()

print(
    "Result Keys:"
)

for key in result.keys():
    print(
        f"- {key}"
    )


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

print("\nTREND VALIDATION")
print("-" * 60)

if coverage["observations"] > 0:
    print(
        "Date observations: PASSED"
    )
else:
    print(
        "Date observations: FAILED"
    )

if not daily_sales.empty:
    print(
        "Daily sales analysis: PASSED"
    )
else:
    print(
        "Daily sales analysis: FAILED"
    )

if not monthly_sales.empty:
    print(
        "Monthly sales analysis: PASSED"
    )
else:
    print(
        "Monthly sales analysis: FAILED"
    )

if not monthly_quantity.empty:
    print(
        "Monthly quantity analysis: PASSED"
    )
else:
    print(
        "Monthly quantity analysis: FAILED"
    )


print("\n" + "=" * 60)
print("            TREND ANALYTICS TEST COMPLETED")
print("=" * 60)