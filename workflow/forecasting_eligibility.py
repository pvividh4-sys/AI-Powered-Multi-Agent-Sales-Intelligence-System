import pandas as pd


# ============================================================
# Forecasting Eligibility Configuration
# ============================================================

MIN_OBSERVATIONS = 30
MIN_UNIQUE_PERIODS = 12
MIN_DATE_PARSE_RATIO = 0.80
MIN_SALES_VALID_RATIO = 0.80


# ============================================================
# Helper: Parse Dates
# ============================================================

def parse_date_column(df, date_column):
    """
    Attempt to parse the selected date column.

    Both common day-first and month-first interpretations
    are tested. The interpretation with the higher valid
    parsing ratio is selected.
    """

    series = df[date_column]

    # Already datetime
    if pd.api.types.is_datetime64_any_dtype(series):

        parsed = pd.to_datetime(
            series,
            errors="coerce"
        )

        return parsed, 1.0, "already_datetime"

    non_null = series.dropna()

    if len(non_null) == 0:

        return (
            pd.Series(
                pd.NaT,
                index=df.index
            ),
            0.0,
            "none"
        )

    # --------------------------------------------------------
    # Standard interpretation
    # --------------------------------------------------------

    parsed_standard = pd.to_datetime(
        series,
        errors="coerce",
        dayfirst=False
    )

    standard_ratio = (
        parsed_standard.notna().sum()
        / len(non_null)
    )

    # --------------------------------------------------------
    # Day-first interpretation
    # --------------------------------------------------------

    parsed_dayfirst = pd.to_datetime(
        series,
        errors="coerce",
        dayfirst=True
    )

    dayfirst_ratio = (
        parsed_dayfirst.notna().sum()
        / len(non_null)
    )

    # --------------------------------------------------------
    # Select better interpretation
    # --------------------------------------------------------

    if dayfirst_ratio > standard_ratio:

        return (
            parsed_dayfirst,
            float(dayfirst_ratio),
            "dayfirst"
        )

    return (
        parsed_standard,
        float(standard_ratio),
        "standard"
    )


# ============================================================
# Helper: Validate Sales Column
# ============================================================

def validate_sales_column(df, sales_column):
    """
    Check whether the sales column contains sufficiently
    valid numerical observations.
    """

    numeric_sales = pd.to_numeric(
        df[sales_column],
        errors="coerce"
    )

    non_null_sales = df[sales_column].notna().sum()

    if non_null_sales == 0:

        return {
            "valid_ratio": 0.0,
            "numeric_sales": numeric_sales,
            "valid_count": 0,
            "invalid_count": 0,
            "status": False
        }

    valid_count = numeric_sales.notna().sum()

    invalid_count = (
        non_null_sales
        - valid_count
    )

    valid_ratio = (
        valid_count
        / non_null_sales
    )

    return {
        "valid_ratio": float(valid_ratio),
        "numeric_sales": numeric_sales,
        "valid_count": int(valid_count),
        "invalid_count": int(invalid_count),
        "status": (
            valid_ratio
            >= MIN_SALES_VALID_RATIO
        )
    }


# ============================================================
# Forecasting Eligibility
# ============================================================

