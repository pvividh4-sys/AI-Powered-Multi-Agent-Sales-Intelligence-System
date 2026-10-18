import pandas as pd


def detect_date_columns(df):
    """
    Detect columns that are likely to contain dates.

    The function does not depend only on the column name.
    It checks both:
    1. Column-name hints
    2. Actual values and their ability to be parsed as dates

    Returns:
        list: Possible date columns
    """

    possible_date_columns = []

    # Words that commonly indicate a date/time column
    date_keywords = [
        "date",
        "time",
        "timestamp",
        "datetime",
        "day",
        "month",
        "year"
    ]

    for column in df.columns:

        series = df[column]

        # --------------------------------------------------
        # Case 1: Already a datetime column
        # --------------------------------------------------

        if pd.api.types.is_datetime64_any_dtype(series):

            possible_date_columns.append(column)
            continue

        # --------------------------------------------------
        # Only attempt string/date inference on object columns
        # --------------------------------------------------

        if not (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        ):
            continue

        # Remove missing values and convert to strings
        non_null_values = series.dropna().astype(str).str.strip()

        if len(non_null_values) == 0:
            continue

        # --------------------------------------------------
        # Attempt several common date formats
        # --------------------------------------------------

        parsed_results = []

        formats_to_try = [
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%Y/%m/%d",
            "%d/%m/%y",
            "%m/%d/%y",
            "%d-%m-%y",
            "%m-%d-%y"
        ]

        for date_format in formats_to_try:

            parsed = pd.to_datetime(
                non_null_values,
                format=date_format,
                errors="coerce"
            )

            valid_ratio = parsed.notna().mean()

            parsed_results.append(valid_ratio)

        # --------------------------------------------------
        # Also try Pandas automatic date parsing
        # --------------------------------------------------

        try:

            parsed_normal = pd.to_datetime(
                non_null_values,
                errors="coerce",
                dayfirst=False
            )

            normal_ratio = parsed_normal.notna().mean()

        except Exception:

            normal_ratio = 0

        try:

            parsed_dayfirst = pd.to_datetime(
                non_null_values,
                errors="coerce",
                dayfirst=True
            )

            dayfirst_ratio = parsed_dayfirst.notna().mean()

        except Exception:

            dayfirst_ratio = 0

        # Best parsing result
        best_ratio = max(
            max(parsed_results),
            normal_ratio,
            dayfirst_ratio
        )

        # --------------------------------------------------
        # Column-name evidence
        # --------------------------------------------------

        column_name = str(column).lower().strip()

        has_date_keyword = any(
            keyword in column_name
            for keyword in date_keywords
        )

        # --------------------------------------------------
        # Final decision
        # --------------------------------------------------

        # Strong evidence:
        # At least 80% of values successfully parse as dates
        if best_ratio >= 0.80:

            possible_date_columns.append(column)

        # Additional protection:
        # If the column name strongly indicates a date,
        # accept it when at least 50% of values parse.
        elif has_date_keyword and best_ratio >= 0.50:

            possible_date_columns.append(column)

    return possible_date_columns


def profile_dataset(df):
    """
    Create a structured profile of an uploaded
    retail/e-commerce dataset.
    """

    profile = {}

    # --------------------------------------------------
    # Basic Dataset Information
    # --------------------------------------------------

    profile["rows"] = int(df.shape[0])

    profile["columns"] = int(df.shape[1])

    profile["column_names"] = df.columns.tolist()

    # --------------------------------------------------
    # Physical Data Types
    # --------------------------------------------------

    profile["data_types"] = {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }

    # --------------------------------------------------
    # Missing Values
    # --------------------------------------------------

    profile["missing_values"] = {
        column: int(value)
        for column, value in df.isna().sum().items()
    }

    # --------------------------------------------------
    # Duplicate Rows
    # --------------------------------------------------

    profile["duplicate_rows"] = int(
        df.duplicated().sum()
    )

    # --------------------------------------------------
    # Unique Values
    # --------------------------------------------------

    profile["unique_values"] = {
        column: int(value)
        for column, value in df.nunique().items()
    }

    # --------------------------------------------------
    # Numerical Columns
    # --------------------------------------------------

    profile["numerical_columns"] = (
        df.select_dtypes(include="number")
        .columns
        .tolist()
    )

    # --------------------------------------------------
    # Categorical Columns
    # --------------------------------------------------

    profile["categorical_columns"] = (
        df.select_dtypes(
            include=["object", "category"]
        )
        .columns
        .tolist()
    )

    # --------------------------------------------------
    # Possible Date Columns
    # --------------------------------------------------

    profile["possible_date_columns"] = detect_date_columns(df)

    return profile