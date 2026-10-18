"""
Forecast Evaluation

Evaluates forecasting models using chronological historical
validation.

Responsibilities:
- Create chronological train/test splits
- Generate out-of-sample predictions
- Calculate MAE, RMSE and MAPE
- Compare available forecasting models
- Select the best available model based on MAE

This module does NOT:
- modify the original dataset
- perform random train/test splitting
- make business recommendations
- call an LLM
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from forecasting.models import (
    naive_forecast,
    moving_average_forecast,
    exponential_smoothing_forecast,
    arima_forecast,
)


# =============================================================
# RESULT STRUCTURES
# =============================================================

@dataclass
class ModelEvaluationResult:
    """
    Evaluation result for one forecasting model.
    """

    model_name: str
    status: str

    train_observations: int
    test_observations: int

    mae: Optional[float]
    rmse: Optional[float]
    mape: Optional[float]

    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a dictionary."""
        return asdict(self)


@dataclass
class ForecastEvaluationSummary:
    """
    Overall forecast evaluation summary.
    """

    frequency: str
    test_size: int

    results: Dict[str, ModelEvaluationResult]

    best_model: Optional[str]
    best_mae: Optional[float]

    status: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to a dictionary."""

        result = asdict(self)

        result["results"] = {
            key: value.to_dict()
            for key, value in self.results.items()
        }

        return result


# =============================================================
# METRICS
# =============================================================

def calculate_mae(
    actual: pd.Series,
    predicted: pd.Series,
) -> float:
    """
    Calculate Mean Absolute Error.

    MAE = mean(|actual - predicted|)
    """

    actual_values = np.asarray(
        actual,
        dtype=float,
    )

    predicted_values = np.asarray(
        predicted,
        dtype=float,
    )

    _validate_metric_inputs(
        actual_values,
        predicted_values,
    )

    return float(
        np.mean(
            np.abs(
                actual_values - predicted_values
            )
        )
    )


def calculate_rmse(
    actual: pd.Series,
    predicted: pd.Series,
) -> float:
    """
    Calculate Root Mean Squared Error.

    RMSE = sqrt(mean((actual - predicted)^2))
    """

    actual_values = np.asarray(
        actual,
        dtype=float,
    )

    predicted_values = np.asarray(
        predicted,
        dtype=float,
    )

    _validate_metric_inputs(
        actual_values,
        predicted_values,
    )

    return float(
        np.sqrt(
            np.mean(
                (
                    actual_values
                    - predicted_values
                ) ** 2
            )
        )
    )


def calculate_mape(
    actual: pd.Series,
    predicted: pd.Series,
) -> float:
    """
    Calculate Mean Absolute Percentage Error.

    Zero actual values are excluded from the percentage
    calculation because division by zero is undefined.

    Returns percentage, not a decimal.

    Example:
        12.5 means 12.5%.
    """

    actual_values = np.asarray(
        actual,
        dtype=float,
    )

    predicted_values = np.asarray(
        predicted,
        dtype=float,
    )

    _validate_metric_inputs(
        actual_values,
        predicted_values,
    )

    non_zero_mask = (
        actual_values != 0
    )

    if not non_zero_mask.any():
        return float("nan")

    actual_non_zero = (
        actual_values[
            non_zero_mask
        ]
    )

    predicted_non_zero = (
        predicted_values[
            non_zero_mask
        ]
    )

    percentage_errors = (
        np.abs(
            (
                actual_non_zero
                - predicted_non_zero
            )
            / actual_non_zero
        )
        * 100.0
    )

    return float(
        np.mean(
            percentage_errors
        )
    )


def _validate_metric_inputs(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> None:
    """Validate arrays used by evaluation metrics."""

    if actual.ndim != 1:
        raise ValueError(
            "Actual values must be one-dimensional."
        )

    if predicted.ndim != 1:
        raise ValueError(
            "Predicted values must be one-dimensional."
        )

    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and predicted values must have "
            "the same length."
        )

    if len(actual) == 0:
        raise ValueError(
            "Cannot calculate metrics on empty data."
        )

    if not np.isfinite(actual).all():
        raise ValueError(
            "Actual values contain invalid numeric values."
        )

    if not np.isfinite(predicted).all():
        raise ValueError(
            "Predicted values contain invalid numeric values."
        )


# =============================================================
# CHRONOLOGICAL SPLIT
# =============================================================

def chronological_train_test_split(
    series: pd.Series,
    test_size: int = 30,
) -> tuple[pd.Series, pd.Series]:
    """
    Split a time series chronologically.

    No random shuffling is performed.

    Example:

        Historical Data
        ├───────────────────────┤
        Training       Test
        ├──────────────┼────────┤
                       ↑
                   cutoff

    Parameters
    ----------
    series:
        Complete historical time series.

    test_size:
        Number of observations reserved for testing.

    Returns
    -------
    train, test
    """

    if not isinstance(series, pd.Series):
        raise TypeError(
            "series must be a pandas Series."
        )

    if series.empty:
        raise ValueError(
            "Cannot split an empty time series."
        )

    if not series.index.is_monotonic_increasing:
        raise ValueError(
            "Time series must be sorted chronologically."
        )

    if test_size <= 0:
        raise ValueError(
            "test_size must be greater than zero."
        )

    if test_size >= len(series):
        raise ValueError(
            "test_size must be smaller than the "
            "total number of observations."
        )

    train = series.iloc[
        :-test_size
    ].copy()

    test = series.iloc[
        -test_size:
    ].copy()

    return train, test


# =============================================================
# MODEL EVALUATION HELPERS
# =============================================================

def _evaluate_forecast(
    model_name: str,
    actual: pd.Series,
    predicted: pd.Series,
    train_observations: int,
) -> ModelEvaluationResult:
    """
    Calculate evaluation metrics for one model.
    """

    try:

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

        return ModelEvaluationResult(
            model_name=model_name,
            status="completed",
            train_observations=train_observations,
            test_observations=len(actual),
            mae=mae,
            rmse=rmse,
            mape=mape,
            message=(
                "Model evaluation completed successfully."
            ),
        )

    except Exception as exc:

        return ModelEvaluationResult(
            model_name=model_name,
            status="failed",
            train_observations=train_observations,
            test_observations=len(actual),
            mae=None,
            rmse=None,
            mape=None,
            message=(
                f"Model evaluation failed: {exc}"
            ),
        )


# =============================================================
# NAIVE EVALUATION
# =============================================================

def evaluate_naive(
    train: pd.Series,
    test: pd.Series,
    frequency: str = "D",
) -> ModelEvaluationResult:
    """
    Evaluate the Naive model on historical test data.
    """

    forecast_result = naive_forecast(
        series=train,
        horizon=len(test),
        frequency=frequency,
    )

    predicted = pd.Series(
        forecast_result.forecast[
            "forecast"
        ].to_numpy(),
        index=test.index,
    )

    return _evaluate_forecast(
        model_name="Naive",
        actual=test,
        predicted=predicted,
        train_observations=len(train),
    )


# =============================================================
# MOVING AVERAGE EVALUATION
# =============================================================

def evaluate_moving_average(
    train: pd.Series,
    test: pd.Series,
    window: int = 7,
    frequency: str = "D",
) -> ModelEvaluationResult:
    """
    Evaluate the Moving Average model.
    """

    try:

        forecast_result = (
            moving_average_forecast(
                series=train,
                horizon=len(test),
                window=window,
                frequency=frequency,
            )
        )

        predicted = pd.Series(
            forecast_result.forecast[
                "forecast"
            ].to_numpy(),
            index=test.index,
        )

        return _evaluate_forecast(
            model_name="Moving Average",
            actual=test,
            predicted=predicted,
            train_observations=len(train),
        )

    except Exception as exc:

        return ModelEvaluationResult(
            model_name="Moving Average",
            status="failed",
            train_observations=len(train),
            test_observations=len(test),
            mae=None,
            rmse=None,
            mape=None,
            message=(
                f"Moving Average evaluation failed: {exc}"
            ),
        )


# =============================================================
# EXPONENTIAL SMOOTHING EVALUATION
# =============================================================

def evaluate_exponential_smoothing(
    train: pd.Series,
    test: pd.Series,
    frequency: str = "D",
) -> ModelEvaluationResult:
    """
    Evaluate Simple Exponential Smoothing.
    """

    try:

        forecast_result = (
            exponential_smoothing_forecast(
                series=train,
                horizon=len(test),
                frequency=frequency,
            )
        )

        predicted = pd.Series(
            forecast_result.forecast[
                "forecast"
            ].to_numpy(),
            index=test.index,
        )

        return _evaluate_forecast(
            model_name="Exponential Smoothing",
            actual=test,
            predicted=predicted,
            train_observations=len(train),
        )

    except Exception as exc:

        return ModelEvaluationResult(
            model_name="Exponential Smoothing",
            status="failed",
            train_observations=len(train),
            test_observations=len(test),
            mae=None,
            rmse=None,
            mape=None,
            message=(
                "Exponential Smoothing evaluation "
                f"failed: {exc}"
            ),
        )


# =============================================================
# ARIMA EVALUATION
# =============================================================

def evaluate_arima(
    train: pd.Series,
    test: pd.Series,
    order: tuple[int, int, int] = (1, 1, 1),
    frequency: str = "D",
) -> ModelEvaluationResult:
    """
    Evaluate ARIMA.

    If statsmodels is unavailable, the model is reported as
    unavailable instead of crashing evaluation.
    """

    forecast_result = arima_forecast(
        series=train,
        horizon=len(test),
        order=order,
        frequency=frequency,
    )

    if forecast_result.status != "completed":

        return ModelEvaluationResult(
            model_name="ARIMA",
            status=forecast_result.status,
            train_observations=len(train),
            test_observations=len(test),
            mae=None,
            rmse=None,
            mape=None,
            message=forecast_result.message,
        )

    predicted = pd.Series(
        forecast_result.forecast[
            "forecast"
        ].to_numpy(),
        index=test.index,
    )

    return _evaluate_forecast(
        model_name="ARIMA",
        actual=test,
        predicted=predicted,
        train_observations=len(train),
    )


# =============================================================
# COMPLETE EVALUATION
# =============================================================

def evaluate_all_models(
    series: pd.Series,
    test_size: int = 30,
    frequency: str = "D",
    moving_average_window: int = 7,
    arima_order: tuple[int, int, int] = (1, 1, 1),
) -> ForecastEvaluationSummary:
    """
    Evaluate all supported forecasting models.

    Models are evaluated on the same chronological test period.

    Best model selection:
        Lowest MAE among successfully evaluated models.

    ARIMA may be unavailable depending on the environment.
    """

    if not isinstance(series, pd.Series):
        raise TypeError(
            "series must be a pandas Series."
        )

    train, test = chronological_train_test_split(
        series=series,
        test_size=test_size,
    )

    results: Dict[
        str,
        ModelEvaluationResult
    ] = {}

    # ---------------------------------------------------------
    # Naive
    # ---------------------------------------------------------

    results["naive"] = evaluate_naive(
        train=train,
        test=test,
        frequency=frequency,
    )

    # ---------------------------------------------------------
    # Moving Average
    # ---------------------------------------------------------

    results["moving_average"] = (
        evaluate_moving_average(
            train=train,
            test=test,
            window=moving_average_window,
            frequency=frequency,
        )
    )

    # ---------------------------------------------------------
    # Exponential Smoothing
    # ---------------------------------------------------------

    results["exponential_smoothing"] = (
        evaluate_exponential_smoothing(
            train=train,
            test=test,
            frequency=frequency,
        )
    )

    # ---------------------------------------------------------
    # ARIMA
    # ---------------------------------------------------------

    results["arima"] = evaluate_arima(
        train=train,
        test=test,
        order=arima_order,
        frequency=frequency,
    )

    # ---------------------------------------------------------
    # Find best model
    # ---------------------------------------------------------

    successful_results = [
        result
        for result in results.values()
        if (
            result.status == "completed"
            and result.mae is not None
            and np.isfinite(result.mae)
        )
    ]

    if successful_results:

        best_result = min(
            successful_results,
            key=lambda result: result.mae,
        )

        best_model = best_result.model_name
        best_mae = best_result.mae

        status = "completed"

        message = (
            "Forecast model evaluation completed. "
            "Best model selected using the lowest MAE."
        )

    else:

        best_model = None
        best_mae = None

        status = "failed"

        message = (
            "No forecasting model could be successfully evaluated."
        )

    return ForecastEvaluationSummary(
        frequency=frequency,
        test_size=test_size,
        results=results,
        best_model=best_model,
        best_mae=best_mae,
        status=status,
        message=message,
    )