"""
Test KPI Analytics
"""

import pandas as pd

from agents.planner_agent import PlannerAgent
from cleaning.detection import DataQualityDetector
from cleaning.decisions import CleaningDecisionEngine
from cleaning.execution import CleaningExecutionEngine
from cleaning.validation import CleaningValidationEngine

from analytics.kpis import KPIAnalyzer


DATASET_PATH = (
    "data/sample/Retail Sales Dataset.csv"
)


def get_value(obj, key, default=None):
    """
    Supports both dictionaries and dataclass objects.
    """

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(
        obj,
        key,
        default
    )


print("=" * 60)
print("                 KPI ANALYTICS TEST")
print("=" * 60)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("\nLOADING DATASET")
print("-" * 60)

df = pd.read_csv(DATASET_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


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
# Display mapping
# ---------------------------------------------------------

print("\nSEMANTIC MAPPING")
print("-" * 60)

for semantic_name, mapping in semantic_mapping.items():

    if isinstance(mapping, dict):
        column = mapping.get("column")
        confidence = mapping.get(
            "confidence"
        )
    else:
        column = mapping
        confidence = None

    print(
        f"{semantic_name}: "
        f"{column} | "
        f"confidence: {confidence}"
    )


# ---------------------------------------------------------
# Run existing cleaning workflow
# ---------------------------------------------------------

print("\nRUNNING CLEANING WORKFLOW")
print("-" * 60)

detector = DataQualityDetector(
    df,
    semantic_mapping=semantic_mapping
)

issues = detector.detect_all()

decision_engine = CleaningDecisionEngine()

decisions = decision_engine.create_decisions(
    issues
)

execution_engine = CleaningExecutionEngine(
    df
)

# High-risk decisions are intentionally skipped
# because no user approval is provided.
for decision in decisions:

    requires_approval = get_value(
        decision,
        "requires_approval",
        False
    )

    if requires_approval:
        get_value(
            decision,
            "user_decision"
        )

    else:
        try:
            if isinstance(decision, dict):
                decision["user_decision"] = "APPROVE"
            else:
                decision.user_decision = "APPROVE"
        except Exception:
            pass

cleaned_df = execution_engine.execute_decisions(
    decisions
)

execution_logs = (
    execution_engine.get_execution_logs()
)

print(
    "Cleaned Rows:",
    len(cleaned_df)
)

print(
    "Execution Logs:",
    len(execution_logs)
)


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

print("\nVALIDATING CLEANED DATA")
print("-" * 60)

date_mapping = semantic_mapping.get(
    "date"
)

if isinstance(date_mapping, dict):
    date_column = date_mapping.get(
        "column"
    )
else:
    date_column = date_mapping

validator = CleaningValidationEngine(
    original_df=df,
    cleaned_df=cleaned_df,
    execution_logs=execution_logs,
    semantic_mapping=semantic_mapping
)

validation_result = validator.validate_all(
    date_column=date_column
)

print(
    "Validation Status:",
    validation_result.get(
        "overall_status"
    )
)


# ---------------------------------------------------------
# KPI Analysis
# ---------------------------------------------------------

print("\nRUNNING KPI ANALYSIS")
print("-" * 60)

kpi_analyzer = KPIAnalyzer(
    df=cleaned_df,
    semantic_mapping=semantic_mapping
)

kpis = kpi_analyzer.calculate_all()


# ---------------------------------------------------------
# Display KPI results
# ---------------------------------------------------------

print("\nKPI RESULTS")
print("-" * 60)

for name, value in kpis.items():

    print(
        f"{name}: {value}"
    )


# ---------------------------------------------------------
# Basic checks
# ---------------------------------------------------------

print("\nKPI VALIDATION")
print("-" * 60)

if kpis["total_sales"] is not None:
    print("Total Sales: PASSED")
else:
    print("Total Sales: FAILED")

if kpis["total_quantity"] is not None:
    print("Total Quantity: PASSED")
else:
    print("Total Quantity: FAILED")

if kpis["total_orders"] > 0:
    print("Total Orders: PASSED")
else:
    print("Total Orders: FAILED")

if kpis["total_customers"] is not None:
    print("Total Customers: PASSED")
else:
    print("Total Customers: FAILED")


print("\n" + "=" * 60)
print("             KPI ANALYTICS TEST COMPLETED")
print("=" * 60)