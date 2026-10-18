import pandas as pd
from typing import Dict, List, Optional


class DataQualityDetector:
    """
    Detects data-quality issues without modifying the DataFrame.

    The detector can use semantic mappings produced by the
    Planner Agent, but it validates those mappings before
    using them for numeric/business analysis.

    Detection only:
        - No data mutation
        - No row deletion
        - No imputation
        - No automatic cleaning
    """

    def __init__(
        self,
        df: pd.DataFrame,
        semantic_mapping: Optional[Dict] = None
    ):
        self.df = df.copy()
        self.semantic_mapping = semantic_mapping or {}

        self.issues: List[Dict] = []

    # =========================================================
    # ADD ISSUE
    # =========================================================

    def add_issue(
        self,
        issue_id: str,
        issue_type: str,
        column: str,
        affected_rows: int,
        evidence: str,
        risk_level: str,
        requires_approval: bool,
        **extra
    ):
        issue = {
            "issue_id": issue_id,
            "issue_type": issue_type,
            "column": column,
            "affected_rows": int(affected_rows),
            "evidence": evidence,
            "detected_by": "Python",
            "risk_level": risk_level,
            "requires_approval": requires_approval
        }

        issue.update(extra)

        self.issues.append(issue)

    # =========================================================
    # SEMANTIC MAPPING
    # =========================================================

    def get_semantic_column(
        self,
        semantic_name: str
    ) -> Optional[str]:

        value = self.semantic_mapping.get(semantic_name)

        if value is None:
            return None

        # Example:
        # "date": "Date"
        if isinstance(value, str):
            return value

        # Example:
        # "date": {
        #     "column": "Date",
        #     "confidence": 0.95
        # }
        if isinstance(value, dict):
            return value.get("column")

        return None

    # =========================================================
    # VALIDATE NUMERIC SEMANTIC MAPPING
    # =========================================================

    def is_valid_numeric_mapping(
        self,
        column: str
    ) -> bool:
        """
        Validate whether a Planner-mapped column is suitable
        for numeric/business analysis.

        This prevents semantic-mapping mistakes such as:

            sales → Sales Rep E-mail

        """

        if column not in self.df.columns:
            return False

        name = column.lower().strip()

        # -----------------------------------------------------
        # Clearly non-numeric semantic fields
        # -----------------------------------------------------

        excluded_keywords = [
            "email",
            "e-mail",
            "mail",
            "id",
            "identifier",
            "phone",
            "mobile",
            "address",
            "city",
            "state",
            "country",
            "gender",
            "category",
            "type",
            "status",
            "name"
        ]

        if any(
            keyword in name
            for keyword in excluded_keywords
        ):
            return False

        series = self.df[column]

        # -----------------------------------------------------
        # Already numeric
        # -----------------------------------------------------

        if pd.api.types.is_numeric_dtype(series):
            return True

        # -----------------------------------------------------
        # Object/string column:
        # determine whether it is genuinely numeric-like
        # -----------------------------------------------------

        non_null = series.dropna()

        if len(non_null) == 0:
            return False

        converted = pd.to_numeric(
            non_null,
            errors="coerce"
        )

        numeric_ratio = converted.notna().mean()

        # Require at least 80% numeric-looking values before
        # considering a text column a numeric candidate.
        return numeric_ratio >= 0.80

    # =========================================================
    # NUMERIC BUSINESS COLUMNS
    # =========================================================

    def get_numeric_business_columns(self) -> List[str]:

        columns = []

        # -----------------------------------------------------
        # 1. Planner semantic mapping
        # -----------------------------------------------------

        semantic_numeric_roles = [
            "sales",
            "revenue",
            "quantity",
            "price",
            "profit",
            "cost"
        ]

        for role in semantic_numeric_roles:

            column = self.get_semantic_column(role)

            if not column:
                continue

            if column not in self.df.columns:
                continue

            # IMPORTANT:
            # Validate the Planner's mapping.
            if not self.is_valid_numeric_mapping(column):
                continue

            if column not in columns:
                columns.append(column)

        # -----------------------------------------------------
        # 2. Safe fallback detection
        # -----------------------------------------------------

        numeric_keywords = [
            "sales",
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
            "zip",
            "postal",
            "phone",
            "mobile",
            "email",
            "e-mail",
            "mail",
            "address",
            "city",
            "state",
            "country"
        ]

        for column in self.df.columns:

            if column in columns:
                continue

            name = column.lower().strip()

            # Explicitly exclude obvious non-business measures
            if any(
                keyword in name
                for keyword in excluded_keywords
            ):
                continue

            # Name must suggest a business measure
            if not any(
                keyword in name
                for keyword in numeric_keywords
            ):
                continue

            # Validate actual values
            if not self.is_valid_numeric_mapping(column):
                continue

            columns.append(column)

        return columns

    # =========================================================
    # BASIC QUALITY
    # =========================================================

    def detect_basic_quality(self) -> Dict:

        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "missing_values": int(
                self.df.isna().sum().sum()
            ),
            "duplicate_rows": int(
                self.df.duplicated().sum()
            )
        }

    # =========================================================
    # MISSING VALUES
    # =========================================================

    def detect_missing_values(self):

        numeric_columns = (
            self.get_numeric_business_columns()
        )

        for column in self.df.columns:

            missing_count = int(
                self.df[column].isna().sum()
            )

            if missing_count == 0:
                continue

            if column in numeric_columns:

                risk = "HIGH"
                approval = True

                evidence = (
                    f"{missing_count} missing values detected "
                    f"in business/numeric column."
                )

            else:

                risk = "MEDIUM"
                approval = True

                evidence = (
                    f"{missing_count} missing values detected."
                )

            self.add_issue(
                issue_id=f"MISSING_{column}",
                issue_type="missing_values",
                column=column,
                affected_rows=missing_count,
                evidence=evidence,
                risk_level=risk,
                requires_approval=approval
            )

    # =========================================================
    # EXACT DUPLICATES
    # =========================================================

    def detect_exact_duplicates(self):

        duplicate_count = int(
            self.df.duplicated().sum()
        )

        if duplicate_count == 0:
            return

        self.add_issue(
            issue_id="EXACT_DUPLICATES",
            issue_type="exact_duplicate",
            column="ALL_COLUMNS",
            affected_rows=duplicate_count,
            evidence=(
                f"{duplicate_count} rows are exact duplicates "
                f"across all columns."
            ),
            risk_level="LOW",
            requires_approval=False
        )

    # =========================================================
    # DUPLICATE IDENTIFIERS
    # =========================================================

    def detect_duplicate_identifiers(self):

        order_id_column = self.get_semantic_column(
            "order_id"
        )

        identifier_columns = []

        # Validate mapped order ID
        if (
            order_id_column
            and order_id_column in self.df.columns
        ):
            identifier_columns.append(order_id_column)

        # Fallback
        if not identifier_columns:

            for column in self.df.columns:

                name = column.lower().strip()

                if (
                    name == "order id"
                    or name.endswith("order id")
                    or name == "transaction id"
                ):
                    identifier_columns.append(column)

        for column in identifier_columns:

            duplicate_mask = self.df[column].duplicated(
                keep=False
            )

            duplicate_count = int(
                duplicate_mask.sum()
            )

            if duplicate_count == 0:
                continue

            self.add_issue(
                issue_id=(
                    f"DUPLICATE_IDENTIFIER_{column}"
                ),
                issue_type="duplicate_identifier",
                column=column,
                affected_rows=duplicate_count,
                evidence=(
                    f"{duplicate_count} rows contain repeated "
                    f"values in identifier column '{column}'. "
                    f"Repeated identifiers may represent "
                    f"legitimate line items."
                ),
                risk_level="HIGH",
                requires_approval=True,
                warning=(
                    "Do not automatically delete repeated "
                    "identifiers. Multiple line items can "
                    "legitimately share one order ID."
                )
            )

    # =========================================================
    # NUMERIC CONVERSION
    # =========================================================

    def detect_numeric_conversion_issues(self):

        numeric_candidates = (
            self.get_numeric_business_columns()
        )

        for column in numeric_candidates:

            series = self.df[column]

            # Already numeric
            if pd.api.types.is_numeric_dtype(series):
                continue

            converted = pd.to_numeric(
                series,
                errors="coerce"
            )

            invalid_mask = (
                series.notna()
                & converted.isna()
            )

            invalid_count = int(
                invalid_mask.sum()
            )

            if invalid_count == 0:
                continue

            invalid_examples = (
                series[invalid_mask]
                .astype(str)
                .drop_duplicates()
                .head(10)
                .tolist()
            )

            valid_values = converted.dropna()

            median_value = None

            if len(valid_values) > 0:
                median_value = float(
                    valid_values.median()
                )

            self.add_issue(
                issue_id=(
                    f"NUMERIC_CONVERSION_{column}"
                ),
                issue_type="numeric_conversion",
                column=column,
                affected_rows=invalid_count,
                evidence=(
                    f"{invalid_count} non-empty values cannot "
                    f"be converted to numeric."
                ),
                risk_level="HIGH",
                requires_approval=True,
                invalid_examples=invalid_examples,
                computed_median=median_value
            )

    # =========================================================
    # DATE ISSUES
    # =========================================================

    def detect_date_issues(self):

        date_column = self.get_semantic_column("date")

        if (
            date_column
            and date_column in self.df.columns
        ):
            date_columns = [date_column]

        else:

            date_columns = []

            for column in self.df.columns:

                name = column.lower().strip()

                if (
                    "date" in name
                    or "time" in name
                    or "timestamp" in name
                ):
                    date_columns.append(column)

        for column in date_columns:

            series = self.df[column]

            if pd.api.types.is_datetime64_any_dtype(
                series
            ):
                continue

            # DD/MM/YYYY support
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
                continue

            invalid_examples = (
                series[invalid_mask]
                .astype(str)
                .drop_duplicates()
                .head(10)
                .tolist()
            )

            self.add_issue(
                issue_id=f"DATE_CONVERSION_{column}",
                issue_type="invalid_dates",
                column=column,
                affected_rows=invalid_count,
                evidence=(
                    f"{invalid_count} non-empty values cannot "
                    f"be parsed as dates."
                ),
                risk_level="MEDIUM",
                requires_approval=True,
                invalid_examples=invalid_examples,
                parsing_strategy="dayfirst=True"
            )

    # =========================================================
    # NEGATIVE VALUES
    # =========================================================

    def detect_negative_values(self):

        numeric_columns = (
            self.get_numeric_business_columns()
        )

        for column in numeric_columns:

            series = self.df[column]

            if not pd.api.types.is_numeric_dtype(
                series
            ):
                continue

            negative_mask = series < 0

            negative_count = int(
                negative_mask.sum()
            )

            if negative_count == 0:
                continue

            self.add_issue(
                issue_id=f"NEGATIVE_{column}",
                issue_type="negative_value",
                column=column,
                affected_rows=negative_count,
                evidence=(
                    f"{negative_count} negative values detected "
                    f"in business measure '{column}'."
                ),
                risk_level="HIGH",
                requires_approval=True,
                warning=(
                    "Negative values may represent refunds, "
                    "returns or legitimate business events."
                )
            )

    # =========================================================
    # OUTLIERS
    # =========================================================

    def detect_outliers(self):

        numeric_columns = (
            self.get_numeric_business_columns()
        )

        for column in numeric_columns:

            series = self.df[column]

            if not pd.api.types.is_numeric_dtype(
                series
            ):
                continue

            clean_series = series.dropna()

            if len(clean_series) < 4:
                continue

            q1 = clean_series.quantile(0.25)
            q3 = clean_series.quantile(0.75)

            iqr = q3 - q1

            if iqr == 0:
                continue

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_mask = (
                (series < lower_bound)
                | (series > upper_bound)
            )

            outlier_count = int(
                outlier_mask.sum()
            )

            if outlier_count == 0:
                continue

            self.add_issue(
                issue_id=f"OUTLIER_{column}",
                issue_type="statistical_outlier",
                column=column,
                affected_rows=outlier_count,
                evidence=(
                    f"{outlier_count} potential statistical "
                    f"outliers detected using IQR."
                ),
                risk_level="HIGH",
                requires_approval=True,
                lower_bound=float(lower_bound),
                upper_bound=float(upper_bound),
                warning=(
                    "An outlier is not automatically an error. "
                    "Do not delete without business justification."
                )
            )

    # =========================================================
    # CALCULATION MISMATCHES
    # =========================================================

    def detect_calculation_mismatches(self):
        """Detect rows where quantity × unit price differs
        from the recorded total."""

        def find_column(aliases):
            # Match column names without case or spacing differences.
            normalized = {
                str(column).strip().lower().replace("_", " "): column
                for column in self.df.columns
            }

            for alias in aliases:
                key = alias.strip().lower().replace("_", " ")
                if key in normalized:
                    return normalized[key]

            return None

        quantity_column = (
            self.get_semantic_column("quantity")
            or find_column(["Quantity", "Qty", "Units Sold"])
        )

        price_column = (
            self.get_semantic_column("price")
            or find_column([
                "Price per Unit",
                "Unit Price",
                "Price Per Item"
            ])
        )

        if (
            quantity_column not in self.df.columns
            or price_column not in self.df.columns
        ):
            return

        # These totals are checked independently.
        total_columns = []

        for alias in [
            "Total Amount",
            "Total Price"
        ]:
            column = find_column([alias])
            if column and column not in total_columns:
                total_columns.append(column)

        if not total_columns:
            return

        quantity = pd.to_numeric(
            self.df[quantity_column], errors="coerce"
        )
        unit_price = pd.to_numeric(
            self.df[price_column], errors="coerce"
        )

        expected_total = quantity * unit_price

        for total_column in total_columns:
            actual_total = pd.to_numeric(
                self.df[total_column], errors="coerce"
            )

            # Only compare rows where all three values are available.
            valid = (
                quantity.notna()
                & unit_price.notna()
                & actual_total.notna()
                & (quantity >= 0)
                & (unit_price >= 0)
            )

            mismatch = valid & (
                (actual_total - expected_total).abs() > 0.01
            )

            affected_count = int(mismatch.sum())

            if affected_count == 0:
                continue

            example_rows = self.df.index[mismatch].tolist()[:10]

            self.add_issue(
                issue_id=f"CALCULATION_MISMATCH_{total_column}",
                issue_type="calculation_mismatch",
                column=total_column,
                affected_rows=affected_count,
                evidence=(
                    f"{affected_count} rows in '{total_column}' "
                    f"do not match quantity × unit price."
                ),
                risk_level="HIGH",
                requires_approval=True,
                quantity_column=quantity_column,
                unit_price_column=price_column,
                target_column=total_column,
                expected_total_column=total_column,
                example_row_indices=example_rows
            )

    # =========================================================
    # RUN ALL DETECTIONS
    # =========================================================

    def _find_column_by_alias(
        self,
        semantic_role: str,
        aliases: List[str],
    ) -> Optional[str]:
        """Resolve a column using Planner mapping, then aliases."""

        mapped = self.get_semantic_column(semantic_role)

        if mapped in self.df.columns:
            return mapped

        normalise = lambda value: (
            str(value).strip().lower().replace("_", " ")
        )

        lookup = {
            normalise(column): column
            for column in self.df.columns
        }

        for alias in aliases:
            match = lookup.get(normalise(alias))
            if match is not None:
                return match

        return None

    def detect_calculation_mismatches(self):
        """Detect totals inconsistent with quantity × unit price."""

        quantity_col = self._find_column_by_alias(
            "quantity",
            ["Quantity", "Qty", "Units Sold"],
        )

        price_col = self._find_column_by_alias(
            "price",
            [
                "Price per Unit",
                "Unit Price",
                "Unit_Price",
                "Price Per Item",
            ],
        )

        if not quantity_col or not price_col:
            return

        quantity = pd.to_numeric(
            self.df[quantity_col], errors="coerce"
        )
        unit_price = pd.to_numeric(
            self.df[price_col], errors="coerce"
        )

        expected = quantity * unit_price
        valid_inputs = (
            quantity.notna()
            & unit_price.notna()
            & quantity.ge(0)
            & unit_price.ge(0)
        )

        # Check each calculated-total column independently.
        target_aliases = [
            "Total Amount",
            "Total_Amount",
            "Total Price",
            "Total_Price",
        ]

        for target in target_aliases:
            target_col = self._find_column_by_alias(
                target, [target]
            )

            if target_col is None:
                continue

            actual = pd.to_numeric(
                self.df[target_col], errors="coerce"
            )

            mismatch = (
                valid_inputs
                & actual.notna()
                & ((actual - expected).abs() > 0.01)
            )

            count = int(mismatch.sum())

            if count == 0:
                continue

            examples = []
            for index in self.df.index[mismatch][:10]:
                examples.append({
                    "row_index": int(index),
                    "actual": float(actual.loc[index]),
                    "expected": round(float(expected.loc[index]), 2),
                })

            self.add_issue(
                issue_id=f"CALCULATION_MISMATCH_{target_col}",
                issue_type="calculation_mismatch",
                column=target_col,
                affected_rows=count,
                evidence=(
                    f"{count} rows in '{target_col}' do not match "
                    f"{quantity_col} × {price_col}."
                ),
                risk_level="HIGH",
                requires_approval=True,
                quantity_column=quantity_col,
                unit_price_column=price_col,
                target_column=target_col,
                expected_formula=(
                    f"{quantity_col} * {price_col}"
                ),
                examples=examples,
            )




    def detect_all(self):

        self.issues = []

        self.detect_missing_values()
        self.detect_exact_duplicates()
        self.detect_duplicate_identifiers()
        self.detect_numeric_conversion_issues()
        self.detect_date_issues()
        self.detect_negative_values()
        self.detect_outliers()

        # New calculation consistency check
        self.detect_calculation_mismatches()

        return self.issues


# =============================================================
# CONVENIENCE FUNCTION
# =============================================================

def detect_data_quality(
    df: pd.DataFrame,
    semantic_mapping: Optional[Dict] = None
):

    detector = DataQualityDetector(
        df=df,
        semantic_mapping=semantic_mapping
    )

    quality = detector.detect_basic_quality()

    issues = detector.detect_all()

    return {
        "quality": quality,
        "issues": issues
    }