def check_forecasting_eligibility(
    df,
    date_column=None,
    sales_column=None
):
    """
    Determine whether the dataset contains enough reliable
    information for forecasting.

    This function does NOT build a forecast.

    It only determines whether forecasting should be attempted.
    """

    reasons = []
    warnings = []

    # ========================================================
    # Basic Checks
    # ========================================================

    if df is None or df.empty:

        return {
            "eligible": False,
            "status": "Not Eligible",
            "reasons": [
                "Dataset is empty."
            ],
            "warnings": [],
            "date_column": date_column,
            "sales_column": sales_column,
            "observations": 0,
            "unique_periods": 0,
            "date_parse_ratio": 0.0,
            "sales_valid_ratio": 0.0
        }

    # --------------------------------------------------------
    # Date column
    # --------------------------------------------------------

    if not date_column:

        return {
            "eligible": False,
            "status": "Not Eligible",
            "reasons": [
                "No date column was identified."
            ],
            "warnings": [],
            "date_column": None,
            "sales_column": sales_column,
            "observations": len(df),
            "unique_periods": 0,
            "date_parse_ratio": 0.0,
            "sales_valid_ratio": 0.0
        }

    if date_column not in df.columns:

        return {
            "eligible": False,
            "status": "Not Eligible",
            "reasons": [
                f"Date column '{date_column}' "
                "does not exist in the dataset."
            ],
            "warnings": [],
            "date_column": date_column,
            "sales_column": sales_column,
            "observations": len(df),
            "unique_periods": 0,
            "date_parse_ratio": 0.0,
            "sales_valid_ratio": 0.0
        }

    # --------------------------------------------------------
    # Sales column
    # --------------------------------------------------------

    if not sales_column:

        return {
            "eligible": False,
            "status": "Not Eligible",
            "reasons": [
                "No sales/revenue column was identified."
            ],
            "warnings": [],
            "date_column": date_column,
            "sales_column": None,
            "observations": len(df),
            "unique_periods": 0,
            "date_parse_ratio": 0.0,
            "sales_valid_ratio": 0.0
        }

    if sales_column not in df.columns:

        return {
            "eligible": False,
            "status": "Not Eligible",
            "reasons": [
                f"Sales column '{sales_column}' "
                "does not exist in the dataset."
            ],
            "warnings": [],
            "date_column": date_column,
            "sales_column": sales_column,
            "observations": len(df),
            "unique_periods": 0,
            "date_parse_ratio": 0.0,
            "sales_valid_ratio": 0.0
        }

    # ========================================================
    # Date Validation
    # ========================================================

    parsed_dates, date_ratio, date_mode = (
        parse_date_column(
            df,
            date_column
        )
    )

    if date_ratio < MIN_DATE_PARSE_RATIO:

        reasons.append(
            f"Only {date_ratio:.1%} of non-null "
            "date values could be parsed successfully."
        )

    else:

        reasons.append(
            f"{date_ratio:.1%} of non-null date values "
            "can be parsed successfully."
        )

    # ========================================================
    # Sales Validation
    # ========================================================

    sales_validation = validate_sales_column(
        df,
        sales_column
    )

    sales_ratio = sales_validation[
        "valid_ratio"
    ]

    if sales_ratio < MIN_SALES_VALID_RATIO:

        reasons.append(
            f"Only {sales_ratio:.1%} of non-null "
            "sales values are numeric."
        )

    else:

        reasons.append(
            f"{sales_ratio:.1%} of non-null sales "
            "values are numeric."
        )

    # ========================================================
    # Valid Time-Series Observations
    # ========================================================

    valid_mask = (
        parsed_dates.notna()
        &
        sales_validation[
            "numeric_sales"
        ].notna()
    )

    valid_dates = parsed_dates[
        valid_mask
    ]

    valid_sales = sales_validation[
        "numeric_sales"
    ][valid_mask]

    observations = len(valid_dates)

    if observations < MIN_OBSERVATIONS:

        reasons.append(
            f"Only {observations} valid date-sales "
            f"observations are available. "
            f"At least {MIN_OBSERVATIONS} are recommended."
        )

    else:

        reasons.append(
            f"{observations} valid date-sales "
            "observations are available."
        )

    # ========================================================
    # Unique Time Periods
    # ========================================================

    unique_periods = (
        valid_dates
        .dt.normalize()
        .nunique()
    )

    if unique_periods < MIN_UNIQUE_PERIODS:

        reasons.append(
            f"Only {unique_periods} unique date periods "
            f"are available. At least "
            f"{MIN_UNIQUE_PERIODS} are recommended."
        )

    else:

        reasons.append(
            f"{unique_periods} unique date periods "
            "are available."
        )

    # ========================================================
    # Date Range
    # ========================================================

    if observations > 0:

        start_date = valid_dates.min()
        end_date = valid_dates.max()

        date_range_days = (
            end_date - start_date
        ).days

    else:

        start_date = None
        end_date = None
        date_range_days = 0

    # ========================================================
    # Duplicate Date Check
    # ========================================================

    duplicate_date_count = (
        valid_dates
        .dt.normalize()
        .duplicated()
        .sum()
    )

    if duplicate_date_count > 0:

        warnings.append(
            f"{duplicate_date_count} observations "
            "share dates with other observations. "
            "Aggregation may be required before forecasting."
        )

    # ========================================================
    # Date Ordering Check
    # ========================================================

    if observations > 1:

        is_sorted = (
            valid_dates
            .is_monotonic_increasing
        )

        if not is_sorted:

            warnings.append(
                "Date observations are not currently "
                "sorted chronologically."
            )

    # ========================================================
    # Negative Sales Check
    # ========================================================

    negative_sales_count = (
        (valid_sales < 0).sum()
    )

    if negative_sales_count > 0:

        warnings.append(
            f"{negative_sales_count} negative sales "
            "values were detected. These may represent "
            "returns, refunds, or data-quality issues."
        )

    # ========================================================
    # Constant Sales Check
    # ========================================================

    if valid_sales.nunique() <= 1:

        reasons.append(
            "Sales values contain no meaningful variation."
        )

    # ========================================================
    # Final Eligibility
    # ========================================================

    eligible = (
        date_ratio >= MIN_DATE_PARSE_RATIO
        and
        sales_ratio >= MIN_SALES_VALID_RATIO
        and
        observations >= MIN_OBSERVATIONS
        and
        unique_periods >= MIN_UNIQUE_PERIODS
        and
        valid_sales.nunique() > 1
    )

    if eligible:

        status = "Eligible"

        reasons.append(
            "The dataset satisfies the minimum "
            "requirements for attempting forecasting."
        )

    else:

        status = "Not Eligible"

        reasons.append(
            "The dataset does not satisfy all minimum "
            "requirements for forecasting."
        )

    # ========================================================
    # Return Structured Result
    # ========================================================

    return {

        "eligible":
            bool(eligible),

        "status":
            status,

        "date_column":
            date_column,

        "sales_column":
            sales_column,

        "date_parse_ratio":
            round(
                float(date_ratio),
                4
            ),

        "sales_valid_ratio":
            round(
                float(sales_ratio),
                4
            ),

        "observations":
            int(observations),

        "unique_periods":
            int(unique_periods),

        "date_parse_method":
            date_mode,

        "start_date":
            (
                str(start_date.date())
                if start_date is not None
                else None
            ),

        "end_date":
            (
                str(end_date.date())
                if end_date is not None
                else None
            ),

        "date_range_days":
            int(date_range_days),

        "duplicate_date_observations":
            int(duplicate_date_count),

        "negative_sales_count":
            int(negative_sales_count),

        "reasons":
            reasons,

        "warnings":
            warnings
    }