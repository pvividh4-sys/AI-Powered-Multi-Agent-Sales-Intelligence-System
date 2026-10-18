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
)

from forecasting.evaluation import (
    calculate_mae,
    calculate_rmse,
    calculate_mape,
    chronological_train_test_split,
    evaluate_naive,
    evaluate_moving_average,
    evaluate_exponential_smoothing,
    evaluate_arima,
    evaluate_all_models,
)


DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "sample",
    "Retail Sales Dataset.csv",
)


def main():

    print("=" * 70)
    print("8.6.3 FORECAST EVALUATION TEST")
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

    assert len(series) > 60

    assert series.notna().all()

    assert series.index.is_monotonic_increasing

    # =========================================================
    # 3. METRIC TEST
    # =========================================================

    print("\n3. Testing Evaluation Metrics")

    actual = pd.Series(
        [100, 200, 300, 400]
    )

    predicted = pd.Series(
        [110, 190, 310, 380]
    )

    mae = calculate_mae(
        actual,
        predicted,
    )

    rmse = calculate_rmse(
        actual,
        predicted,
    )

    mape = calculate_mape(
        actual,
        predicted,
    )

    print(
        f"MAE : {mae:.4f}"
    )

    print(
        f"RMSE: {rmse:.4f}"
    )

    print(
        f"MAPE: {mape:.4f}%"
    )

    # ---------------------------------------------------------
    # Correct expected values
    # ---------------------------------------------------------

    # Errors:
    # [100-110, 200-190, 300-310, 400-380]
    # [-10, 10, -10, 20]
    #
    # MAE:
    # (10 + 10 + 10 + 20) / 4 = 12.5
    #
    # RMSE:
    # sqrt((100 + 100 + 100 + 400) / 4)
    # = sqrt(175)
    # = 13.2288...
    #
    # MAPE:
    # mean(
    #   10/100,
    #   10/200,
    #   10/300,
    #   20/400
    # ) * 100
    # = 5.8333%

    assert round(
        mae,
        4
    ) == 12.5000

    assert round(
        rmse,
        4
    ) == 13.2288

    assert round(
        mape,
        4
    ) == 5.8333

    print(
        "Metric calculations: PASSED"
    )

    # =========================================================
    # 4. CHRONOLOGICAL SPLIT
    # =========================================================

    test_size = 30

    print("\n4. Chronological Train/Test Split")

    train, test = chronological_train_test_split(
        series=series,
        test_size=test_size,
    )

    print(
        f"Training Observations: {len(train)}"
    )

    print(
        f"Testing Observations : {len(test)}"
    )

    print(
        f"Training End         : {train.index[-1].date()}"
    )

    print(
        f"Testing Start        : {test.index[0].date()}"
    )

    assert len(test) == test_size

    assert (
        len(train) + len(test)
        == len(series)
    )

    assert (
        train.index[-1]
        < test.index[0]
    )

    assert train.index.is_monotonic_increasing

    assert test.index.is_monotonic_increasing

    print(
        "Chronological split: PASSED"
    )

    # =========================================================
    # 5. NAIVE EVALUATION
    # =========================================================

    print("\n5. Naive Model Evaluation")

    naive_result = evaluate_naive(
        train=train,
        test=test,
        frequency="D",
    )

    print(
        f"Status: {naive_result.status}"
    )

    print(
        f"MAE   : {naive_result.mae:.4f}"
    )

    print(
        f"RMSE  : {naive_result.rmse:.4f}"
    )

    print(
        f"MAPE  : {naive_result.mape:.4f}%"
    )

    assert naive_result.status == "completed"

    assert naive_result.mae is not None

    assert naive_result.rmse is not None

    assert naive_result.mape is not None

    assert naive_result.mae >= 0

    assert naive_result.rmse >= 0

    assert naive_result.mape >= 0

    print(
        "Naive evaluation: PASSED"
    )

    # =========================================================
    # 6. MOVING AVERAGE EVALUATION
    # =========================================================

    print("\n6. Moving Average Evaluation")

    moving_average_result = (
        evaluate_moving_average(
            train=train,
            test=test,
            window=7,
            frequency="D",
        )
    )

    print(
        f"Status: {moving_average_result.status}"
    )

    print(
        f"MAE   : {moving_average_result.mae:.4f}"
    )

    print(
        f"RMSE  : {moving_average_result.rmse:.4f}"
    )

    print(
        f"MAPE  : {moving_average_result.mape:.4f}%"
    )

    assert (
        moving_average_result.status
        == "completed"
    )

    assert (
        moving_average_result.mae
        is not None
    )

    assert (
        moving_average_result.rmse
        is not None
    )

    assert (
        moving_average_result.mape
        is not None
    )

    assert (
        moving_average_result.mae
        >= 0
    )

    print(
        "Moving Average evaluation: PASSED"
    )

    # =========================================================
    # 7. EXPONENTIAL SMOOTHING EVALUATION
    # =========================================================

    print("\n7. Exponential Smoothing Evaluation")

    exponential_result = (
        evaluate_exponential_smoothing(
            train=train,
            test=test,
            frequency="D",
        )
    )

    print(
        f"Status: {exponential_result.status}"
    )

    print(
        f"MAE   : {exponential_result.mae:.4f}"
    )

    print(
        f"RMSE  : {exponential_result.rmse:.4f}"
    )

    print(
        f"MAPE  : {exponential_result.mape:.4f}%"
    )

    assert (
        exponential_result.status
        == "completed"
    )

    assert (
        exponential_result.mae
        is not None
    )

    assert (
        exponential_result.rmse
        is not None
    )

    assert (
        exponential_result.mape
        is not None
    )

    assert (
        exponential_result.mae
        >= 0
    )

    print(
        "Exponential Smoothing evaluation: PASSED"
    )

    # =========================================================
    # 8. ARIMA EVALUATION
    # =========================================================

    print("\n8. ARIMA Evaluation")

    arima_result = evaluate_arima(
        train=train,
        test=test,
        order=(1, 1, 1),
        frequency="D",
    )

    print(
        f"Status : {arima_result.status}"
    )

    print(
        f"Message: {arima_result.message}"
    )

    assert arima_result.status in {
        "completed",
        "unavailable",
        "failed",
    }

    if arima_result.status == "completed":

        print(
            f"MAE   : {arima_result.mae:.4f}"
        )

        print(
            f"RMSE  : {arima_result.rmse:.4f}"
        )

        print(
            f"MAPE  : {arima_result.mape:.4f}%"
        )

        assert arima_result.mae is not None

        assert arima_result.rmse is not None

        assert arima_result.mape is not None

        print(
            "ARIMA evaluation: PASSED"
        )

    elif arima_result.status == "unavailable":

        print(
            "ARIMA was not included in the "
            "successful model comparison."
        )

        print(
            "ARIMA evaluation: UNAVAILABLE "
            "(environment restriction)"
        )

    else:

        print(
            "ARIMA evaluation: FAILED"
        )

    # =========================================================
    # 9. COMPLETE MODEL EVALUATION
    # =========================================================

    print("\n9. Complete Model Evaluation")

    summary = evaluate_all_models(
        series=series,
        test_size=test_size,
        frequency="D",
        moving_average_window=7,
        arima_order=(1, 1, 1),
    )

    print("\nMODEL COMPARISON")
    print("-" * 70)

    for model_key, result in (
        summary.results.items()
    ):

        print(
            f"{result.model_name:<24}"
            f" Status: {result.status}"
        )

        if result.status == "completed":

            print(
                f"  MAE : {result.mae:.4f}"
            )

            print(
                f"  RMSE: {result.rmse:.4f}"
            )

            print(
                f"  MAPE: {result.mape:.4f}%"
            )

        else:

            print(
                f"  Message: {result.message}"
            )

    print("\nBEST MODEL")
    print("-" * 70)

    print(
        f"Best Model: {summary.best_model}"
    )

    print(
        f"Best MAE  : {summary.best_mae:.4f}"
    )

    print(
        f"Status    : {summary.status}"
    )

    # =========================================================
    # 10. SUMMARY VALIDATION
    # =========================================================

    assert summary.status == "completed"

    assert summary.best_model is not None

    assert summary.best_mae is not None

    assert summary.best_mae >= 0

    # Three models must be successfully evaluated.
    assert (
        summary.results["naive"].status
        == "completed"
    )

    assert (
        summary.results["moving_average"].status
        == "completed"
    )

    assert (
        summary.results[
            "exponential_smoothing"
        ].status
        == "completed"
    )

    # ARIMA may be completed, unavailable, or failed
    # depending on the local environment.
    assert (
        summary.results["arima"].status
        in {
            "completed",
            "unavailable",
            "failed",
        }
    )

    # The selected model must be one of the models that
    # actually completed evaluation.
    completed_model_names = {
        result.model_name
        for result in summary.results.values()
        if result.status == "completed"
    }

    assert (
        summary.best_model
        in completed_model_names
    )

    # =========================================================
    # 11. SERIALIZATION
    # =========================================================

    print("\n11. Result Serialization")

    summary_dict = summary.to_dict()

    assert isinstance(
        summary_dict,
        dict,
    )

    assert (
        summary_dict["frequency"]
        == "D"
    )

    assert (
        summary_dict["test_size"]
        == test_size
    )

    assert isinstance(
        summary_dict["results"],
        dict,
    )

    assert (
        summary_dict["best_model"]
        == summary.best_model
    )

    print(
        "Summary serialization: PASSED"
    )

    # =========================================================
    # FINAL
    # =========================================================

    print("\n" + "=" * 70)
    print("8.6.3 FORECAST EVALUATION TEST: PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()