import pandas as pd
from typing import Dict, Any, List, Optional


class CleaningValidationEngine:
    """
    Validates the dataset after cleaning execution.

    IMPORTANT:
    - Does not modify the DataFrame.
    - Compares original and cleaned datasets.
    - Uses Planner semantic mapping when available.
    - Checks data integrity.
    - Checks execution results.
    """

    def validate_calculated_totals(self):
        """Verify total amount/price equals quantity × unit price."""

        def find_column(aliases):
            normalise = lambda value: (
                str(value).strip().lower().replace("_", " ")
            )
            lookup = {
                normalise(col): col
                for col in self.cleaned_df.columns
            }

            for alias in aliases:
                if normalise(alias) in lookup:
                    return lookup[normalise(alias)]

            return None

        quantity_col = find_column(
            ["Quantity", "Qty", "Units Sold"]
        )
        price_col = find_column(
            ["Price per Unit", "Unit Price", "Unit_Price"]
        )

        if not quantity_col or not price_col:
            self.add_check(
                check_name="calculated_totals",
                status="SKIPPED",
                message=(
                    "Quantity or unit-price column was not found."
                ),
            )
            return

        quantity = pd.to_numeric(
            self.cleaned_df[quantity_col], errors="coerce"
        )
        price = pd.to_numeric(
            self.cleaned_df[price_col], errors="coerce"
        )

        expected = quantity * price
        valid = (
            quantity.notna()
            & price.notna()
            & quantity.ge(0)
            & price.ge(0)
        )

        targets = []
        for name in ["Total Amount", "Total_Amount",
                     "Total Price", "Total_Price"]:
            target = find_column([name])
            if target and target not in targets:
                targets.append(target)

        if not targets:
            self.add_check(
                check_name="calculated_totals",
                status="SKIPPED",
                message="No calculated-total column was found.",
            )
            return

        for target in targets:
            actual = pd.to_numeric(
                self.cleaned_df[target], errors="coerce"
            )

            mismatch = valid & (
                actual.isna()
                | ((actual - expected).abs() > 0.01)
            )
            count = int(mismatch.sum())

            self.add_check(
                check_name=f"calculated_total_{target}",
                status="FAILED" if count else "PASSED",
                message=(
                    f"{count} inconsistent value(s) remain in "
                    f"'{target}'."
                    if count
                    else f"'{target}' matches quantity × unit price."
                ),
                after=count,
            )




    def __init__(
        self,
        original_df: pd.DataFrame,
        cleaned_df: pd.DataFrame,
        execution_logs: Optional[List[Dict[str, Any]]] = None,
        semantic_mapping: Optional[Dict[str, Any]] = None
    ):

        self.original_df = original_df.copy()
        self.cleaned_df = cleaned_df.copy()

        self.execution_logs = (
            execution_logs
            if execution_logs is not None
            else []
        )

        self.semantic_mapping = (
            semantic_mapping
            if semantic_mapping is not None
            else {}
        )

        self.checks: List[Dict[str, Any]] = []

    # =========================================================
    # SEMANTIC MAPPING HELPER
    # =========================================================

    def get_semantic_column(
        self,
        semantic_name: str
    ) -> Optional[str]:
        """
        Get physical DataFrame column from Planner semantic mapping.
        """

        value = self.semantic_mapping.get(
            semantic_name
        )

        if value is None:
            return None

        if isinstance(value, str):
            return value

        if isinstance(value, dict):
            return value.get("column")

        return None

    # =========================================================
    # NUMERIC BUSINESS COLUMNS
    # =========================================================

    def get_numeric_business_columns(self) -> List[str]:
        """
        Determine numeric business columns using Planner
        semantic mapping first, followed by a safe fallback.

        This prevents fields such as:

            Sales Rep E-mail

        from being incorrectly classified as numeric merely
        because the column name contains the word 'Sales'.
        """

        columns = []

        # -----------------------------------------------------
        # Planner semantic roles
        # -----------------------------------------------------

        numeric_roles = [
            "sales",
            "revenue",
            "quantity",
            "price",
            "profit",
            "cost"
        ]

        for role in numeric_roles:

            column = self.get_semantic_column(
                role
            )

            if not column:
                continue

            if column not in self.cleaned_df.columns:
                continue

            # Make sure mapped column is actually numeric
            if pd.api.types.is_numeric_dtype(
                self.cleaned_df[column]
            ):

                if column not in columns:
                    columns.append(column)

        # -----------------------------------------------------
        # Safe fallback
        # -----------------------------------------------------

        numeric_keywords = [
            "revenue",
            "amount",
            "price",
            "quantity",
            "profit",
            "cost"
        ]

        excluded_keywords = [
            "id",
            "age",
            "email",
            "e-mail",
            "mail",
            "phone",
            "mobile",
            "address",
            "city",
            "state",
            "country"
        ]

        for column in self.cleaned_df.columns:

            if column in columns:
                continue

            name = column.lower().strip()

            # Exclude obvious non-business fields
            if any(
                keyword in name
                for keyword in excluded_keywords
            ):
                continue

            # Require business-measure keyword
            if not any(
                keyword in name
                for keyword in numeric_keywords
            ):
                continue

            # Require actual numeric dtype
            if pd.api.types.is_numeric_dtype(
                self.cleaned_df[column]
            ):

                columns.append(column)

        return columns

    # =========================================================
    # ADD CHECK
    # =========================================================

    def add_check(
        self,
        check_name: str,
        status: str,
        message: str,
        before: Any = None,
        after: Any = None
    ):

        self.checks.append({
            "check_name": check_name,
            "status": status,
            "message": message,
            "before": before,
            "after": after
        })

    # =========================================================
    # STRUCTURE VALIDATION
    # =========================================================

    def validate_structure(self):

        original_rows = len(
            self.original_df
        )

        cleaned_rows = len(
            self.cleaned_df
        )

        original_columns = list(
            self.original_df.columns
        )

        cleaned_columns = list(
            self.cleaned_df.columns
        )

        # -----------------------------------------------------
        # Columns
        # -----------------------------------------------------

        if original_columns == cleaned_columns:

            self.add_check(
                check_name="column_structure",
                status="PASSED",
                message=(
                    "Column structure is unchanged."
                ),
                before=len(original_columns),
                after=len(cleaned_columns)
            )

        else:

            self.add_check(
                check_name="column_structure",
                status="WARNING",
                message=(
                    "Column structure changed during execution."
                ),
                before=original_columns,
                after=cleaned_columns
            )

        # -----------------------------------------------------
        # Rows
        # -----------------------------------------------------

        if cleaned_rows <= original_rows:

            self.add_check(
                check_name="row_count",
                status="PASSED",
                message=(
                    "Cleaned dataset does not contain more "
                    "rows than the original dataset."
                ),
                before=original_rows,
                after=cleaned_rows
            )

        else:

            self.add_check(
                check_name="row_count",
                status="FAILED",
                message=(
                    "Cleaned dataset contains more rows than "
                    "the original dataset."
                ),
                before=original_rows,
                after=cleaned_rows
            )

    # =========================================================
    # MISSING VALUES
    # =========================================================

    def validate_missing_values(self):

        before = int(
            self.original_df.isna().sum().sum()
        )

        after = int(
            self.cleaned_df.isna().sum().sum()
        )

        if after <= before:

            self.add_check(
                check_name="missing_values",
                status="PASSED",
                message=(
                    "Missing values did not increase after "
                    "cleaning."
                ),
                before=before,
                after=after
            )

        else:

            self.add_check(
                check_name="missing_values",
                status="FAILED",
                message=(
                    "Missing values increased after cleaning."
                ),
                before=before,
                after=after
            )

    # =========================================================
    # DUPLICATES
    # =========================================================

    def validate_duplicates(self):

        before = int(
            self.original_df.duplicated().sum()
        )

        after = int(
            self.cleaned_df.duplicated().sum()
        )

        if after <= before:

            self.add_check(
                check_name="duplicate_rows",
                status="PASSED",
                message=(
                    "Duplicate rows did not increase."
                ),
                before=before,
                after=after
            )

        else:

            self.add_check(
                check_name="duplicate_rows",
                status="FAILED",
                message=(
                    "Duplicate rows increased after cleaning."
                ),
                before=before,
                after=after
            )

    # =========================================================
    # DATA TYPE VALIDATION
    # =========================================================

    def validate_data_types(self):

        numeric_columns = (
            self.get_numeric_business_columns()
        )

        problems = []

        for column in numeric_columns:

            if not pd.api.types.is_numeric_dtype(
                self.cleaned_df[column]
            ):

                problems.append(column)

        if not problems:

            self.add_check(
                check_name="numeric_data_types",
                status="PASSED",
                message=(
                    "Planner-identified business numeric "
                    "columns have valid numeric data types."
                )
            )

        else:

            self.add_check(
                check_name="numeric_data_types",
                status="FAILED",
                message=(
                    "The following business numeric columns "
                    f"are not numeric: {problems}"
                )
            )

    # =========================================================
    # DATE VALIDATION
    # =========================================================

    def validate_dates(
        self,
        date_column: Optional[str] = None
    ):

        # -----------------------------------------------------
        # Use Planner mapping first
        # -----------------------------------------------------

        if date_column is None:

            date_column = self.get_semantic_column(
                "date"
            )

        # -----------------------------------------------------
        # Fallback
        # -----------------------------------------------------

        if date_column is None:

            candidates = []

            for column in self.cleaned_df.columns:

                name = column.lower().strip()

                if (
                    "date" in name
                    or "timestamp" in name
                    or name == "time"
                ):

                    candidates.append(column)

            if candidates:

                date_column = candidates[0]

        # -----------------------------------------------------
        # No date column
        # -----------------------------------------------------

        if date_column is None:

            self.add_check(
                check_name="date_validation",
                status="SKIPPED",
                message=(
                    "No date column identified."
                )
            )

            return

        # -----------------------------------------------------
        # Column doesn't exist
        # -----------------------------------------------------

        if date_column not in self.cleaned_df.columns:

            self.add_check(
                check_name="date_validation",
                status="FAILED",
                message=(
                    f"Date column '{date_column}' does "
                    f"not exist."
                )
            )

            return

        series = self.cleaned_df[
            date_column
        ]

        # -----------------------------------------------------
        # Datetime dtype
        # -----------------------------------------------------

        if pd.api.types.is_datetime64_any_dtype(
            series
        ):

            invalid_dates = int(
                series.isna().sum()
            )

            self.add_check(
                check_name="date_validation",
                status="PASSED",
                message=(
                    f"Date column '{date_column}' is "
                    f"stored as datetime."
                ),
                after=invalid_dates
            )

            return

        # -----------------------------------------------------
        # Parse dates
        # -----------------------------------------------------

        parsed = pd.to_datetime(
            series,
            errors="coerce",
            dayfirst=True
        )

        invalid_mask = (
            series.notna()
            & parsed.isna()
        )

        invalid_count = int(
            invalid_mask.sum()
        )

        if invalid_count == 0:

            self.add_check(
                check_name="date_validation",
                status="PASSED",
                message=(
                    f"All non-empty values in "
                    f"'{date_column}' are valid dates."
                ),
                after=0
            )

        else:

            self.add_check(
                check_name="date_validation",
                status="FAILED",
                message=(
                    f"{invalid_count} invalid date values "
                    f"remain in '{date_column}'."
                ),
                after=invalid_count
            )

    # =========================================================
    # EXECUTION LOG VALIDATION
    # =========================================================

    def validate_execution_logs(self):

        failed = 0
        executed = 0
        skipped = 0

        for log in self.execution_logs:

            status = str(
                log.get("status", "")
            ).lower()

            if status == "failed":

                failed += 1

            elif status == "executed":

                executed += 1

            elif status == "skipped":

                skipped += 1

        if failed == 0:

            self.add_check(
                check_name="execution_logs",
                status="PASSED",
                message=(
                    f"Execution completed without failures. "
                    f"Executed: {executed}, "
                    f"Skipped: {skipped}."
                )
            )

        else:

            self.add_check(
                check_name="execution_logs",
                status="FAILED",
                message=(
                    f"{failed} execution operation(s) failed. "
                    f"Executed: {executed}, "
                    f"Skipped: {skipped}."
                )
            )

    # =========================================================
    # DATA LOSS VALIDATION
    # =========================================================

    def validate_data_loss(self):

        original_rows = len(
            self.original_df
        )

        cleaned_rows = len(
            self.cleaned_df
        )

        rows_removed = (
            original_rows - cleaned_rows
        )

        # -----------------------------------------------------
        # No rows removed
        # -----------------------------------------------------

        if rows_removed == 0:

            self.add_check(
                check_name="data_loss",
                status="PASSED",
                message="No rows were removed."
            )

            return

        # -----------------------------------------------------
        # Compare with execution log
        # -----------------------------------------------------

        logged_removals = 0

        for log in self.execution_logs:

            if log.get("status") != "executed":
                continue

            action = str(
                log.get("action", "")
            ).lower()

            if (
                "remove" in action
                or "delete" in action
            ):

                logged_removals += int(
                    log.get(
                        "affected_rows",
                        0
                    )
                )

        if logged_removals == rows_removed:

            self.add_check(
                check_name="data_loss",
                status="PASSED",
                message=(
                    f"{rows_removed} rows were removed "
                    f"and the removal is fully explained "
                    f"by the execution log."
                ),
                before=original_rows,
                after=cleaned_rows
            )

        else:

            self.add_check(
                check_name="data_loss",
                status="FAILED",
                message=(
                    f"{rows_removed} rows were removed, "
                    f"but execution logs account for only "
                    f"{logged_removals} rows."
                ),
                before=original_rows,
                after=cleaned_rows
            )

    # =========================================================
    # EMPTY DATASET
    # =========================================================

    def validate_not_empty(self):

        if len(self.cleaned_df) > 0:

            self.add_check(
                check_name="dataset_not_empty",
                status="PASSED",
                message=(
                    "Cleaned dataset contains records."
                ),
                after=len(self.cleaned_df)
            )

        else:

            self.add_check(
                check_name="dataset_not_empty",
                status="FAILED",
                message=(
                    "Cleaning resulted in an empty dataset."
                )
            )

    # =========================================================
    # RUN ALL VALIDATIONS
    # =========================================================

    def validate_all(
        self,
        date_column: Optional[str] = None
    ):

        self.checks = []

        self.validate_structure()

        self.validate_missing_values()

        self.validate_duplicates()

        self.validate_data_types()

        self.validate_dates(
            date_column=date_column
        )

        self.validate_execution_logs()

        self.validate_data_loss()

        self.validate_not_empty()

        # -----------------------------------------------------
        # Overall status
        # -----------------------------------------------------

        failed_checks = [
            check
            for check in self.checks
            if check["status"] == "FAILED"
        ]

        warnings = [
            check
            for check in self.checks
            if check["status"] == "WARNING"
        ]

        if failed_checks:

            overall_status = "FAILED"

        elif warnings:

            overall_status = "WARNING"

        else:

            overall_status = "PASSED"

        return {
            "overall_status": overall_status,
            "total_checks": len(self.checks),
            "passed_checks": sum(
                1
                for check in self.checks
                if check["status"] == "PASSED"
            ),
            "failed_checks": len(
                failed_checks
            ),
            "warning_checks": len(
                warnings
            ),
            "checks": self.checks
        }


# =============================================================
# CONVENIENCE FUNCTION
# =============================================================

def validate_cleaned_data(
    original_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    execution_logs: Optional[
        List[Dict[str, Any]]
    ] = None,
    date_column: Optional[str] = None,
    semantic_mapping: Optional[Dict[str, Any]] = None
):

    validator = CleaningValidationEngine(
        original_df=original_df,
        cleaned_df=cleaned_df,
        execution_logs=execution_logs,
        semantic_mapping=semantic_mapping
    )

    return validator.validate_all(
        date_column=date_column
    )