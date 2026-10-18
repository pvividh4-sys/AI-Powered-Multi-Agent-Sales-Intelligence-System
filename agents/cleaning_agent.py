"""
Data Cleaning Agent

Coordinates the complete cleaning workflow:

Detection
    ↓
Decision
    ↓
Approval
    ↓
Execution
    ↓
Validation
    ↓
Logging
"""

from typing import Optional, Dict, Any, List
import pandas as pd

from cleaning.detection import DataQualityDetector
from cleaning.decisions import CleaningDecisionEngine
from cleaning.execution import CleaningExecutionEngine
from cleaning.validation import CleaningValidationEngine


class CleaningAgent:
    """
    Main coordinator for the Data Cleaning workflow.
    """

    AGENT_NAME = "Data Cleaning Agent"

    def __init__(
        self,
        df: pd.DataFrame,
        semantic_mapping: Optional[Dict[str, Any]] = None
    ):

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "df must be a pandas DataFrame."
            )

        if df.empty:
            raise ValueError(
                "Cleaning Agent cannot process an empty dataset."
            )

        self.original_df = df.copy()

        self.semantic_mapping = (
            semantic_mapping or {}
        )

        self.cleaned_df = df.copy()

        self.detected_issues: List[Any] = []
        self.cleaning_decisions: List[Any] = []
        self.execution_logs: List[Dict[str, Any]] = []

        self.validation_result: Dict[str, Any] = {}

        self.status = "initialized"

        self.detector = None
        self.decision_engine = None
        self.execution_engine = None
        self.validation_engine = None

    # ============================================================
    # HELPER
    # ============================================================

    @staticmethod
    def _get_value(
        obj: Any,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get a value from either a dictionary or an object.

        Supports CleaningDecision dataclass objects.
        """

        if isinstance(obj, dict):
            return obj.get(key, default)

        return getattr(
            obj,
            key,
            default
        )

    @staticmethod
    def _set_value(
        obj: Any,
        key: str,
        value: Any
    ) -> None:
        """
        Set a value on either a dictionary or an object.
        """

        if isinstance(obj, dict):
            obj[key] = value

        else:
            setattr(
                obj,
                key,
                value
            )

    # ============================================================
    # 1. DETECTION
    # ============================================================

    def detect(self) -> List[Any]:
        """
        Detect data quality issues.

        This stage does not modify the dataset.
        """

        self.detector = DataQualityDetector(
            self.original_df,
            semantic_mapping=self.semantic_mapping
        )

        self.detected_issues = (
            self.detector.detect_all()
        )

        self.status = "issues_detected"

        return self.detected_issues

    # ============================================================
    # 2. DECISION GENERATION
    # ============================================================

    def create_decisions(self) -> List[Any]:
        """
        Convert detected issues into structured
        cleaning decisions.
        """

        if self.detector is None:
            self.detect()

        self.decision_engine = (
            CleaningDecisionEngine()
        )

        self.cleaning_decisions = (
            self.decision_engine.create_decisions(
                self.detected_issues
            )
        )

        self.status = "decisions_created"

        return self.cleaning_decisions

    # ============================================================
    # 3. APPROVAL
    # ============================================================

    def apply_approval(
        self,
        approvals: Optional[Dict[str, str]] = None
    ) -> List[Any]:
        """
        Apply approval decisions.

        Example:

        approvals = {
            "OUTLIER_Total Amount": "APPROVE",
            "OUTLIER_Quantity": "SKIP"
        }

        HIGH-risk decisions require explicit approval.
        """

        if self.decision_engine is None:
            self.create_decisions()

        approvals = approvals or {}

        for decision in self.cleaning_decisions:

            issue_id = self._get_value(
                decision,
                "issue_id"
            )

            requires_approval = self._get_value(
                decision,
                "requires_approval",
                False
            )

            # ----------------------------------------------------
            # Explicit approval supplied
            # ----------------------------------------------------

            if issue_id in approvals:

                user_decision = str(
                    approvals[issue_id]
                ).strip().upper()

                if user_decision not in {
                    "APPROVE",
                    "SKIP"
                }:
                    user_decision = "SKIP"

                self._set_value(
                    decision,
                    "user_decision",
                    user_decision
                )

            # ----------------------------------------------------
            # Approval required but not supplied
            # ----------------------------------------------------

            elif requires_approval:

                self._set_value(
                    decision,
                    "user_decision",
                    "SKIP"
                )

            # ----------------------------------------------------
            # Low-risk decision
            # ----------------------------------------------------

            else:

                current_decision = self._get_value(
                    decision,
                    "user_decision"
                )

                if not current_decision:

                    self._set_value(
                        decision,
                        "user_decision",
                        "APPROVE"
                    )

        self.status = "approval_processed"

        return self.cleaning_decisions

    # ============================================================
    # 4. EXECUTION
    # ============================================================

    def execute(
        self,
        approvals: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Execute approved cleaning decisions.

        High-risk operations cannot be executed without
        explicit approval.
        """

        if self.decision_engine is None:
            self.create_decisions()

        self.apply_approval(
            approvals=approvals
        )

        self.execution_engine = (
            CleaningExecutionEngine(
                self.original_df
            )
        )

        self.cleaned_df = (
            self.execution_engine.execute_decisions(
                self.cleaning_decisions
            )
        )

        self.execution_logs = (
            self.execution_engine.get_execution_logs()
        )

        self.status = "executed"

        return self.cleaned_df

    # ============================================================
    # 5. VALIDATION
    # ============================================================

    def validate(self) -> Dict[str, Any]:
        """
        Validate the cleaned dataset.

        Uses CleaningValidationEngine.validate_all()
        because that is the public validation method.
        """

        self.validation_engine = (
            CleaningValidationEngine(
                original_df=self.original_df,
                cleaned_df=self.cleaned_df,
                execution_logs=self.execution_logs,
                semantic_mapping=self.semantic_mapping
            )
        )

        # --------------------------------------------------------
        # Get date column from Planner mapping
        # --------------------------------------------------------

        date_column = None

        date_mapping = self.semantic_mapping.get(
            "date"
        )

        if isinstance(date_mapping, dict):

            date_column = date_mapping.get(
                "column"
            )

        elif isinstance(date_mapping, str):

            date_column = date_mapping

        # --------------------------------------------------------
        # Run complete validation
        # --------------------------------------------------------

        self.validation_result = (
            self.validation_engine.validate_all(
                date_column=date_column
            )
        )

        # --------------------------------------------------------
        # Update agent status
        # --------------------------------------------------------

        overall_status = (
            self.validation_result.get(
                "overall_status"
            )
        )

        if overall_status == "PASSED":

            self.status = "validated"

        elif overall_status == "WARNING":

            self.status = "validated_with_warnings"

        else:

            self.status = "validation_failed"

        return self.validation_result

    # ============================================================
    # 6. COMPLETE WORKFLOW
    # ============================================================

    def run(
        self,
        approvals: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete Data Cleaning Agent workflow.

        Detection
            ↓
        Decision
            ↓
        Approval
            ↓
        Execution
            ↓
        Validation
        """

        # Step 1
        self.detect()

        # Step 2
        self.create_decisions()

        # Step 3 + 4
        self.execute(
            approvals=approvals
        )

        # Step 5
        self.validate()

        return self.get_result()

    # ============================================================
    # 7. RESULT
    # ============================================================

    def get_result(self) -> Dict[str, Any]:
        """
        Return complete structured agent state.
        """

        return {
            "agent": self.AGENT_NAME,

            "status": self.status,

            "original_rows": len(
                self.original_df
            ),

            "cleaned_rows": len(
                self.cleaned_df
            ),

            "original_columns": len(
                self.original_df.columns
            ),

            "cleaned_columns": len(
                self.cleaned_df.columns
            ),

            "detected_issues": (
                self.detected_issues
            ),

            "cleaning_decisions": (
                self.cleaning_decisions
            ),

            "execution_logs": (
                self.execution_logs
            ),

            "validation": (
                self.validation_result
            ),

            "cleaned_df": (
                self.cleaned_df
            )
        }

    # ============================================================
    # 8. ACCESS METHODS
    # ============================================================

    def get_detected_issues(self) -> List[Any]:

        return self.detected_issues

    def get_cleaning_decisions(self) -> List[Any]:

        return self.cleaning_decisions

    def get_execution_logs(self) -> List[Dict[str, Any]]:

        return self.execution_logs

    def get_validation_result(self) -> Dict[str, Any]:

        return self.validation_result

    def get_cleaned_data(self) -> pd.DataFrame:

        return self.cleaned_df.copy()