"""
Test Ranking Analytics
"""

import pandas as pd

from agents.planner_agent import PlannerAgent
from analytics.rankings import RankingAnalyzer


DATASET_PATH = (
    "data/sample/Retail Sales Dataset.csv"
)


def get_value(obj, key, default=None):

    if isinstance(obj, dict):
        return obj.get(
            key,
            default
        )

    return getattr(
        obj,
        key,
        default
    )


print("=" * 60)
print("               RANKING ANALYTICS TEST")
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

planner_result = planner.run(
    df
)

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
# Ranking Analyzer
# ---------------------------------------------------------

print("\nINITIALISING RANKING ANALYZER")
print("-" * 60)

analyzer = RankingAnalyzer(
    df=df,
    semantic_mapping=semantic_mapping
)


# ---------------------------------------------------------
# Product Sales
# ---------------------------------------------------------

print("\nTOP PRODUCT CATEGORIES BY SALES")
print("-" * 60)

product_sales = analyzer.product_sales(
    top_n=10
)

print(
    product_sales.to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Product Quantity
# ---------------------------------------------------------

print("\nTOP PRODUCT CATEGORIES BY QUANTITY")
print("-" * 60)

product_quantity = (
    analyzer.product_quantity(
        top_n=10
    )
)

print(
    product_quantity.to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Regional Sales
# ---------------------------------------------------------

print("\nTOP REGIONS / CITIES BY SALES")
print("-" * 60)

regional_sales = analyzer.regional_sales(
    top_n=10
)

print(
    regional_sales.to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Customer Sales
# ---------------------------------------------------------

print("\nTOP CUSTOMERS BY SALES")
print("-" * 60)

customer_sales = analyzer.customer_sales(
    top_n=10
)

print(
    customer_sales.to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Complete analysis
# ---------------------------------------------------------

print("\nRUNNING COMPLETE RANKING ANALYSIS")
print("-" * 60)

result = analyzer.analyze(
    top_n=10
)

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

print("\nRANKING VALIDATION")
print("-" * 60)

if not product_sales.empty:
    print(
        "Product sales ranking: PASSED"
    )
else:
    print(
        "Product sales ranking: FAILED"
    )

if not product_quantity.empty:
    print(
        "Product quantity ranking: PASSED"
    )
else:
    print(
        "Product quantity ranking: FAILED"
    )

if not regional_sales.empty:
    print(
        "Regional sales ranking: PASSED"
    )
else:
    print(
        "Regional sales ranking: FAILED"
    )

if not customer_sales.empty:
    print(
        "Customer sales ranking: PASSED"
    )
else:
    print(
        "Customer sales ranking: FAILED"
    )


print("\n" + "=" * 60)
print("           RANKING ANALYTICS TEST COMPLETED")
print("=" * 60)