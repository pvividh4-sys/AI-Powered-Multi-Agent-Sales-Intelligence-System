"""
Forecast Models

Provides forecasting models for the Sales Intelligence System.

Supported models:
1. Naive Forecast
2. Moving Average
3. Simple Exponential Smoothing
4. ARIMA (optional)

Important:
- Naive, Moving Average, and Simple Exponential Smoothing do not
  depend on statsmodels.
- ARIMA is loaded dynamically only when requested.
- If ARIMA is unavailable because of an environment or security
  restriction, the remaining forecasting models continue to work.

This module does NOT:
- compare models
- calculate model accuracy
- select the best model
- make business recommendations

Model evaluation is handled separately by forecasting/evaluation.py.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


# =============================================================
# RESULT STRUCTURE
# =============================================================

@dataclass
class ForecastResult:
    """
    Standard result returned by every forecasting model.

    status values:
        completed  -> forecast successfully generated
        unavailable -> model could not be executed
        failed     -> model execution failed
    """

    model_name: str
    frequency: str
    horizon: int

    historical_observations: int

    forecast: pd.DataFrame

    status: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result into a serialisable dictionary."""

        result = asdict(self)

        result["forecast"] = self.forecast.to_dict(
            orient="records"
        )

        return result


# =============================================================
# TIME-SERIES PREPARATION
# =============================================================

