"""
Test Visualization Agent
"""

import os

import pandas as pd

from agents.planner_agent import PlannerAgent
from agents.eda_agent import EDAAgent
from agents.visualization_agent import (
    VisualizationAgent
)


DATASET_PATH = (
    "data/sample/Retail Sales Dataset.csv"
)

OUTPUT_DIR = (
    "outputs/test_visualization_agent"
)


def get_value(
    obj,
    key,
    default=None
):

    if isinstance(
        obj,
        dict
    ):
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
print("             VISUALIZATION AGENT TEST")
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
# EDA
# ---------------------------------------------------------

print("\nRUNNING EDA")
print("-" * 60)

eda_agent = EDAAgent(
    df=df,
    semantic_mapping=semantic_mapping,
    cleaning_validation={
        "overall_status": "PASSED"
    }
)

eda_result = eda_agent.run(
    top_n=10
)

print(
    "EDA Status:",
    eda_result["status"]
)


# ---------------------------------------------------------
# Visualization Agent
# ---------------------------------------------------------

print("\nINITIALISING VISUALIZATION AGENT")
print("-" * 60)

visualization_agent = (
    VisualizationAgent(
        eda_result=eda_result,
        output_dir=OUTPUT_DIR
    )
)

print(
    "Visualization Agent Status:",
    visualization_agent.status
)


# ---------------------------------------------------------
# Run agent
# ---------------------------------------------------------

print("\nRUNNING VISUALIZATION AGENT")
print("-" * 60)

result = visualization_agent.run()

print(
    "Visualization Agent Status:",
    result["status"]
)


# ---------------------------------------------------------
# Selection
# ---------------------------------------------------------

print("\nVISUALIZATION SELECTION")
print("-" * 60)

selection = result[
    "selection"
]

print(
    "Selected Visualizations:"
)

for item in selection[
    "selected"
]:

    print(
        f"- {item}"
    )

print(
    "Total Selected:",
    selection["count"]
)


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

print("\nKPI CARDS")
print("-" * 60)

print(
    "KPI Cards:",
    len(
        result[
            "kpi_cards"
        ]
    )
)

for card in result[
    "kpi_cards"
]:

    print(
        f"- {card['label']}: "
        f"{card['value']}"
    )


# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

print("\nGENERATED CHARTS")
print("-" * 60)

print(
    "Total Charts:",
    result[
        "total_charts"
    ]
)

for chart in result[
    "charts"
]:

    print(
        f"- {chart['title']} "
        f"| {chart['chart_type']} "
        f"| rows={chart['rows_used']} "
        f"| exists={os.path.exists(chart['path'])}"
    )


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

print("\nVISUALIZATION AGENT VALIDATION")
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

print("\nFINAL VISUALIZATION CHECKS")
print("-" * 60)

if result["status"] == "completed":

    print(
        "Visualization Agent execution: PASSED"
    )

else:

    print(
        "Visualization Agent execution: FAILED"
    )


if len(
    result["kpi_cards"]
) == 7:

    print(
        "KPI card integration: PASSED"
    )

else:

    print(
        "KPI card integration: FAILED"
    )


if result[
    "total_charts"
] == 6:

    print(
        "Chart integration: PASSED"
    )

else:

    print(
        "Chart integration: FAILED"
    )


all_files_exist = all(
    os.path.exists(
        chart["path"]
    )
    for chart in result[
        "charts"
    ]
)

if all_files_exist:

    print(
        "Chart file safety: PASSED"
    )

else:

    print(
        "Chart file safety: FAILED"
    )


if validation[
    "overall_status"
] == "PASSED":

    print(
        "Visualization validation: PASSED"
    )

else:

    print(
        "Visualization validation: FAILED"
    )


print("\n" + "=" * 60)
print("          VISUALIZATION AGENT TEST COMPLETED")
print("=" * 60)