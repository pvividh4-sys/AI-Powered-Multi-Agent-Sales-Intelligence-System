"""
Forecast Eligibility

Determines whether a dataset is suitable for time-series forecasting.

Responsibilities:
- Resolve date and sales columns
- Parse dates correctly
- Validate sales values
- Measure usable historical observations
- Check historical coverage
- Check time-series consistency
- Select a practical forecasting frequency
- Return a structured eligibility result

This module does NOT train forecasting models.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

import pandas as pd


@dataclass
class ForecastEligibilityResult:
    """Structured result returned by the forecast eligibility check."""

    eligible: bool

    date_column: Optional[str]
    sales_column: Optional[str]

    observations: int
    unique_dates: int

    start_date: Optional[str]
    end_date: Optional[str]

    frequency: Optional[str]

    date_valid: bool
    sales_valid: bool
    sufficient_history: bool
    consistent_series: bool
    acceptable_quality: bool

    reasons: list[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a dictionary."""
        return asdict(self)


def _find_column(
    df: pd.DataFrame,
    semantic_mapping: Optional[Dict[str, Any]],
    semantic_name: str,
) -> Optional[str]:
    """
    Resolve a column using Planner semantic mapping.

    Supported formats:

        {"date": "Date"}

    or:

        {
            "date": {
                "column": "Date",
                "confidence": 0.95
            }
        }
    """

    if not semantic_mapping:
        return None

    value = semantic_mapping.get(semantic_name)

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return value.get("column")

    return None


def _validate_column_exists(
    df: pd.DataFrame,
    column: Optional[str],
) -> bool:
    """Check whether a column exists."""

    return (
        column is not None
        and column in df.columns
    )


def _parse_dates(
    series: pd.Series,
) -> pd.Series:
    """
    Parse dataset dates.

    The current retail dataset uses DD/MM/YYYY.

    The explicit format prevents pandas from incorrectly
    interpreting dates such as 13/01/2023.
    """

    return pd.to_datetime(
        series,
        format="%d/%m/%Y",
        errors="coerce",
    )


def _detect_frequency(
    dates: pd.Series,
) -> Optional[str]:
    """
    Determine a practical forecasting frequency.

    Daily:
        At least 30 unique dates and 30 days of coverage.

    Weekly:
        At least 8 unique weeks.

    Monthly:
        At least 6 unique months.

    Seasonality is NOT determined here.
    """

    if dates.empty:
        return None

    unique_dates = (
        dates
        .dropna()
        .dt.normalize()
        .drop_duplicates()
        .sort_values()
    )

    if len(unique_dates) < 2:
        return None

    date_span_days = (
        unique_dates.iloc[-1] -
        unique_dates.iloc[0]
    ).days

    # Prefer daily forecasting when enough daily
    # observations are available.
    if len(unique_dates) >= 30 and date_span_days >= 30:
        return "D"

    weekly_periods = unique_dates.dt.to_period("W").nunique()

    if weekly_periods >= 8:
        return "W"

    monthly_periods = unique_dates.dt.to_period("M").nunique()

    if monthly_periods >= 6:
        return "M"

    return None


