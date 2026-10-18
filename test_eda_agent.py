"""
Test EDA Agent
"""

import pandas as pd

from agents.planner_agent import PlannerAgent
from agents.eda_agent import EDAAgent


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
print("                   EDA AGENT TEST")
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
# Cleaning validation
# ---------------------------------------------------------

print("\nUSING CLEANING VALIDATION")
print("-" * 60)

cleaning_validation = {
    "overall_status": "PASSED"
}

print(
    "Cleaning Validation:",
    cleaning_validation[
        "overall_status"
    ]
)


# ---------------------------------------------------------
# Initialise EDA Agent
# ---------------------------------------------------------

print("\nINITIALISING EDA AGENT")
print("-" * 60)

eda_agent = EDAAgent(
    df=df,
    semantic_mapping=semantic_mapping,
    cleaning_validation=cleaning_validation
)

print(
    "EDA Agent Status:",
    eda_agent.status
)


# ---------------------------------------------------------
# Run EDA
# ---------------------------------------------------------

print("\nRUNNING EDA WORKFLOW")
print("-" * 60)

result = eda_agent.run(
    top_n=10
)

print(
    "EDA Agent Status:",
    result["status"]
)


# ---------------------------------------------------------
# KPI results
# ---------------------------------------------------------

print("\nKPI RESULTS")
print("-" * 60)

for key, value in result[
    "kpis"
].items():

    print(
        f"{key}: {value}"
    )


# ---------------------------------------------------------
# Trend results
# ---------------------------------------------------------

print("\nTREND RESULTS")
print("-" * 60)

trends = result[
    "trends"
]

print(
    "Trend Status:",
    trends.get(
        "status",
        "available"
    )
)

coverage = trends.get(
    "date_coverage",
    {}
)

print(
    f"Start Date: "
    f"{coverage.get('start_date')}"
)

print(
    f"End Date: "
    f"{coverage.get('end_date')}"
)

print(
    f"Observations: "
    f"{coverage.get('observations')}"
)

monthly_sales = trends.get(
    "monthly_sales"
)

if isinstance(
    monthly_sales,
    pd.DataFrame
):

    print(
        f"Monthly Sales Rows: "
        f"{len(monthly_sales)}"
    )


# ---------------------------------------------------------
# Ranking results
# ---------------------------------------------------------

print("\nRANKING RESULTS")
print("-" * 60)

rankings = result[
    "rankings"
]

for key, dataframe in rankings.items():

    print(
        f"\n{key}:"
    )

    if isinstance(
        dataframe,
        pd.DataFrame
    ):

        print(
            dataframe.head(5).to_string(
                index=False
            )
        )


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

print("\nEDA VALIDATION")
print("-" * 60)

validation = result[
    "validation"
]

print(
    "Overall Status:",
    validation.get(
        "overall_status"
    )
)

print(
    "Total Checks:",
    validation.get(
        "total_checks"
    )
)

print(
    "Passed:",
    validation.get(
        "passed_checks"
    )
)

print(
    "Warnings:",
    validation.get(
        "warning_checks"
    )
)

print(
    "Failed:",
    validation.get(
        "failed_checks"
    )
)

print(
    "\nIndividual Checks:"
)

for check in validation.get(
    "checks",
    []
):

    print(
        f"- {check['check']}: "
        f"{check['status']}"
    )


# ---------------------------------------------------------
# Final checks
# ---------------------------------------------------------

print("\nFINAL EDA CHECKS")
print("-" * 60)

if result["status"] == "completed":
    print(
        "EDA Agent execution: PASSED"
    )
else:
    print(
        "EDA Agent execution: FAILED"
    )

if (
    result["kpis"].get(
        "total_sales"
    ) is not None
):
    print(
        "KPI integration: PASSED"
    )
else:
    print(
        "KPI integration: FAILED"
    )

if (
    isinstance(
        result["trends"].get(
            "monthly_sales"
        ),
        pd.DataFrame
    )
    and not result["trends"][
        "monthly_sales"
    ].empty
):
    print(
        "Trend integration: PASSED"
    )
else:
    print(
        "Trend integration: FAILED"
    )

if all(
    isinstance(
        dataframe,
        pd.DataFrame
    )
    and not dataframe.empty
    for dataframe in result[
        "rankings"
    ].values()
):
    print(
        "Ranking integration: PASSED"
    )
else:
    print(
        "Ranking integration: FAILED"
    )


print("\n" + "=" * 60)
print("              EDA AGENT TEST COMPLETED")
print("=" * 60)