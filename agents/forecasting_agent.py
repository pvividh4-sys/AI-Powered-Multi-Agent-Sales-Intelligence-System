"""
Forecasting Agent
-----------------
Coordinates the complete forecasting pipeline:

1. Check forecast eligibility
2. Prepare the time series
3. Generate forecasts from available models
4. Evaluate models chronologically
5. Select the best validated model
6. Validate the final forecasting output
7. Return a structured result

The agent does NOT directly modify the dataset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import pandas as pd

from forecasting.eligibility import check_forecast_eligibility
from forecasting.models import (
    generate_all_forecasts,
    prepare_time_series,
)
from forecasting.evaluation import evaluate_all_models


# ======================================================================
# Result Object
# ======================================================================

@dataclass
class ForecastingAgentResult:
    """Structured result returned by the Forecasting Agent."""

    status: str
    eligibility: Dict[str, Any]
    evaluation: Dict[str, Any]
    forecasts: Dict[str, Any]

    best_model: Optional[str] = None
    best_model_display: Optional[str] = None
    best_mae: Optional[float] = None

    frequency: Optional[str] = None
    horizon: Optional[int] = None

    validation: Dict[str, Any] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result into a dictionary."""

        return {
            "status": self.status,
            "eligibility": self.eligibility,
            "evaluation": self.evaluation,
            "forecasts": self.forecasts,
            "best_model": self.best_model,
            "best_model_display": self.best_model_display,
            "best_mae": self.best_mae,
            "frequency": self.frequency,
            "horizon": self.horizon,
            "validation": self.validation,
            "messages": self.messages,
        }


# ======================================================================
# Forecasting Agent
# ======================================================================

