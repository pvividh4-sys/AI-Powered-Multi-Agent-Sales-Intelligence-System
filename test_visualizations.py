
"""
Test Visualization Analytics

Runs the visualization pipeline and validates KPI cards,
chart generation, chart files, and expected visualization coverage.

Compatible with:
    python test_visualizations.py
    python -m pytest test_visualizations.py -v
"""

import os

import matplotlib
matplotlib.use("Agg")

import pandas as pd
import pytest

from agents.planner_agent import PlannerAgent
from agents.eda_agent import EDAAgent
from analytics.visualizations import VisualizationAnalyzer


DATASET_PATH = "data/sample/Retail Sales Dataset.csv"
OUTPUT_DIR = "outputs/test_visualizations"

EXPECTED_TITLES = {
    "Daily Sales Trend",
    "Monthly Sales Trend",
    "Sales by Product Category",
    "Quantity by Product Category",
    "Sales by Region",
    "Top Customers by Sales",
}


def get_value(obj, key, default=None):
    """Read a value from either a dictionary or an object."""
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def run_visualization_pipeline():
    """Run the Planner, EDA, and visualization pipeline."""

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    print("=" * 60)
    print("           VISUALIZATION ANALYTICS TEST")
    print("=" * 60)

    # 1. Load dataset
    print("\nLOADING DATASET")
    print("-" * 60)

    df = pd.read_csv(DATASET_PATH)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    if df.empty:
        raise AssertionError("The input dataset is empty.")

    # 2. Planner
    print("\nRUNNING PLANNER")
    print("-" * 60)

    planner = PlannerAgent()
    planner_result = planner.run(df)

    planner_status = get_value(
        planner_result, "status"
    )

    semantic_mapping = get_value(
        planner_result, "semantic_mapping", {}
    )

    print("Planner Status:", planner_status)

    if planner_status != "completed":
        raise AssertionError(
            f"Planner did not complete: {planner_status}"
        )

    # 3. EDA
    print("\nRUNNING EDA")
    print("-" * 60)

    eda_agent = EDAAgent(
        df=df,
        semantic_mapping=semantic_mapping,
        cleaning_validation={
            "overall_status": "PASSED"
        },
    )

    eda_result = eda_agent.run(top_n=10)

    print("EDA Status:", eda_result["status"])

    if eda_result.get("status") != "completed":
        raise AssertionError(
            f"EDA did not complete: {eda_result.get('status')}"
        )

    # 4. Initialise visualization analyzer
    print("\nINITIALISING VISUALIZATION ANALYZER")
    print("-" * 60)

    visualization_analyzer = VisualizationAnalyzer(
        eda_result=eda_result,
        output_dir=OUTPUT_DIR,
    )

    # 5. KPI cards
    print("\nKPI CARDS")
    print("-" * 60)

    kpi_cards = visualization_analyzer.create_kpi_cards()

    print(f"KPI Cards: {len(kpi_cards)}")

    for card in kpi_cards:
        print(f"{card['label']}: {card['value']}")

    if not kpi_cards:
        raise AssertionError(
            "KPI card generation returned no cards."
        )

    # 6. Generate charts
    print("\nGENERATING CHARTS")
    print("-" * 60)

    result = visualization_analyzer.generate_all()

    print("Visualization Status:", result.get("status"))
    print("Total Charts:", result.get("total_charts"))

    if result.get("status") != "completed":
        raise AssertionError(
            "Visualization generation did not complete: "
            f"{result.get('status')}"
        )

    charts = result.get("charts", [])

    # 7. Chart details
    print("\nGENERATED CHARTS")
    print("-" * 60)

    for chart in charts:
        print(f"Title: {chart.get('title')}")
        print(f"Type: {chart.get('chart_type')}")
        print(f"Rows Used: {chart.get('rows_used')}")
        print(f"Path: {chart.get('path')}")
        print(
            "File Exists:",
            os.path.exists(chart.get("path", "")),
        )
        print("-" * 40)

    # 8. Validation
    print("\nVISUALIZATION VALIDATION")
    print("-" * 60)

    print("KPI card generation: PASSED")

    if not charts:
        raise AssertionError(
            "Chart generation returned no charts."
        )

    print("Chart generation: PASSED")

    missing_files = [
        chart.get("path", "")
        for chart in charts
        if not chart.get("path")
        or not os.path.isfile(chart["path"])
    ]

    if missing_files:
        raise AssertionError(
            f"Some chart files are missing: {missing_files}"
        )

    print("Chart file validation: PASSED")

    actual_titles = {
        chart.get("title")
        for chart in charts
    }

    missing_titles = EXPECTED_TITLES - actual_titles

    if missing_titles:
        raise AssertionError(
            "Expected visualization titles are missing: "
            f"{sorted(missing_titles)}"
        )

    print("Visualization coverage: PASSED")

    print("\n" + "=" * 60)
    print("       VISUALIZATION ANALYTICS TEST COMPLETED")
    print("=" * 60)

    return {
        "dataframe": df,
        "planner_result": planner_result,
        "eda_result": eda_result,
        "kpi_cards": kpi_cards,
        "result": result,
        "charts": charts,
        "actual_titles": actual_titles,
    }


# Cache the pipeline result for this test module so the expensive
# analysis and chart generation run only once during pytest.
@pytest.fixture(scope="module")
def visualization_output():
    return run_visualization_pipeline()


def test_planner_and_eda_complete(visualization_output):
    """Verify the upstream analytics agents completed."""
    assert get_value(
        visualization_output["planner_result"], "status"
    ) == "completed"

    assert (
        visualization_output["eda_result"].get("status")
        == "completed"
    )


def test_kpi_cards_are_generated(visualization_output):
    """Verify that at least one KPI card is generated."""
    assert len(visualization_output["kpi_cards"]) > 0


def test_charts_are_generated(visualization_output):
    """Verify chart generation returns at least one chart."""
    result = visualization_output["result"]

    assert result.get("status") == "completed"
    assert result.get("total_charts", 0) > 0
    assert len(visualization_output["charts"]) > 0


def test_chart_files_exist(visualization_output):
    """Verify all generated chart files exist."""
    for chart in visualization_output["charts"]:
        path = chart.get("path")

        assert path, f"Chart has no output path: {chart}"
        assert os.path.isfile(path), (
            f"Chart file does not exist: {path}"
        )


def test_expected_visualization_coverage(visualization_output):
    """Verify all six expected chart titles are present."""
    actual_titles = visualization_output["actual_titles"]

    missing_titles = EXPECTED_TITLES - actual_titles

    assert not missing_titles, (
        f"Missing expected chart titles: {sorted(missing_titles)}"
    )


if __name__ == "__main__":
    run_visualization_pipeline()
