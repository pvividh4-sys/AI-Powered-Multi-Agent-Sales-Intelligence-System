import os
import sys

import pandas as pd


# Allow imports from project root
sys.path.insert(
    0,
    os.path.dirname(os.path.abspath(__file__))
)

from forecasting.models import (
    prepare_time_series,
    naive_forecast,
    moving_average_forecast,
    exponential_smoothing_forecast,
    arima_forecast,
    generate_all_forecasts,
)


DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "sample",
    "Retail Sales Dataset.csv",
)


def validate_completed_forecast(
    result,
    expected_model_name,
    horizon,
):
    """Validate a successfully generated forecast."""

    assert result.model_name == expected_model_name

    assert result.frequency == "D"

    assert result.horizon == horizon

    assert result.historical_observations > 0

    assert result.status == "completed"

    assert isinstance(
        result.forecast,
        pd.DataFrame,
    )

    assert len(result.forecast) == horizon

    assert list(
        result.forecast.columns
    ) == [
        "date",
        "forecast",
    ]

    assert result.forecast["date"].notna().all()

    assert result.forecast["forecast"].notna().all()

    assert pd.api.types.is_numeric_dtype(
        result.forecast["forecast"]
    )


def main():

    print("=" * 70)
    print("8.6.2 FORECAST MODELS TEST")
    print("=" * 70)

    # =========================================================
    # 1. LOAD DATASET
    # =========================================================

    print("\n1. Loading dataset...")

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Dataset Shape: {df.shape}"
    )

    # =========================================================
    # 2. PREPARE TIME SERIES
    # =========================================================

    print("\n2. Preparing daily sales time series...")

    series = prepare_time_series(
        df=df,
        date_column="Date",
        sales_column="Total Amount",
        frequency="D",
    )

    print(
        f"Time-Series Observations: {len(series)}"
    )

    print(
        f"Start Date: {series.index.min().date()}"
    )

    print(
        f"End Date: {series.index.max().date()}"
    )

    print(
        f"Total Sales: {series.sum():.2f}"
    )

    assert isinstance(
        series,
        pd.Series,
    )

    assert len(series) > 30

    assert series.index.is_monotonic_increasing

    assert series.notna().all()

    # =========================================================
    # 3. FORECAST CONFIGURATION
    # =========================================================

    horizon = 7

    print("\n3. Forecast Configuration")
    print("-" * 70)
    print("Frequency: D")
    print(f"Horizon  : {horizon} days")

    # =========================================================
    # 4. NAIVE
    # =========================================================

    print("\n4. Naive Forecast")

    naive_result = naive_forecast(
        series=series,
        horizon=horizon,
        frequency="D",
    )

    print(
        naive_result.forecast.to_string(
            index=False
        )
    )

    validate_completed_forecast(
        naive_result,
        "Naive",
        horizon,
    )

    print("Status: PASSED")

    # =========================================================
    # 5. MOVING AVERAGE
    # =========================================================

    print("\n5. Moving Average Forecast")

    moving_average_result = (
        moving_average_forecast(
            series=series,
            horizon=horizon,
            window=7,
            frequency="D",
        )
    )

    print(
        moving_average_result.forecast.to_string(
            index=False
        )
    )

    validate_completed_forecast(
        moving_average_result,
        "Moving Average",
        horizon,
    )

    print("Status: PASSED")

    # =========================================================
    # 6. EXPONENTIAL SMOOTHING
    # =========================================================

    print("\n6. Exponential Smoothing Forecast")

    exponential_result = (
        exponential_smoothing_forecast(
            series=series,
            horizon=horizon,
            frequency="D",
        )
    )

    print(
        exponential_result.forecast.to_string(
            index=False
        )
    )

    validate_completed_forecast(
        exponential_result,
        "Exponential Smoothing",
        horizon,
    )

    print("Status: PASSED")

    # =========================================================
    # 7. ARIMA
    # =========================================================

    print("\n7. ARIMA Forecast")

    arima_result = arima_forecast(
        series=series,
        horizon=horizon,
        order=(1, 1, 1),
        frequency="D",
    )

    print(
        f"Status : {arima_result.status}"
    )

    print(
        f"Message: {arima_result.message}"
    )

    if arima_result.status == "completed":

        print(
            arima_result.forecast.to_string(
                index=False
            )
        )

        validate_completed_forecast(
            arima_result,
            "ARIMA",
            horizon,
        )

        print(
            "ARIMA Status: AVAILABLE AND PASSED"
        )

    elif arima_result.status == "unavailable":

        print(
            "ARIMA Status: UNAVAILABLE"
        )

        print(
            "This is acceptable because the environment "
            "blocks the required statsmodels native component."
        )

        assert (
            len(arima_result.forecast) == 0
        )

    else:

        raise AssertionError(
            "ARIMA unexpectedly failed instead of "
            "completing or reporting unavailable."
        )

    # =========================================================
    # 8. ALL MODELS
    # =========================================================

    print("\n8. Testing generate_all_forecasts()")

    all_results = generate_all_forecasts(
        series=series,
        horizon=horizon,
        frequency="D",
        moving_average_window=7,
        arima_order=(1, 1, 1),
    )

    expected_models = {
        "naive",
        "moving_average",
        "exponential_smoothing",
        "arima",
    }

    assert set(
        all_results.keys()
    ) == expected_models

    for model_key, result in all_results.items():

        print(
            f"- {model_key}: "
            f"{result.status}"
        )

    # Three models must always be available.
    assert (
        all_results["naive"].status
        == "completed"
    )

    assert (
        all_results["moving_average"].status
        == "completed"
    )

    assert (
        all_results["exponential_smoothing"].status
        == "completed"
    )

    # ARIMA can be completed or unavailable.
    assert (
        all_results["arima"].status
        in {
            "completed",
            "unavailable",
        }
    )

    # =========================================================
    # 9. FUTURE DATE VALIDATION
    # =========================================================

    print("\n9. Forecast Date Validation")

    last_historical_date = (
        series.index[-1]
    )

    for model_key, result in all_results.items():

        if result.status != "completed":
            continue

        forecast_dates = (
            result.forecast["date"]
        )

        assert (
            forecast_dates.iloc[0]
            > last_historical_date
        )

        assert (
            forecast_dates.is_monotonic_increasing
        )

        assert len(
            forecast_dates
        ) == horizon

        print(
            f"- {model_key}: "
            f"{forecast_dates.iloc[0].date()} "
            f"to "
            f"{forecast_dates.iloc[-1].date()}"
        )

    # =========================================================
    # 10. RESULT SERIALISATION
    # =========================================================

    print("\n10. Result Serialization")

    for model_key, result in all_results.items():

        result_dict = result.to_dict()

        assert isinstance(
            result_dict,
            dict,
        )

        assert (
            result_dict["model_name"]
            == result.model_name
        )

        assert (
            result_dict["status"]
            == result.status
        )

        assert isinstance(
            result_dict["forecast"],
            list,
        )

        print(
            f"- {model_key}: serialization PASSED"
        )

    # =========================================================
    # FINAL
    # =========================================================

    print("\n" + "=" * 70)
    print("8.6.2 FORECAST MODELS TEST: PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()