def check_forecast_eligibility(
    df: pd.DataFrame,
    semantic_mapping: Optional[Dict[str, Any]] = None,
    date_column: Optional[str] = None,
    sales_column: Optional[str] = None,
    min_observations: int = 30,
) -> ForecastEligibilityResult:
    """
    Check whether a dataset is suitable for forecasting.

    Parameters
    ----------
    df:
        Input sales dataframe.

    semantic_mapping:
        Planner semantic mapping containing keys such as
        'date' and 'sales'.

    date_column:
        Optional explicit date column.

    sales_column:
        Optional explicit sales/revenue column.

    min_observations:
        Minimum valid observations required.

    Returns
    -------
    ForecastEligibilityResult
        Structured eligibility result.
    """

    reasons: list[str] = []

    # =========================================================
    # 1. BASIC DATASET VALIDATION
    # =========================================================

    if df is None:
        return ForecastEligibilityResult(
            eligible=False,
            date_column=None,
            sales_column=None,
            observations=0,
            unique_dates=0,
            start_date=None,
            end_date=None,
            frequency=None,
            date_valid=False,
            sales_valid=False,
            sufficient_history=False,
            consistent_series=False,
            acceptable_quality=False,
            reasons=["Dataset is None."],
        )

    if not isinstance(df, pd.DataFrame):
        return ForecastEligibilityResult(
            eligible=False,
            date_column=None,
            sales_column=None,
            observations=0,
            unique_dates=0,
            start_date=None,
            end_date=None,
            frequency=None,
            date_valid=False,
            sales_valid=False,
            sufficient_history=False,
            consistent_series=False,
            acceptable_quality=False,
            reasons=["Input must be a pandas DataFrame."],
        )

    if df.empty:
        return ForecastEligibilityResult(
            eligible=False,
            date_column=None,
            sales_column=None,
            observations=0,
            unique_dates=0,
            start_date=None,
            end_date=None,
            frequency=None,
            date_valid=False,
            sales_valid=False,
            sufficient_history=False,
            consistent_series=False,
            acceptable_quality=False,
            reasons=["Dataset is empty."],
        )

    # =========================================================
    # 2. RESOLVE SEMANTIC COLUMNS
    # =========================================================

    mapped_date_column = _find_column(
        df,
        semantic_mapping,
        "date",
    )

    mapped_sales_column = _find_column(
        df,
        semantic_mapping,
        "sales",
    )

    date_column = date_column or mapped_date_column
    sales_column = sales_column or mapped_sales_column

    # =========================================================
    # 3. DATE COLUMN VALIDATION
    # =========================================================

    if not _validate_column_exists(df, date_column):

        reasons.append(
            "A valid date column could not be identified."
        )

        return ForecastEligibilityResult(
            eligible=False,
            date_column=date_column,
            sales_column=sales_column,
            observations=0,
            unique_dates=0,
            start_date=None,
            end_date=None,
            frequency=None,
            date_valid=False,
            sales_valid=False,
            sufficient_history=False,
            consistent_series=False,
            acceptable_quality=False,
            reasons=reasons,
        )

    parsed_dates = _parse_dates(
        df[date_column]
    )

    valid_date_mask = parsed_dates.notna()

    date_valid_count = int(
        valid_date_mask.sum()
    )

    # =========================================================
    # 4. SALES COLUMN VALIDATION
    # =========================================================

    if not _validate_column_exists(df, sales_column):

        reasons.append(
            "A valid sales/revenue column could not be identified."
        )

        return ForecastEligibilityResult(
            eligible=False,
            date_column=date_column,
            sales_column=sales_column,
            observations=date_valid_count,
            unique_dates=int(
                parsed_dates[
                    valid_date_mask
                ]
                .dt.normalize()
                .nunique()
            ),
            start_date=(
                parsed_dates[
                    valid_date_mask
                ]
                .min()
                .date()
                .isoformat()
                if date_valid_count > 0
                else None
            ),
            end_date=(
                parsed_dates[
                    valid_date_mask
                ]
                .max()
                .date()
                .isoformat()
                if date_valid_count > 0
                else None
            ),
            frequency=None,
            date_valid=True,
            sales_valid=False,
            sufficient_history=False,
            consistent_series=False,
            acceptable_quality=False,
            reasons=reasons,
        )

    numeric_sales = pd.to_numeric(
        df[sales_column],
        errors="coerce",
    )

    valid_sales_mask = numeric_sales.notna()

    sales_valid_count = int(
        valid_sales_mask.sum()
    )

    # =========================================================
    # 5. USABLE FORECASTING OBSERVATIONS
    # =========================================================

    usable_mask = (
        valid_date_mask &
        valid_sales_mask
    )

    usable_dates = parsed_dates[
        usable_mask
    ]

    usable_sales = numeric_sales[
        usable_mask
    ]

    observations = int(
        len(usable_dates)
    )

    unique_dates = int(
        usable_dates
        .dt.normalize()
        .nunique()
    )

    # =========================================================
    # 6. DATE RANGE
    # =========================================================

    if observations > 0:

        start_date = (
            usable_dates
            .min()
            .date()
            .isoformat()
        )

        end_date = (
            usable_dates
            .max()
            .date()
            .isoformat()
        )

    else:

        start_date = None
        end_date = None

    # =========================================================
    # 7. DATA QUALITY
    # =========================================================

    date_invalid_count = int(
        (~valid_date_mask).sum()
    )

    sales_invalid_count = int(
        (~valid_sales_mask).sum()
    )

    invalid_count = (
        date_invalid_count +
        sales_invalid_count
    )

    invalid_ratio = (
        invalid_count / len(df)
        if len(df) > 0
        else 1.0
    )

    acceptable_quality = (
        invalid_ratio <= 0.10
    )

    if not acceptable_quality:

        reasons.append(
            "More than 10% of rows contain invalid "
            "date or sales values."
        )

    # =========================================================
    # 8. SUFFICIENT HISTORY
    # =========================================================

    sufficient_history = (
        observations >= min_observations
    )

    if not sufficient_history:

        reasons.append(
            f"Only {observations} valid observations "
            f"are available; at least "
            f"{min_observations} are required."
        )

    # =========================================================
    # 9. FREQUENCY
    # =========================================================

    frequency = _detect_frequency(
        usable_dates
    )

    if frequency is None:

        reasons.append(
            "The dataset does not contain enough "
            "historical coverage for daily, weekly, "
            "or monthly forecasting."
        )

    # =========================================================
    # 10. TIME-SERIES CONSISTENCY
    # =========================================================

    consistent_series = False

    if unique_dates >= 2:

        normalized_dates = (
            usable_dates
            .dt.normalize()
            .sort_values()
            .drop_duplicates()
        )

        date_differences = (
            normalized_dates
            .diff()
            .dropna()
            .dt.days
        )

        positive_differences = (
            date_differences[
                date_differences > 0
            ]
        )

        if not positive_differences.empty:

            median_gap = float(
                positive_differences.median()
            )

            max_gap = float(
                positive_differences.max()
            )

            if frequency == "D":

                consistent_series = (
                    median_gap <= 2
                    and max_gap <= 31
                )

            elif frequency == "W":

                consistent_series = (
                    median_gap <= 14
                    and max_gap <= 60
                )

            elif frequency == "M":

                consistent_series = (
                    median_gap <= 62
                )

    if not consistent_series:

        reasons.append(
            "The chronological observations are too "
            "irregular for the selected forecasting frequency."
        )

    # =========================================================
    # 11. SALES VALIDATION
    # =========================================================

    sales_valid = (
        sales_valid_count > 0
        and not usable_sales.empty
    )

    if not sales_valid:

        reasons.append(
            f"Sales column '{sales_column}' "
            "contains no usable numeric values."
        )

    # Negative sales values are deliberately NOT rejected.
    #
    # They may represent refunds or returns.
    # The forecasting stage can decide how they should
    # be handled.

    # =========================================================
    # 12. FINAL ELIGIBILITY
    # =========================================================

    eligible = all(
        [
            date_valid_count > 0,
            sales_valid,
            sufficient_history,
            frequency is not None,
            consistent_series,
            acceptable_quality,
        ]
    )

    if eligible:

        reasons.append(
            "Dataset satisfies the minimum forecasting "
            "eligibility criteria."
        )

    return ForecastEligibilityResult(
        eligible=eligible,
        date_column=date_column,
        sales_column=sales_column,
        observations=observations,
        unique_dates=unique_dates,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        date_valid=True,
        sales_valid=sales_valid,
        sufficient_history=sufficient_history,
        consistent_series=consistent_series,
        acceptable_quality=acceptable_quality,
        reasons=reasons,
    )


def is_forecast_eligible(
    df: pd.DataFrame,
    semantic_mapping: Optional[Dict[str, Any]] = None,
    date_column: Optional[str] = None,
    sales_column: Optional[str] = None,
) -> bool:
    """
    Convenience function returning only True/False.
    """

    result = check_forecast_eligibility(
        df=df,
        semantic_mapping=semantic_mapping,
        date_column=date_column,
        sales_column=sales_column,
    )

    return result.eligible