def prepare_time_series(
    df: pd.DataFrame,
    date_column: str,
    sales_column: str,
    frequency: str = "D",
) -> pd.Series:
    """
    Prepare a regular sales time series from transaction data.

    Steps:
    1. Validate dataframe.
    2. Validate date and sales columns.
    3. Parse DD/MM/YYYY dates.
    4. Convert sales to numeric.
    5. Remove invalid observations.
    6. Aggregate sales by requested frequency.
    7. Fill missing periods with zero.

    Parameters
    ----------
    df:
        Input transaction dataframe.

    date_column:
        Date column.

    sales_column:
        Sales/revenue column.

    frequency:
        D = daily
        W = weekly
        M = monthly

    Returns
    -------
    pandas.Series
        Regular time series.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Cannot prepare a time series from an empty dataset."
        )

    if date_column not in df.columns:
        raise ValueError(
            f"Date column '{date_column}' not found."
        )

    if sales_column not in df.columns:
        raise ValueError(
            f"Sales column '{sales_column}' not found."
        )

    if frequency not in {"D", "W", "M"}:
        raise ValueError(
            "Unsupported frequency. Use 'D', 'W', or 'M'."
        )

    # ---------------------------------------------------------
    # Parse dates
    # ---------------------------------------------------------

    dates = pd.to_datetime(
        df[date_column],
        format="%d/%m/%Y",
        errors="coerce",
    )

    # ---------------------------------------------------------
    # Convert sales
    # ---------------------------------------------------------

    sales = pd.to_numeric(
        df[sales_column],
        errors="coerce",
    )

    # ---------------------------------------------------------
    # Keep valid observations
    # ---------------------------------------------------------

    valid_mask = (
        dates.notna()
        & sales.notna()
    )

    if not valid_mask.any():
        raise ValueError(
            "No valid date/sales observations are available."
        )

    working_df = pd.DataFrame(
        {
            "date": dates[valid_mask],
            "sales": sales[valid_mask],
        }
    )

    working_df = (
        working_df
        .set_index("date")
        .sort_index()
    )

    # ---------------------------------------------------------
    # Aggregate
    # ---------------------------------------------------------

    if frequency == "D":

        series = (
            working_df["sales"]
            .resample("D")
            .sum()
        )

    elif frequency == "W":

        series = (
            working_df["sales"]
            .resample("W")
            .sum()
        )

    else:

        # Month-end frequency.
        series = (
            working_df["sales"]
            .resample("ME")
            .sum()
        )

    # ---------------------------------------------------------
    # Fill missing periods
    # ---------------------------------------------------------

    series = series.asfreq(
        series.index.freq
    )

    # A missing calendar period means no recorded transaction.
    # We therefore use zero instead of interpolation.
    series = series.fillna(0.0)

    series = series.astype(float)

    series.name = sales_column

    return series


# =============================================================
# FORECAST INDEX
# =============================================================

def _create_forecast_index(
    series: pd.Series,
    horizon: int,
    frequency: str,
) -> pd.DatetimeIndex:
    """
    Create future dates for a forecast.
    """

    if horizon <= 0:
        raise ValueError(
            "Forecast horizon must be greater than zero."
        )

    if series.empty:
        raise ValueError(
            "Cannot create a forecast index from an empty series."
        )

    if frequency == "D":

        offset = pd.offsets.Day()

    elif frequency == "W":

        offset = pd.offsets.Week()

    elif frequency == "M":

        offset = pd.offsets.MonthEnd()

    else:

        raise ValueError(
            "Unsupported frequency. Use 'D', 'W', or 'M'."
        )

    start_date = series.index[-1] + offset

    return pd.date_range(
        start=start_date,
        periods=horizon,
        freq=frequency,
    )


# =============================================================
# INPUT VALIDATION
# =============================================================

def _validate_series(
    series: pd.Series,
    horizon: int,
) -> None:
    """Validate common model inputs."""

    if not isinstance(series, pd.Series):
        raise TypeError(
            "series must be a pandas Series."
        )

    if series.empty:
        raise ValueError(
            "Cannot forecast an empty series."
        )

    if horizon <= 0:
        raise ValueError(
            "Forecast horizon must be greater than zero."
        )

    if not series.index.is_monotonic_increasing:
        raise ValueError(
            "Time-series index must be sorted chronologically."
        )

    if series.isna().any():
        raise ValueError(
            "Time series contains missing values."
        )


# =============================================================
# NAIVE FORECAST
# =============================================================

def naive_forecast(
    series: pd.Series,
    horizon: int,
    frequency: str = "D",
) -> ForecastResult:
    """
    Generate a Naive Forecast.

    Every future value is equal to the last observed value.

    This model acts as the baseline for model evaluation.
    """

    _validate_series(
        series,
        horizon,
    )

    last_value = float(
        series.iloc[-1]
    )

    forecast_index = _create_forecast_index(
        series,
        horizon,
        frequency,
    )

    forecast_values = np.repeat(
        last_value,
        horizon,
    )

    forecast_df = pd.DataFrame(
        {
            "date": forecast_index,
            "forecast": forecast_values,
        }
    )

    return ForecastResult(
        model_name="Naive",
        frequency=frequency,
        horizon=horizon,
        historical_observations=len(series),
        forecast=forecast_df,
        status="completed",
        message=(
            "Naive forecast generated successfully."
        ),
    )


# =============================================================
# MOVING AVERAGE FORECAST
# =============================================================

def moving_average_forecast(
    series: pd.Series,
    horizon: int,
    window: int = 7,
    frequency: str = "D",
) -> ForecastResult:
    """
    Generate a Moving Average Forecast.

    The mean of the most recent observations is used as the
    forecast for each future period.

    Example:
        window = 7

    means:
        last 7 historical observations
        ↓
        future forecast
    """

    _validate_series(
        series,
        horizon,
    )

    if window <= 0:
        raise ValueError(
            "Moving-average window must be greater than zero."
        )

    if len(series) < window:
        raise ValueError(
            f"At least {window} observations are required "
            "for the moving average."
        )

    recent_values = series.tail(
        window
    )

    mean_value = float(
        recent_values.mean()
    )

    forecast_index = _create_forecast_index(
        series,
        horizon,
        frequency,
    )

    forecast_values = np.repeat(
        mean_value,
        horizon,
    )

    forecast_df = pd.DataFrame(
        {
            "date": forecast_index,
            "forecast": forecast_values,
        }
    )

    return ForecastResult(
        model_name="Moving Average",
        frequency=frequency,
        horizon=horizon,
        historical_observations=len(series),
        forecast=forecast_df,
        status="completed",
        message=(
            f"Moving average forecast generated "
            f"using a {window}-period window."
        ),
    )


# =============================================================
# SIMPLE EXPONENTIAL SMOOTHING
# =============================================================

def exponential_smoothing_forecast(
    series: pd.Series,
    horizon: int,
    frequency: str = "D",
    alpha: Optional[float] = None,
) -> ForecastResult:
    """
    Generate a Simple Exponential Smoothing forecast.

    Formula:

        S(t) = alpha * Y(t)
             + (1 - alpha) * S(t-1)

    The final smoothed value is used for future forecasts.

    Parameters
    ----------
    series:
        Historical time series.

    horizon:
        Number of future periods.

    frequency:
        Forecast frequency.

    alpha:
        Smoothing factor between 0 and 1.

        If None, alpha is selected automatically using a simple
        one-step-ahead squared-error search.

    Notes
    -----
    This implementation intentionally does not depend on
    statsmodels.
    """

    _validate_series(
        series,
        horizon,
    )

    if len(series) < 2:
        raise ValueError(
            "At least two observations are required "
            "for exponential smoothing."
        )

    if alpha is not None:

        if not 0 < alpha <= 1:
            raise ValueError(
                "alpha must be greater than 0 and less than "
                "or equal to 1."
            )

        selected_alpha = float(alpha)

    else:

        selected_alpha = _select_exponential_alpha(
            series
        )

    values = series.to_numpy(
        dtype=float
    )

    smoothed_value = values[0]

    for value in values[1:]:

        smoothed_value = (
            selected_alpha * value
            + (1.0 - selected_alpha)
            * smoothed_value
        )

    forecast_index = _create_forecast_index(
        series,
        horizon,
        frequency,
    )

    forecast_values = np.repeat(
        smoothed_value,
        horizon,
    )

    forecast_df = pd.DataFrame(
        {
            "date": forecast_index,
            "forecast": forecast_values,
        }
    )

    return ForecastResult(
        model_name="Exponential Smoothing",
        frequency=frequency,
        horizon=horizon,
        historical_observations=len(series),
        forecast=forecast_df,
        status="completed",
        message=(
            "Simple exponential smoothing forecast "
            f"generated successfully using alpha={selected_alpha:.3f}."
        ),
    )


def _select_exponential_alpha(
    series: pd.Series,
) -> float:
    """
    Select alpha using one-step-ahead squared-error search.

    Candidate alpha values are evaluated from 0.01 to 1.00.

    The first observation is used to initialise the smoother.
    """

    values = series.to_numpy(
        dtype=float
    )

    best_alpha = 0.5
    best_error = float("inf")

    candidate_alphas = np.arange(
        0.01,
        1.01,
        0.01,
    )

    for alpha in candidate_alphas:

        smoothed = values[0]
        squared_error = 0.0

        for actual in values[1:]:

            prediction = smoothed

            error = actual - prediction

            squared_error += error ** 2

            smoothed = (
                alpha * actual
                + (1.0 - alpha) * smoothed
            )

        if squared_error < best_error:

            best_error = squared_error
            best_alpha = float(alpha)

    return best_alpha


# =============================================================
# ARIMA
# =============================================================

def arima_forecast(
    series: pd.Series,
    horizon: int,
    order: tuple[int, int, int] = (1, 1, 1),
    frequency: str = "D",
) -> ForecastResult:
    """
    Generate an ARIMA forecast when statsmodels is available.

    statsmodels is imported dynamically here rather than at module
    import time.

    This prevents a blocked statsmodels binary from crashing the
    complete forecasting module.

    If the environment blocks statsmodels, the returned status is
    'unavailable' instead of raising an import error.
    """

    _validate_series(
        series,
        horizon,
    )

    if len(series) < 10:

        raise ValueError(
            "At least 10 observations are required "
            "for the ARIMA model."
        )

    if (
        not isinstance(order, tuple)
        or len(order) != 3
        or not all(
            isinstance(value, int)
            for value in order
        )
    ):

        raise ValueError(
            "ARIMA order must be a tuple of three integers: "
            "(p, d, q)."
        )

    # ---------------------------------------------------------
    # Dynamically import statsmodels
    # ---------------------------------------------------------

    try:

        from statsmodels.tsa.arima.model import ARIMA

    except Exception as exc:

        return ForecastResult(
            model_name="ARIMA",
            frequency=frequency,
            horizon=horizon,
            historical_observations=len(series),
            forecast=pd.DataFrame(
                columns=[
                    "date",
                    "forecast",
                ]
            ),
            status="unavailable",
            message=(
                "ARIMA is unavailable because the statsmodels "
                f"native dependency could not be loaded: {exc}"
            ),
        )

    # ---------------------------------------------------------
    # Fit ARIMA
    # ---------------------------------------------------------

    try:

        model = ARIMA(
            series,
            order=order,
        )

        fitted_model = model.fit()

        forecast_values = fitted_model.forecast(
            steps=horizon
        )

        forecast_values = np.asarray(
            forecast_values,
            dtype=float,
        )

        forecast_index = _create_forecast_index(
            series,
            horizon,
            frequency,
        )

        forecast_df = pd.DataFrame(
            {
                "date": forecast_index,
                "forecast": forecast_values,
            }
        )

        return ForecastResult(
            model_name="ARIMA",
            frequency=frequency,
            horizon=horizon,
            historical_observations=len(series),
            forecast=forecast_df,
            status="completed",
            message=(
                f"ARIMA{order} forecast generated successfully."
            ),
        )

    except Exception as exc:

        return ForecastResult(
            model_name="ARIMA",
            frequency=frequency,
            horizon=horizon,
            historical_observations=len(series),
            forecast=pd.DataFrame(
                columns=[
                    "date",
                    "forecast",
                ]
            ),
            status="failed",
            message=(
                f"ARIMA model execution failed: {exc}"
            ),
        )


# =============================================================
# ALL MODELS
# =============================================================

def generate_all_forecasts(
    series: pd.Series,
    horizon: int,
    frequency: str = "D",
    moving_average_window: int = 7,
    arima_order: tuple[int, int, int] = (1, 1, 1),
) -> Dict[str, ForecastResult]:
    """
    Generate forecasts from all supported models.

    The function continues even if ARIMA is unavailable.

    Returns
    -------
    dict
        Dictionary containing ForecastResult objects.

    Model selection is NOT performed here.
    """

    results: Dict[str, ForecastResult] = {}

    # ---------------------------------------------------------
    # Naive
    # ---------------------------------------------------------

    results["naive"] = naive_forecast(
        series=series,
        horizon=horizon,
        frequency=frequency,
    )

    # ---------------------------------------------------------
    # Moving Average
    # ---------------------------------------------------------

    results["moving_average"] = (
        moving_average_forecast(
            series=series,
            horizon=horizon,
            window=moving_average_window,
            frequency=frequency,
        )
    )

    # ---------------------------------------------------------
    # Exponential Smoothing
    # ---------------------------------------------------------

    results["exponential_smoothing"] = (
        exponential_smoothing_forecast(
            series=series,
            horizon=horizon,
            frequency=frequency,
        )
    )

    # ---------------------------------------------------------
    # ARIMA
    # ---------------------------------------------------------

    results["arima"] = arima_forecast(
        series=series,
        horizon=horizon,
        order=arima_order,
        frequency=frequency,
    )

    return results