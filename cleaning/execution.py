import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class CleaningExecutionEngine:
    """
    Executes approved cleaning decisions.

    IMPORTANT:
    - Works on a copy of the original DataFrame.
    - Does not make independent cleaning decisions.
    - Only executes actions explicitly approved by the user/policy.
    - Every execution produces an execution log.
    - Supports both dictionary decisions and CleaningDecision objects.
    """

    def correct_calculated_total(
        self,
        issue_id: str,
        quantity_column: str,
        unit_price_column: str,
        target_column: str,
    ):
        """Recalculate a total after explicit user approval."""

        required = [
            quantity_column,
            unit_price_column,
            target_column,
        ]

        missing = [
            col for col in required
            if col not in self.df.columns
        ]

        if missing:
            self.log_execution(
                issue_id=issue_id,
                issue_type="calculation_mismatch",
                column=target_column,
                action="Recalculate total",
                status="failed",
                message=f"Missing required columns: {missing}",
            )
            return

        quantity = pd.to_numeric(
            self.df[quantity_column], errors="coerce"
        )
        price = pd.to_numeric(
            self.df[unit_price_column], errors="coerce"
        )
        actual = pd.to_numeric(
            self.df[target_column], errors="coerce"
        )

        expected = (quantity * price).round(2)

        valid_inputs = (
            quantity.notna()
            & price.notna()
            & quantity.ge(0)
            & price.ge(0)
        )

        mismatch = (
            valid_inputs
            & (
                actual.isna()
                | ((actual - expected).abs() > 0.01)
            )
        )

        affected = int(mismatch.sum())

        self.df.loc[mismatch, target_column] = expected[mismatch]

        self.log_execution(
            issue_id=issue_id,
            issue_type="calculation_mismatch",
            column=target_column,
            action="Recalculate total using quantity × unit price",
            status="executed",
            affected_rows=affected,
            message=(
                f"Recalculated {affected} values in "
                f"'{target_column}'."
            ),
        )





    def __init__(self, df: pd.DataFrame):

        self.original_df = df.copy()
        self.df = df.copy()

        self.execution_logs: List[Dict[str, Any]] = []

    # =========================================================
    # DECISION VALUE HELPER
    # =========================================================

    @staticmethod
    def _get_value(
        decision: Any,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get a value from either:
        - dictionary
        - dataclass/object

        This allows the execution engine to work with the
        CleaningDecision dataclass returned by the Decision Engine.
        """

        if isinstance(decision, dict):
            return decision.get(key, default)

        return getattr(
            decision,
            key,
            default
        )

    # =========================================================
    # LOG EXECUTION
    # =========================================================

    def log_execution(
        self,
        issue_id: str,
        issue_type: str,
        column: str,
        action: str,
        status: str,
        affected_rows: int = 0,
        message: str = ""
    ):

        log = {
            "issue_id": issue_id,
            "issue_type": issue_type,
            "column": column,
            "action": action,
            "status": status,
            "affected_rows": int(affected_rows),
            "message": message
        }

        self.execution_logs.append(log)

    # =========================================================
    # EXACT DUPLICATES
    # =========================================================

    def remove_exact_duplicates(
        self,
        issue_id: str
    ):

        before = len(self.df)

        self.df = self.df.drop_duplicates().reset_index(
            drop=True
        )

        removed = before - len(self.df)

        self.log_execution(
            issue_id=issue_id,
            issue_type="exact_duplicate",
            column="ALL_COLUMNS",
            action="Remove exact duplicate rows",
            status="executed",
            affected_rows=removed,
            message=(
                f"{removed} exact duplicate rows removed."
            )
        )

    # =========================================================
    # MISSING CATEGORICAL VALUES
    # =========================================================

    def fill_missing_categorical(
        self,
        column: str,
        issue_id: str
    ):

        if column not in self.df.columns:

            self.log_execution(
                issue_id=issue_id,
                issue_type="missing_values",
                column=column,
                action="Fill missing categorical values",
                status="failed",
                message="Column does not exist."
            )

            return

        missing_mask = self.df[column].isna()

        affected_rows = int(
            missing_mask.sum()
        )

        if affected_rows == 0:

            self.log_execution(
                issue_id=issue_id,
                issue_type="missing_values",
                column=column,
                action="Fill missing categorical values",
                status="skipped",
                message="No missing values found."
            )

            return

        self.df.loc[
            missing_mask,
            column
        ] = "Unknown"

        self.log_execution(
            issue_id=issue_id,
            issue_type="missing_values",
            column=column,
            action="Fill missing categorical values",
            status="executed",
            affected_rows=affected_rows,
            message=(
                f"{affected_rows} missing values replaced "
                f"with 'Unknown'."
            )
        )

    # =========================================================
    # NUMERIC CONVERSION
    # =========================================================

    def convert_to_numeric(
        self,
        column: str,
        issue_id: str,
        invalid_strategy: str = "median"
    ):

        if column not in self.df.columns:

            self.log_execution(
                issue_id=issue_id,
                issue_type="numeric_conversion",
                column=column,
                action="Convert column to numeric",
                status="failed",
                message="Column does not exist."
            )

            return

        original = self.df[column]

        converted = pd.to_numeric(
            original,
            errors="coerce"
        )

        invalid_mask = (
            original.notna()
            & converted.isna()
        )

        invalid_count = int(
            invalid_mask.sum()
        )

        # -----------------------------------------------------
        # No invalid values
        # -----------------------------------------------------

        if invalid_count == 0:

            self.df[column] = converted

            self.log_execution(
                issue_id=issue_id,
                issue_type="numeric_conversion",
                column=column,
                action="Convert column to numeric",
                status="executed",
                affected_rows=0,
                message="Column successfully converted to numeric."
            )

            return

        # -----------------------------------------------------
        # Keep invalid values
        # -----------------------------------------------------

        if invalid_strategy == "keep":

            self.df[column] = converted

            self.log_execution(
                issue_id=issue_id,
                issue_type="numeric_conversion",
                column=column,
                action="Convert valid values; keep invalid values",
                status="executed",
                affected_rows=invalid_count,
                message=(
                    f"{invalid_count} invalid values became NaN."
                )
            )

            return

        # -----------------------------------------------------
        # Median replacement
        # -----------------------------------------------------

        if invalid_strategy == "median":

            valid_values = converted.dropna()

            if len(valid_values) == 0:

                self.log_execution(
                    issue_id=issue_id,
                    issue_type="numeric_conversion",
                    column=column,
                    action="Convert and median-impute",
                    status="failed",
                    affected_rows=invalid_count,
                    message=(
                        "No valid numeric values available "
                        "to calculate median."
                    )
                )

                return

            median_value = valid_values.median()

            converted.loc[invalid_mask] = median_value

            self.df[column] = converted

            self.log_execution(
                issue_id=issue_id,
                issue_type="numeric_conversion",
                column=column,
                action="Convert and median-impute",
                status="executed",
                affected_rows=invalid_count,
                message=(
                    f"{invalid_count} invalid values replaced "
                    f"with median {median_value}."
                )
            )

            return

        # -----------------------------------------------------
        # Unknown strategy
        # -----------------------------------------------------

        self.log_execution(
            issue_id=issue_id,
            issue_type="numeric_conversion",
            column=column,
            action="Convert column to numeric",
            status="failed",
            affected_rows=invalid_count,
            message=(
                f"Unknown invalid-value strategy: "
                f"{invalid_strategy}"
            )
        )

    # =========================================================
    # DATE CONVERSION
    # =========================================================

    def convert_to_date(
        self,
        column: str,
        issue_id: str,
        dayfirst: bool = True
    ):

        if column not in self.df.columns:

            self.log_execution(
                issue_id=issue_id,
                issue_type="invalid_dates",
                column=column,
                action="Convert column to datetime",
                status="failed",
                message="Column does not exist."
            )

            return

        original = self.df[column]

        converted = pd.to_datetime(
            original,
            errors="coerce",
            dayfirst=dayfirst
        )

        invalid_mask = (
            original.notna()
            & converted.isna()
        )

        invalid_count = int(
            invalid_mask.sum()
        )

        self.df[column] = converted

        if invalid_count == 0:

            self.log_execution(
                issue_id=issue_id,
                issue_type="invalid_dates",
                column=column,
                action="Convert column to datetime",
                status="executed",
                affected_rows=0,
                message=(
                    "All non-empty date values converted successfully."
                )
            )

        else:

            self.log_execution(
                issue_id=issue_id,
                issue_type="invalid_dates",
                column=column,
                action="Convert column to datetime",
                status="executed",
                affected_rows=invalid_count,
                message=(
                    f"{invalid_count} invalid date values "
                    f"became NaT."
                )
            )

    # =========================================================
    # OUTLIER REMOVAL
    # =========================================================

    def remove_outliers(
        self,
        column: str,
        issue_id: str,
        lower_bound: float,
        upper_bound: float
    ):

        if column not in self.df.columns:

            self.log_execution(
                issue_id=issue_id,
                issue_type="statistical_outlier",
                column=column,
                action="Remove statistical outliers",
                status="failed",
                message="Column does not exist."
            )

            return

        before = len(self.df)

        outlier_mask = (
            (self.df[column] < lower_bound)
            | (self.df[column] > upper_bound)
        )

        outlier_count = int(
            outlier_mask.sum()
        )

        self.df = self.df.loc[
            ~outlier_mask
        ].reset_index(drop=True)

        removed = before - len(self.df)

        self.log_execution(
            issue_id=issue_id,
            issue_type="statistical_outlier",
            column=column,
            action="Remove statistical outliers",
            status="executed",
            affected_rows=removed,
            message=(
                f"{removed} rows removed using IQR boundaries "
                f"({lower_bound}, {upper_bound})."
            )
        )

    # =========================================================
    # DUPLICATE IDENTIFIER REMOVAL
    # =========================================================

    def remove_duplicate_identifiers(
        self,
        column: str,
        issue_id: str
    ):

        if column not in self.df.columns:

            self.log_execution(
                issue_id=issue_id,
                issue_type="duplicate_identifier",
                column=column,
                action="Remove duplicate identifiers",
                status="failed",
                message="Column does not exist."
            )

            return

        before = len(self.df)

        self.df = self.df.drop_duplicates(
            subset=[column],
            keep="first"
        ).reset_index(drop=True)

        removed = before - len(self.df)

        self.log_execution(
            issue_id=issue_id,
            issue_type="duplicate_identifier",
            column=column,
            action="Remove duplicate identifiers",
            status="executed",
            affected_rows=removed,
            message=(
                f"{removed} rows removed based on duplicate "
                f"identifier values."
            )
        )

    # =========================================================
    # EXECUTE SINGLE DECISION
    # =========================================================

    def execute_decision(
        self,
        decision: Any
    ):
        """
        Execute one CleaningDecision.

        Supports both dictionaries and CleaningDecision objects.
        """

        issue_id = self._get_value(
            decision,
            "issue_id",
            "UNKNOWN"
        )

        issue_type = self._get_value(
            decision,
            "issue_type",
            ""
        )

        column = self._get_value(
            decision,
            "column",
            ""
        )

        # -----------------------------------------------------
        # USER APPROVAL CHECK
        # -----------------------------------------------------

        user_decision = self._get_value(
            decision,
            "user_decision"
        )

        requires_approval = self._get_value(
            decision,
            "requires_approval",
            True
        )

        # -----------------------------------------------------
        # If approval is required, require explicit approval
        # -----------------------------------------------------

        if requires_approval:

            if str(user_decision).upper() != "APPROVE":

                self.log_execution(
                    issue_id=issue_id,
                    issue_type=issue_type,
                    column=column,
                    action="Not executed",
                    status="skipped",
                    message=(
                        "Execution requires explicit user approval."
                    )
                )

                return

        # -----------------------------------------------------
        # Exact duplicates
        # -----------------------------------------------------

        if issue_type == "exact_duplicate":

            self.remove_exact_duplicates(
                issue_id=issue_id
            )

        # -----------------------------------------------------
        # Missing values
        # -----------------------------------------------------

        elif issue_type == "missing_values":

            action = str(
                self._get_value(
                    decision,
                    "recommended_action",
                    ""
                )
            ).lower()

            if "unknown" in action:

                self.fill_missing_categorical(
                    column=column,
                    issue_id=issue_id
                )

            else:

                self.log_execution(
                    issue_id=issue_id,
                    issue_type=issue_type,
                    column=column,
                    action=action,
                    status="skipped",
                    message=(
                        "No executable missing-value strategy "
                        "was selected."
                    )
                )

        # -----------------------------------------------------
        # Numeric conversion
        # -----------------------------------------------------

        elif issue_type == "numeric_conversion":

            strategy = self._get_value(
                decision,
                "execution_strategy",
                "median"
            )

            self.convert_to_numeric(
                column=column,
                issue_id=issue_id,
                invalid_strategy=strategy
            )

        # -----------------------------------------------------
        # Invalid dates
        # -----------------------------------------------------

        elif issue_type == "invalid_dates":

            self.convert_to_date(
                column=column,
                issue_id=issue_id,
                dayfirst=True
            )

        # -----------------------------------------------------
        # Statistical outliers
        # -----------------------------------------------------

        elif issue_type == "statistical_outlier":

            lower_bound = self._get_value(
                decision,
                "lower_bound"
            )

            upper_bound = self._get_value(
                decision,
                "upper_bound"
            )

            if (
                lower_bound is None
                or upper_bound is None
            ):

                self.log_execution(
                    issue_id=issue_id,
                    issue_type=issue_type,
                    column=column,
                    action="Remove statistical outliers",
                    status="failed",
                    message=(
                        "IQR boundaries were not provided."
                    )
                )

                return

            self.remove_outliers(
                column=column,
                issue_id=issue_id,
                lower_bound=lower_bound,
                upper_bound=upper_bound
            )

        # -----------------------------------------------------
        # Duplicate identifier
        # -----------------------------------------------------

        elif issue_type == "duplicate_identifier":

            self.remove_duplicate_identifiers(
                column=column,
                issue_id=issue_id
            )

        # -----------------------------------------------------
        # Negative values
        # -----------------------------------------------------

        elif issue_type == "negative_value":

            self.log_execution(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                action="Manual review",
                status="skipped",
                message=(
                    "Negative values require business-context "
                    "review before execution."
                )
            )

        elif issue_type == "calculation_mismatch":
            details = self._get_value(
                decision, "details", {}
            ) or {}

            quantity_col = details.get("quantity_column")
            price_col = details.get("unit_price_column")
            target_col = details.get("target_column") or column

            if not quantity_col or not price_col:
                self.log_execution(
                    issue_id=issue_id,
                    issue_type=issue_type,
                    column=column,
                    action="Recalculate total",
                    status="failed",
                    message="Required calculation metadata is missing.",
                )
                return

            self.correct_calculated_total(
                issue_id=issue_id,
                quantity_column=quantity_col,
                unit_price_column=price_col,
                target_column=target_col,
            )

        # -----------------------------------------------------
        # Unknown issue
        # -----------------------------------------------------

        else:

            self.log_execution(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                action="Unknown action",
                status="failed",
                message=(
                    "No execution handler exists for this "
                    "issue type."
                )
            )

    # =========================================================
    # EXECUTE ALL DECISIONS
    # =========================================================

    def execute_decisions(
        self,
        decisions: List[Any]
    ):
        """
        Execute all supplied decisions.

        Returns:
            cleaned DataFrame
        """

        for decision in decisions:

            self.execute_decision(
                decision
            )

        return self.df.copy()

    # =========================================================
    # RESULTS
    # =========================================================

    def get_cleaned_data(self):

        return self.df.copy()

    def get_execution_logs(self):

        return self.execution_logs.copy()