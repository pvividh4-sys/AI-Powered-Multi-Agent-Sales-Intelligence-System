from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class CleaningDecision:
    """
    Structured cleaning decision.

    This class describes what should happen.
    It does NOT modify the DataFrame.
    """

    issue_id: str
    issue_type: str
    column: str

    affected_rows: int

    evidence: str
    detected_by: str

    llm_reasoning: str

    recommended_action: str
    alternative_actions: List[str]

    confidence: float
    risk_level: str

    requires_approval: bool

    user_decision: Optional[str] = None
    execution_result: Optional[str] = None
    validation_result: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert decision object into dictionary.
        """
        return asdict(self)


class CleaningDecisionEngine:
    """
    Converts detected data-quality issues into
    structured cleaning decisions.

    IMPORTANT:
    This class does not modify the DataFrame.
    """

    def __init__(self):
        pass

    # =========================================================
    # CREATE SINGLE DECISION
    # =========================================================

    def create_decision(
        self,
        issue: Dict[str, Any]
    ) -> CleaningDecision:

        issue_id = issue.get(
            "issue_id",
            "UNKNOWN"
        )

        issue_type = issue.get(
            "issue_type",
            ""
        )

        column = issue.get(
            "column",
            ""
        )

        affected_rows = issue.get(
            "affected_rows",
            0
        )

        evidence = issue.get(
            "evidence",
            ""
        )

        detected_by = issue.get(
            "detected_by",
            "Python"
        )


        # =====================================================
        # EXACT DUPLICATES
        # =====================================================

        if issue_type == "exact_duplicate":

            return CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "Rows are exact duplicates across all "
                    "available columns. Removing exact "
                    "duplicates is generally a low-risk "
                    "data-quality operation."
                ),
                recommended_action=(
                    "Remove exact duplicate rows"
                ),
                alternative_actions=[
                    "Keep duplicates",
                    "Review duplicate rows before removal"
                ],
                confidence=0.98,
                risk_level="LOW",
                requires_approval=False
            )

        # =====================================================
        # DUPLICATE IDENTIFIER
        # =====================================================

        if issue_type == "duplicate_identifier":

            return CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "Repeated identifiers do not necessarily "
                    "represent duplicate transactions. Retail "
                    "datasets may contain multiple legitimate "
                    "line items associated with the same order."
                ),
                recommended_action=(
                    "Review repeated identifiers before "
                    "removing any rows"
                ),
                alternative_actions=[
                    "Keep repeated identifiers",
                    "Group records by identifier",
                    "Remove only confirmed duplicate transactions"
                ],
                confidence=0.95,
                risk_level="HIGH",
                requires_approval=True
            )

        # =====================================================
        # MISSING VALUES
        # =====================================================

        if issue_type == "missing_values":

            numeric_keywords = [
                "sales",
                "revenue",
                "amount",
                "price",
                "quantity",
                "profit",
                "cost"
            ]

            column_lower = column.lower()

            is_numeric_business_column = any(
                keyword in column_lower
                for keyword in numeric_keywords
            )

            if is_numeric_business_column:

                return CleaningDecision(
                    issue_id=issue_id,
                    issue_type=issue_type,
                    column=column,
                    affected_rows=affected_rows,
                    evidence=evidence,
                    detected_by=detected_by,
                    llm_reasoning=(
                        "Missing values occur in a business "
                        "numeric measure. Automatically "
                        "imputing these values could change "
                        "KPIs, trends and forecasting results."
                    ),
                    recommended_action=(
                        "Review missing business values "
                        "before imputation"
                    ),
                    alternative_actions=[
                        "Keep missing values",
                        "Impute using median",
                        "Impute using business-specific logic",
                        "Remove affected rows"
                    ],
                    confidence=0.92,
                    risk_level="HIGH",
                    requires_approval=True
                )

            return CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "Missing categorical values can often be "
                    "handled using an explicit category such "
                    "as 'Unknown'."
                ),
                recommended_action=(
                    "Fill missing categorical values with 'Unknown'"
                ),
                alternative_actions=[
                    "Keep missing values",
                    "Remove affected rows",
                    "Use the most frequent category"
                ],
                confidence=0.88,
                risk_level="MEDIUM",
                requires_approval=True
            )

        # =====================================================
        # NUMERIC CONVERSION
        # =====================================================

        if issue_type == "numeric_conversion":

            return CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "Values in a column expected to contain "
                    "numeric data cannot be converted directly. "
                    "Invalid values should be reviewed before "
                    "replacement."
                ),
                recommended_action=(
                    "Convert valid numeric values and review "
                    "invalid values"
                ),
                alternative_actions=[
                    "Replace invalid values with median",
                    "Keep invalid values",
                    "Remove affected rows"
                ],
                confidence=0.90,
                risk_level="HIGH",
                requires_approval=True
            )

        # =====================================================
        # INVALID DATES
        # =====================================================

        if issue_type == "invalid_dates":

            return CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "Date values cannot be reliably parsed "
                    "using the current parsing strategy. "
                    "Date normalization should not silently "
                    "discard records."
                ),
                recommended_action=(
                    "Normalize date format and review "
                    "invalid date values"
                ),
                alternative_actions=[
                    "Keep original date values",
                    "Convert using inferred date format",
                    "Remove confirmed invalid-date rows"
                ],
                confidence=0.90,
                risk_level="MEDIUM",
                requires_approval=True
            )

        # =====================================================
        # NEGATIVE VALUES
        # =====================================================

        if issue_type == "negative_value":

            return CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "Negative values may represent refunds, "
                    "returns or legitimate business events. "
                    "They should not be removed automatically."
                ),
                recommended_action=(
                    "Review negative values using business context"
                ),
                alternative_actions=[
                    "Keep negative values",
                    "Convert to absolute values",
                    "Remove confirmed erroneous records"
                ],
                confidence=0.85,
                risk_level="HIGH",
                requires_approval=True
            )

        # =====================================================
        # STATISTICAL OUTLIERS
        # =====================================================

        if issue_type == "statistical_outlier":

            decision = CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "Statistical outliers are observations "
                    "outside the expected statistical range. "
                    "An outlier is not automatically an error "
                    "and may represent legitimate high-value "
                    "sales or unusual transactions."
                ),
                recommended_action=(
                    "Review outliers; do not delete automatically"
                ),
                alternative_actions=[
                    "Keep outliers",
                    "Investigate outlier transactions",
                    "Remove confirmed erroneous records",
                    "Apply a business-approved treatment"
                ],
                confidence=0.93,
                risk_level="HIGH",
                requires_approval=True
            )

            # Preserve IQR boundaries from detector
            decision_dict = decision.to_dict()

            if "lower_bound" in issue:
                decision_dict["lower_bound"] = issue[
                    "lower_bound"
                ]

            if "upper_bound" in issue:
                decision_dict["upper_bound"] = issue[
                    "upper_bound"
                ]

            return decision_from_dict(
                decision_dict
            )



        if issue_type == "calculation_mismatch":
            return CleaningDecision(
                issue_id=issue_id,
                issue_type=issue_type,
                column=column,
                affected_rows=affected_rows,
                evidence=evidence,
                detected_by=detected_by,
                llm_reasoning=(
                    "The calculated total differs from the "
                    "expected quantity multiplied by unit price. "
                    "Recalculate only after user approval."
                ),
                recommended_action=(
                    "Recalculate the incorrect total using "
                    "quantity multiplied by unit price"
                ),
                alternative_actions=[
                    "Approve recalculation",
                    "Keep the original value",
                    "Review the affected records manually",
                ],
                confidence=0.99,
                risk_level="HIGH",
                requires_approval=True,
                details={
                    "quantity_column": issue.get("quantity_column"),
                    "unit_price_column": issue.get("unit_price_column"),
                    "target_column": issue.get("target_column"),
                },
            )

        # =====================================================
        # UNKNOWN ISSUE TYPE
        # =====================================================

        return CleaningDecision(
            issue_id=issue_id,
            issue_type=issue_type,
            column=column,
            affected_rows=affected_rows,
            evidence=evidence,
            detected_by=detected_by,
            llm_reasoning=(
                "The detected issue type does not have "
                "a predefined cleaning policy."
            ),
            recommended_action="Review issue manually",
            alternative_actions=[
                "Keep original data"
            ],
            confidence=0.50,
            risk_level="HIGH",
            requires_approval=True
        )

    # =========================================================
    # CREATE ALL DECISIONS
    # =========================================================

    def create_decisions(
        self,
        issues: List[Dict[str, Any]]
    ) -> List[CleaningDecision]:

        decisions = []

        for issue in issues:

            decision = self.create_decision(
                issue
            )

            decisions.append(
                decision
            )

        return decisions


# =============================================================
# HELPER
# =============================================================

def decision_from_dict(
    data: Dict[str, Any]
) -> CleaningDecision:
    """
    Rebuild CleaningDecision from a dictionary while
    preserving additional execution metadata separately.

    The execution engine receives dictionaries, so this helper
    allows detector-specific values such as IQR boundaries
    to be retained.
    """

    standard_fields = {
        "issue_id",
        "issue_type",
        "column",
        "affected_rows",
        "evidence",
        "detected_by",
        "llm_reasoning",
        "recommended_action",
        "alternative_actions",
        "confidence",
        "risk_level",
        "requires_approval",
        "user_decision",
        "execution_result",
        "validation_result"
    }

    filtered = {
        key: value
        for key, value in data.items()
        if key in standard_fields
    }

    return CleaningDecision(
        **filtered
    )


# =============================================================
# CONVENIENCE FUNCTION
# =============================================================

def generate_cleaning_decisions(
    issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    engine = CleaningDecisionEngine()

    decisions = engine.create_decisions(
        issues
    )

    result = []

    for decision in decisions:

        result.append(
            decision.to_dict()
        )

    return result