"""
Forecasting Agent Integration Test
-----------------------------------

Tests the complete Forecasting Agent pipeline:

1. Dataset loading
2. Forecast eligibility
3. Time-series preparation
4. Forecast generation
5. Model evaluation
6. Best model selection
7. Final validation
8. Result serialization
"""

from pathlib import Path

import pandas as pd

from agents.forecasting_agent import (
    ForecastingAgent,
    run_forecasting_agent,
)


# ======================================================================
# Configuration
# ======================================================================

DATASET_PATH = Path("data/sample/Retail Sales Dataset.csv")


# ======================================================================
# Helper
# ======================================================================

def print_separator():
    print("=" * 70)


# ======================================================================
# Main Test
# ======================================================================

def main():

    print_separator()
    print("8.6.4 FORECASTING AGENT TEST")
    print_separator()

    # ------------------------------------------------------------------
    # 1. Load Dataset
    # ------------------------------------------------------------------

    print("\n1. Loading dataset...")

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset Shape: {df.shape}")

    assert not df.empty, "Dataset must not be empty."

    print("Dataset loading: PASSED")

    # ------------------------------------------------------------------
    # 2. Planner Semantic Mapping
    # ------------------------------------------------------------------

    print("\n2. Preparing semantic mapping...")

    semantic_mapping = {
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

    print("Date Column : Date")
    print("Sales Column: Total Amount")
    print("Semantic mapping: PASSED")

    # ------------------------------------------------------------------
    # 3. Create Forecasting Agent
    # ------------------------------------------------------------------

    print("\n3. Creating Forecasting Agent...")

    agent = ForecastingAgent(
        horizon=7,
        test_size=30,
        moving_average_window=7,
    )

    assert agent.horizon == 7
    assert agent.test_size == 30
    assert agent.moving_average_window == 7

    print("Forecast Horizon       : 7")
    print("Evaluation Test Size   : 30")
    print("Moving Average Window  : 7")
    print("Agent creation: PASSED")

    # ------------------------------------------------------------------
    # 4. Run Forecasting Agent
    # ------------------------------------------------------------------

    print("\n4. Running Forecasting Agent...")

    result = agent.run(
        df=df,
        semantic_mapping=semantic_mapping,
    )

    print(f"Agent Status: {result.status}")

    # The dataset should be eligible for forecasting.
    assert result.status == "completed", (
        f"Forecasting Agent failed: {result.messages}"
    )

    print("Forecasting Agent execution: PASSED")

    # ------------------------------------------------------------------
    # 5. Eligibility Validation
    # ------------------------------------------------------------------

    print("\n5. Forecast Eligibility")

    eligibility = result.eligibility

    print(
        f"Eligible           : "
        f"{eligibility.get('eligible')}"
    )

    print(
        f"Date Column        : "
        f"{eligibility.get('date_column')}"
    )

    print(
        f"Sales Column       : "
        f"{eligibility.get('sales_column')}"
    )

    print(
        f"Valid Observations : "
        f"{eligibility.get('valid_observations')}"
    )

    print(
        f"Unique Dates       : "
        f"{eligibility.get('unique_dates')}"
    )

    print(
        f"Frequency          : "
        f"{eligibility.get('frequency')}"
    )

    assert eligibility.get("eligible") is True
    assert eligibility.get("date_column") == "Date"
    assert eligibility.get("sales_column") == "Total Amount"

    print("Forecast eligibility integration: PASSED")

    # ------------------------------------------------------------------
    # 6. Forecast Generation
    # ------------------------------------------------------------------

    print("\n6. Generated Forecast Models")

    forecasts = result.forecasts

    assert isinstance(forecasts, dict)
    assert len(forecasts) > 0

    completed_models = []

    for model_name, model_result in forecasts.items():

        status = model_result.get("status")

        print(
            f"{model_name.replace('_', ' ').title():25}"
            f" Status: {status}"
        )

        if status == "completed":

            completed_models.append(model_name)

            forecast = model_result.get("forecast")

            assert forecast is not None

            print(
                f"  Forecast Horizon: "
                f"{model_result.get('horizon')}"
            )

    assert len(completed_models) >= 1

    print(
        f"Completed Models: "
        f"{', '.join(completed_models)}"
    )

    print("Forecast generation integration: PASSED")

    # ------------------------------------------------------------------
    # 7. Model Evaluation
    # ------------------------------------------------------------------

    print("\n7. Model Evaluation")

    evaluation = result.evaluation

    assert isinstance(evaluation, dict)
    assert len(evaluation) > 0

    best_model = evaluation.get("best_model")
    best_mae = evaluation.get("best_mae")

    print(f"Best Model: {best_model}")
    print(f"Best MAE  : {best_mae}")

    assert best_model is not None
    assert best_mae is not None

    print("Model evaluation integration: PASSED")

    # ------------------------------------------------------------------
    # 8. Best Model Validation
    # ------------------------------------------------------------------

    print("\n8. Best Model Validation")

    assert result.best_model == best_model
    assert result.best_mae == best_mae

    assert best_model in completed_models

    print(f"Selected Model: {result.best_model}")
    print(f"Selected MAE  : {result.best_mae}")

    print("Best model selection: PASSED")

    # ------------------------------------------------------------------
    # 9. Forecast Horizon Validation
    # ------------------------------------------------------------------

    print("\n9. Forecast Horizon Validation")

    assert result.horizon == 7

    selected_forecast = forecasts[best_model]

    forecast_data = selected_forecast.get("forecast")

    assert forecast_data is not None

    if isinstance(forecast_data, pd.DataFrame):

        assert len(forecast_data) == 7

        print(
            f"Forecast Observations: "
            f"{len(forecast_data)}"
        )

    elif isinstance(forecast_data, list):

        assert len(forecast_data) == 7

        print(
            f"Forecast Observations: "
            f"{len(forecast_data)}"
        )

    else:

        raise AssertionError(
            "Forecast output must be a DataFrame or list."
        )

    print("Forecast horizon validation: PASSED")

    # ------------------------------------------------------------------
    # 10. Final Agent Validation
    # ------------------------------------------------------------------

    print("\n10. Final Forecasting Agent Validation")

    validation = result.validation

    print(
        f"Overall Status: "
        f"{validation.get('overall_status')}"
    )

    print(
        f"Total Checks  : "
        f"{validation.get('total_checks')}"
    )

    print(
        f"Passed        : "
        f"{validation.get('passed')}"
    )

    print(
        f"Failed        : "
        f"{validation.get('failed')}"
    )

    assert validation.get("overall_status") == "PASSED"
    assert validation.get("failed") == 0

    print("Final forecasting validation: PASSED")

    # ------------------------------------------------------------------
    # 11. Result Serialization
    # ------------------------------------------------------------------

    print("\n11. Result Serialization")

    serialized = result.to_dict()

    assert isinstance(serialized, dict)

    required_keys = [
        "status",
        "eligibility",
        "evaluation",
        "forecasts",
        "best_model",
        "best_mae",
        "frequency",
        "horizon",
        "validation",
        "messages",
    ]

    for key in required_keys:
        assert key in serialized, (
            f"Missing serialized key: {key}"
        )

    assert serialized["status"] == "completed"
    assert serialized["best_model"] == result.best_model
    assert serialized["horizon"] == 7

    print("Serialized keys: PASSED")
    print("Result serialization: PASSED")

    # ------------------------------------------------------------------
    # 12. Convenience Function Test
    # ------------------------------------------------------------------

    print("\n12. Convenience Function")

    wrapper_result = run_forecasting_agent(
        df=df,
        semantic_mapping=semantic_mapping,
        horizon=7,
        test_size=30,
        moving_average_window=7,
    )

    assert wrapper_result.status == "completed"

    assert (
        wrapper_result.best_model
        == result.best_model
    )

    print(
        f"Wrapper Status: "
        f"{wrapper_result.status}"
    )

    print(
        f"Wrapper Best Model: "
        f"{wrapper_result.best_model}"
    )

    print("Convenience function: PASSED")

    # ------------------------------------------------------------------
    # Final Summary
    # ------------------------------------------------------------------

    print("\n")
    print_separator()
    print("FORECASTING AGENT SUMMARY")
    print_separator()

    print(
        f"Agent Status       : {result.status}"
    )

    print(
        f"Eligibility        : "
        f"{eligibility.get('eligible')}"
    )

    print(
        f"Frequency          : "
        f"{result.frequency}"
    )

    print(
        f"Forecast Horizon   : "
        f"{result.horizon}"
    )

    print(
        f"Completed Models   : "
        f"{', '.join(completed_models)}"
    )

    print(
        f"Best Model         : "
        f"{result.best_model}"
    )

    print(
        f"Best MAE           : "
        f"{result.best_mae:.4f}"
    )

    print(
        f"Validation         : "
        f"{validation.get('overall_status')}"
    )

    print_separator()
    print("8.6.4 FORECASTING AGENT TEST: PASSED")
    print_separator()


# ======================================================================
# Entry Point
# ======================================================================

if __name__ == "__main__":
    main()