class ForecastingAgent:
    """
    Forecasting Agent.

    Responsibilities:
    - Check whether forecasting is possible.
    - Prepare the historical time series.
    - Generate candidate forecasts.
    - Evaluate forecasting models.
    - Select the best validated model.
    - Validate the final result.
    """

    def __init__(
        self,
        horizon: int = 7,
        test_size: int = 30,
        moving_average_window: int = 7,
        frequency: Optional[str] = None,
    ) -> None:

        if horizon <= 0:
            raise ValueError(
                "horizon must be greater than zero."
            )

        if test_size <= 0:
            raise ValueError(
                "test_size must be greater than zero."
            )

        if moving_average_window <= 0:
            raise ValueError(
                "moving_average_window must be greater than zero."
            )

        self.horizon = horizon
        self.test_size = test_size
        self.moving_average_window = moving_average_window
        self.frequency = frequency

    # ==================================================================
    # Main Pipeline
    # ==================================================================

    def run(
        self,
        df: pd.DataFrame,
        semantic_mapping: Optional[Dict[str, Any]] = None,
    ) -> ForecastingAgentResult:
        """
        Execute the complete forecasting pipeline.
        """

        messages: list[str] = []

        # --------------------------------------------------------------
        # 1. Input Validation
        # --------------------------------------------------------------

        if df is None:
            return self._failed_result(
                "Forecasting Agent requires a DataFrame."
            )

        if not isinstance(df, pd.DataFrame):
            return self._failed_result(
                "Forecasting Agent input must be a pandas DataFrame."
            )

        if df.empty:
            return self._failed_result(
                "Forecasting cannot run because the dataset is empty."
            )

        messages.append(
            "Input dataset validated."
        )

        # --------------------------------------------------------------
        # 2. Forecast Eligibility
        # --------------------------------------------------------------

        try:

            eligibility = check_forecast_eligibility(
                df,
                semantic_mapping=semantic_mapping,
            )

        except TypeError:

            try:

                eligibility = check_forecast_eligibility(
                    df,
                    semantic_mapping,
                )

            except Exception as exc:

                return self._failed_result(
                    f"Forecast eligibility check failed: {exc}"
                )

        except Exception as exc:

            return self._failed_result(
                f"Forecast eligibility check failed: {exc}"
            )

        eligibility_dict = self._serialize_result(
            eligibility
        )

        if not self._eligibility_is_true(
            eligibility_dict
        ):

            messages.append(
                "Forecasting was not executed because "
                "eligibility criteria were not satisfied."
            )

            return ForecastingAgentResult(
                status="not_eligible",
                eligibility=eligibility_dict,
                evaluation={},
                forecasts={},
                validation={
                    "overall_status": "PASSED",
                    "forecasting_executed": False,
                    "reason": (
                        "Forecast eligibility criteria "
                        "were not satisfied."
                    ),
                },
                messages=messages,
            )

        messages.append(
            "Forecast eligibility validated."
        )

        # --------------------------------------------------------------
        # 3. Determine Date and Sales Columns
        # --------------------------------------------------------------

        date_column = self._get_mapping_column(
            semantic_mapping,
            "date",
            eligibility_dict.get("date_column"),
        )

        sales_column = self._get_mapping_column(
            semantic_mapping,
            "sales",
            eligibility_dict.get("sales_column"),
        )

        selected_frequency = (
            self.frequency
            or eligibility_dict.get("frequency")
            or "D"
        )

        if not date_column:
            return self._failed_result(
                "Forecasting requires a valid date column."
            )

        if not sales_column:
            return self._failed_result(
                "Forecasting requires a valid sales column."
            )

        if date_column not in df.columns:
            return self._failed_result(
                f"Date column '{date_column}' "
                "does not exist in the dataset."
            )

        if sales_column not in df.columns:
            return self._failed_result(
                f"Sales column '{sales_column}' "
                "does not exist in the dataset."
            )

        messages.append(
            f"Forecasting columns: "
            f"date={date_column}, "
            f"sales={sales_column}."
        )

        # --------------------------------------------------------------
        # 4. Prepare Time Series
        # --------------------------------------------------------------

        try:

            time_series = prepare_time_series(
                df=df,
                date_column=date_column,
                sales_column=sales_column,
                frequency=selected_frequency,
            )

        except TypeError:

            try:

                time_series = prepare_time_series(
                    df,
                    date_column,
                    sales_column,
                    selected_frequency,
                )

            except Exception as exc:

                return self._failed_result(
                    f"Time-series preparation failed: {exc}"
                )

        except Exception as exc:

            return self._failed_result(
                f"Time-series preparation failed: {exc}"
            )

        if time_series is None:
            return self._failed_result(
                "Time-series preparation returned no data."
            )

        if not isinstance(
            time_series,
            pd.Series,
        ):
            return self._failed_result(
                "Time-series preparation must return "
                "a pandas Series."
            )

        if len(time_series) == 0:
            return self._failed_result(
                "Time-series preparation returned "
                "zero observations."
            )

        messages.append(
            f"Time series prepared with "
            f"{len(time_series)} observations."
        )

        # --------------------------------------------------------------
        # 5. Generate Candidate Forecasts
        # --------------------------------------------------------------

        try:

            forecasts = generate_all_forecasts(
                time_series,
                horizon=self.horizon,
                moving_average_window=(
                    self.moving_average_window
                ),
            )

        except Exception as exc:

            return self._failed_result(
                f"Forecast generation failed: {exc}"
            )

        forecasts_dict = self._serialize_forecasts(
            forecasts
        )

        completed_forecasts = []

        for model_name, result in forecasts_dict.items():

            if not isinstance(
                result,
                dict,
            ):
                continue

            if result.get(
                "status"
            ) != "completed":
                continue

            if result.get(
                "forecast"
            ) is None:
                continue

            completed_forecasts.append(
                model_name
            )

        if not completed_forecasts:

            return self._failed_result(
                "No forecasting model produced "
                "a completed forecast."
            )

        messages.append(
            "Completed forecast models: "
            + ", ".join(completed_forecasts)
            + "."
        )

        # --------------------------------------------------------------
        # 6. Chronological Model Evaluation
        # --------------------------------------------------------------

        try:

            evaluation = evaluate_all_models(
                time_series,
                test_size=self.test_size,
                frequency=selected_frequency,
                moving_average_window=(
                    self.moving_average_window
                ),
            )

        except TypeError:

            try:

                evaluation = evaluate_all_models(
                    time_series,
                    self.test_size,
                    selected_frequency,
                    self.moving_average_window,
                )

            except Exception as exc:

                return self._failed_result(
                    f"Forecast evaluation failed: {exc}"
                )

        except Exception as exc:

            return self._failed_result(
                f"Forecast evaluation failed: {exc}"
            )

        evaluation_dict = self._serialize_result(
            evaluation
        )

        # --------------------------------------------------------------
        # 7. Best Model
        # --------------------------------------------------------------

        best_model_display = evaluation_dict.get(
            "best_model"
        )

        best_mae = evaluation_dict.get(
            "best_mae"
        )

        best_model_canonical = (
            self._canonical_model_name(
                best_model_display
            )
        )

        if best_model_display:

            messages.append(
                f"Best validated model: "
                f"{best_model_display}."
            )

        # --------------------------------------------------------------
        # 8. Add Display Alias for Best Model
        # --------------------------------------------------------------
        #
        # The forecasting engine uses canonical names:
        #
        # exponential_smoothing
        #
        # The evaluation module returns:
        #
        # Exponential Smoothing
        #
        # Keep the original canonical key and additionally expose
        # the display-name alias so the agent result can be consumed
        # using either naming convention.
        #
        # This does NOT execute the model twice.

        if (
            best_model_display
            and best_model_canonical
            and best_model_canonical in forecasts_dict
        ):

            if (
                best_model_display
                not in forecasts_dict
            ):

                forecasts_dict[
                    best_model_display
                ] = forecasts_dict[
                    best_model_canonical
                ]

        # --------------------------------------------------------------
        # 9. Validate Forecasting Result
        # --------------------------------------------------------------

        validation = (
            self._validate_forecasting_result(
                time_series=time_series,
                forecasts=forecasts_dict,
                evaluation=evaluation_dict,
                best_model=best_model_canonical,
                horizon=self.horizon,
            )
        )

        if validation[
            "overall_status"
        ] != "PASSED":

            messages.append(
                "Forecasting output validation failed."
            )

            return ForecastingAgentResult(
                status="validation_failed",
                eligibility=eligibility_dict,
                evaluation=evaluation_dict,
                forecasts=forecasts_dict,
                best_model=best_model_display,
                best_model_display=best_model_display,
                best_mae=best_mae,
                frequency=selected_frequency,
                horizon=self.horizon,
                validation=validation,
                messages=messages,
            )

        messages.append(
            "Forecasting output validation passed."
        )

        # --------------------------------------------------------------
        # 10. Final Result
        # --------------------------------------------------------------

        return ForecastingAgentResult(
            status="completed",
            eligibility=eligibility_dict,
            evaluation=evaluation_dict,
            forecasts=forecasts_dict,
            best_model=best_model_display,
            best_model_display=best_model_display,
            best_mae=best_mae,
            frequency=selected_frequency,
            horizon=self.horizon,
            validation=validation,
            messages=messages,
        )

    # ==================================================================
    # Failed Result
    # ==================================================================

    @staticmethod
    def _failed_result(
        message: str,
    ) -> ForecastingAgentResult:

        return ForecastingAgentResult(
            status="failed",
            eligibility={},
            evaluation={},
            forecasts={},
            validation={
                "overall_status": "FAILED",
                "forecasting_executed": False,
                "reason": message,
            },
            messages=[message],
        )

    # ==================================================================
    # Serialization
    # ==================================================================

    @staticmethod
    def _serialize_result(
        result: Any,
    ) -> Dict[str, Any]:

        if result is None:
            return {}

        if isinstance(
            result,
            dict,
        ):
            return result

        if hasattr(
            result,
            "to_dict",
        ):

            try:

                value = result.to_dict()

                if isinstance(
                    value,
                    dict,
                ):
                    return value

            except Exception:
                pass

        if hasattr(
            result,
            "__dict__",
        ):

            return dict(
                result.__dict__
            )

        return {}

    @staticmethod
    def _serialize_forecasts(
        forecasts: Any,
    ) -> Dict[str, Any]:

        if forecasts is None:
            return {}

        if not isinstance(
            forecasts,
            dict,
        ):
            return {}

        serialized = {}

        for model_name, result in forecasts.items():

            serialized[
                model_name
            ] = (
                ForecastingAgent
                ._serialize_result(
                    result
                )
            )

        return serialized

    # ==================================================================
    # Eligibility Helpers
    # ==================================================================

    @staticmethod
    def _eligibility_is_true(
        eligibility: Dict[str, Any],
    ) -> bool:

        value = eligibility.get(
            "eligible"
        )

        if value is None:

            value = eligibility.get(
                "is_eligible"
            )

        return bool(value)

    @staticmethod
    def _get_mapping_column(
        semantic_mapping: Optional[
            Dict[str, Any]
        ],
        key: str,
        fallback: Optional[str],
    ) -> Optional[str]:

        if (
            semantic_mapping
            and key in semantic_mapping
        ):

            value = semantic_mapping[
                key
            ]

            if isinstance(
                value,
                str,
            ):

                return value

            if isinstance(
                value,
                dict,
            ):

                column = value.get(
                    "column"
                )

                if column:
                    return column

                column = value.get(
                    "mapped_column"
                )

                if column:
                    return column

        return fallback

    # ==================================================================
    # Model Name Normalization
    # ==================================================================

    @staticmethod
    def _canonical_model_name(
        model_name: Optional[str],
    ) -> Optional[str]:
        """
        Convert display model name to internal model key.

        Examples:

        Exponential Smoothing
            ->
        exponential_smoothing

        Moving Average
            ->
        moving_average
        """

        if not model_name:
            return None

        return (
            str(model_name)
            .strip()
            .lower()
            .replace(
                "-",
                "_",
            )
            .replace(
                " ",
                "_",
            )
        )

    # ==================================================================
    # Forecast Validation
    # ==================================================================

    @classmethod
    def _validate_forecasting_result(
        cls,
        time_series: pd.Series,
        forecasts: Dict[str, Any],
        evaluation: Dict[str, Any],
        best_model: Optional[str],
        horizon: int,
    ) -> Dict[str, Any]:

        checks = []

        # --------------------------------------------------------------
        # 1. Historical Time Series
        # --------------------------------------------------------------

        historical_valid = (
            isinstance(
                time_series,
                pd.Series,
            )
            and len(time_series) > 0
        )

        checks.append(
            {
                "check": "historical_time_series",
                "status": (
                    "PASSED"
                    if historical_valid
                    else "FAILED"
                ),
            }
        )

        if not historical_valid:

            return {
                "overall_status": "FAILED",
                "total_checks": len(checks),
                "passed": 0,
                "failed": 1,
                "checks": checks,
            }

        # --------------------------------------------------------------
        # 2. Completed Forecasts
        # --------------------------------------------------------------

        completed_models = []

        for model_name, result in forecasts.items():

            if not isinstance(
                result,
                dict,
            ):
                continue

            if result.get(
                "status"
            ) != "completed":
                continue

            if result.get(
                "forecast"
            ) is None:
                continue

            completed_models.append(
                model_name
            )

        forecast_valid = (
            len(completed_models) > 0
        )

        checks.append(
            {
                "check": "completed_forecasts",
                "status": (
                    "PASSED"
                    if forecast_valid
                    else "FAILED"
                ),
                "completed_models": (
                    completed_models
                ),
            }
        )

        # --------------------------------------------------------------
        # 3. Forecast Horizon
        # --------------------------------------------------------------

        horizon_results = []

        for model_name in completed_models:

            result = forecasts.get(
                model_name,
                {},
            )

            forecast_value = result.get(
                "forecast"
            )

            actual_horizon = (
                cls._get_forecast_length(
                    forecast_value
                )
            )

            horizon_results.append(
                {
                    "model": model_name,
                    "expected": horizon,
                    "actual": actual_horizon,
                    "status": (
                        "PASSED"
                        if actual_horizon == horizon
                        else "FAILED"
                    ),
                }
            )

        horizon_valid = all(
            item["status"] == "PASSED"
            for item in horizon_results
        )

        checks.append(
            {
                "check": "forecast_horizon",
                "status": (
                    "PASSED"
                    if horizon_valid
                    else "FAILED"
                ),
                "details": horizon_results,
            }
        )

        # --------------------------------------------------------------
        # 4. Model Evaluation
        # --------------------------------------------------------------

        evaluation_valid = bool(
            evaluation
        )

        checks.append(
            {
                "check": "model_evaluation",
                "status": (
                    "PASSED"
                    if evaluation_valid
                    else "FAILED"
                ),
            }
        )

        # --------------------------------------------------------------
        # 5. Best Model
        # --------------------------------------------------------------

        normalised_completed_models = [
            cls._canonical_model_name(
                model
            )
            for model in completed_models
        ]

        best_model_valid = (
            best_model is not None
            and best_model
            in normalised_completed_models
        )

        checks.append(
            {
                "check": "best_model",
                "status": (
                    "PASSED"
                    if best_model_valid
                    else "FAILED"
                ),
                "best_model": best_model,
                "available_models": (
                    completed_models
                ),
            }
        )

        # --------------------------------------------------------------
        # 6. Forecast Values
        # --------------------------------------------------------------

        forecast_values_valid = True

        forecast_value_details = []

        for model_name in completed_models:

            result = forecasts.get(
                model_name,
                {},
            )

            forecast_value = result.get(
                "forecast"
            )

            numeric_valid = (
                cls._forecast_values_are_numeric(
                    forecast_value
                )
            )

            forecast_value_details.append(
                {
                    "model": model_name,
                    "status": (
                        "PASSED"
                        if numeric_valid
                        else "FAILED"
                    ),
                }
            )

            if not numeric_valid:

                forecast_values_valid = False

        checks.append(
            {
                "check": "forecast_values",
                "status": (
                    "PASSED"
                    if forecast_values_valid
                    else "FAILED"
                ),
                "details": forecast_value_details,
            }
        )

        # --------------------------------------------------------------
        # Final Summary
        # --------------------------------------------------------------

        passed = sum(
            1
            for check in checks
            if check["status"] == "PASSED"
        )

        failed = sum(
            1
            for check in checks
            if check["status"] == "FAILED"
        )

        return {
            "overall_status": (
                "PASSED"
                if failed == 0
                else "FAILED"
            ),
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
            "checks": checks,
        }

    # ==================================================================
    # Forecast Length
    # ==================================================================

    @staticmethod
    def _get_forecast_length(
        forecast_value: Any,
    ) -> int:

        if forecast_value is None:
            return 0

        if isinstance(
            forecast_value,
            pd.Series,
        ):
            return len(
                forecast_value
            )

        if isinstance(
            forecast_value,
            pd.DataFrame,
        ):
            return len(
                forecast_value
            )

        if isinstance(
            forecast_value,
            dict,
        ):
            return 1

        try:

            return len(
                forecast_value
            )

        except TypeError:

            return 1

    # ==================================================================
    # Forecast Value Validation
    # ==================================================================

    @staticmethod
    def _forecast_values_are_numeric(
        forecast_value: Any,
    ) -> bool:

        if forecast_value is None:
            return False

        try:

            # ----------------------------------------------------------
            # Series
            # ----------------------------------------------------------

            if isinstance(
                forecast_value,
                pd.Series,
            ):

                numeric = pd.to_numeric(
                    forecast_value,
                    errors="coerce",
                )

                return bool(
                    numeric.notna().all()
                )

            # ----------------------------------------------------------
            # DataFrame
            # ----------------------------------------------------------

            if isinstance(
                forecast_value,
                pd.DataFrame,
            ):

                if forecast_value.empty:
                    return False

                numeric_columns = (
                    forecast_value.select_dtypes(
                        include="number"
                    )
                )

                if numeric_columns.empty:
                    return False

                numeric = numeric_columns.apply(
                    pd.to_numeric,
                    errors="coerce",
                )

                return bool(
                    numeric.notna().all().all()
                )

            # ----------------------------------------------------------
            # Dictionary
            # ----------------------------------------------------------

            if isinstance(
                forecast_value,
                dict,
            ):

                candidate_keys = [
                    "forecast",
                    "prediction",
                    "predicted",
                    "value",
                ]

                for key in candidate_keys:

                    if key in forecast_value:

                        numeric = pd.to_numeric(
                            [
                                forecast_value[key]
                            ],
                            errors="coerce",
                        )

                        return bool(
                            pd.Series(
                                numeric
                            ).notna().all()
                        )

                values = list(
                    forecast_value.values()
                )

                if not values:
                    return False

                numeric = pd.to_numeric(
                    values,
                    errors="coerce",
                )

                return bool(
                    pd.Series(
                        numeric
                    ).notna().all()
                )

            # ----------------------------------------------------------
            # List / Tuple
            # ----------------------------------------------------------

            if isinstance(
                forecast_value,
                (list, tuple),
            ):

                if len(
                    forecast_value
                ) == 0:

                    return False

                # Handle serialised forecast records.
                if all(
                    isinstance(
                        item,
                        dict,
                    )
                    for item in forecast_value
                ):

                    candidate_keys = [
                        "forecast",
                        "prediction",
                        "predicted",
                        "value",
                    ]

                    for key in candidate_keys:

                        if all(
                            key in item
                            for item
                            in forecast_value
                        ):

                            values = [
                                item[key]
                                for item
                                in forecast_value
                            ]

                            numeric = (
                                pd.to_numeric(
                                    values,
                                    errors="coerce",
                                )
                            )

                            return bool(
                                pd.Series(
                                    numeric
                                ).notna().all()
                            )

                    return False

                numeric = pd.to_numeric(
                    forecast_value,
                    errors="coerce",
                )

                return bool(
                    pd.Series(
                        numeric
                    ).notna().all()
                )

            # ----------------------------------------------------------
            # NumPy / Other Array-like
            # ----------------------------------------------------------

            numeric = pd.to_numeric(
                forecast_value,
                errors="coerce",
            )

            if hasattr(
                numeric,
                "notna",
            ):

                return bool(
                    numeric.notna().all()
                )

            return bool(
                pd.Series(
                    numeric
                ).notna().all()
            )

        except Exception:

            return False


# ======================================================================
# Convenience Function
# ======================================================================

def run_forecasting_agent(
    df: pd.DataFrame,
    semantic_mapping: Optional[
        Dict[str, Any]
    ] = None,
    horizon: int = 7,
    test_size: int = 30,
    moving_average_window: int = 7,
    frequency: Optional[str] = None,
) -> ForecastingAgentResult:
    """
    Convenience wrapper for the Forecasting Agent.
    """

    agent = ForecastingAgent(
        horizon=horizon,
        test_size=test_size,
        moving_average_window=(
            moving_average_window
        ),
        frequency=frequency,
    )

    return agent.run(
        df=df,
        semantic_mapping=semantic_mapping,
    )