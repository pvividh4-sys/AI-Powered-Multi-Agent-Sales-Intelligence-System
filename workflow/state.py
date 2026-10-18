"""
Shared workflow state.

The workflow state is the communication layer between the eight
specialised agents.

Agent names are intentionally fixed to the project's architecture:

1. Planner Agent
2. Data Cleaning Agent
3. EDA Agent
4. Visualization Agent
5. Forecasting Agent
6. Insight Agent
7. Recommendation Agent
8. Report Agent
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd


# ====================================================================
# FIXED AGENT ARCHITECTURE
# ====================================================================

AGENT_NAMES = [
    "Planner Agent",
    "Data Cleaning Agent",
    "EDA Agent",
    "Visualization Agent",
    "Forecasting Agent",
    "Insight Agent",
    "Recommendation Agent",
    "Report Agent",
]


# ====================================================================
# WORKFLOW STATE
# ====================================================================

@dataclass
class WorkflowState:
    """Shared state passed between workflow stages."""

    # ================================================================
    # DATA
    # ================================================================

    df: Optional[pd.DataFrame] = None

    # ================================================================
    # PLANNER
    # ================================================================

    planner_result: Optional[Dict[str, Any]] = None

    semantic_mapping: Dict[str, Any] = field(
        default_factory=dict
    )

    capabilities: Dict[str, Any] = field(
        default_factory=dict
    )

    execution_plan: List[Any] = field(
        default_factory=list
    )

    planner_status: Optional[str] = None

    # ================================================================
    # CLEANING
    # ================================================================

    cleaned_df: Optional[pd.DataFrame] = None

    cleaning_result: Optional[Dict[str, Any]] = None

    cleaning_validation: Optional[Dict[str, Any]] = None

    cleaning_status: Optional[str] = None

    cleaning_decision: Optional[str] = None

    # ================================================================
    # EDA
    # ================================================================

    eda_result: Optional[Dict[str, Any]] = None

    eda_validation: Optional[Dict[str, Any]] = None

    eda_status: Optional[str] = None

    eda_decision: Optional[str] = None

    # ================================================================
    # VISUALIZATION
    # ================================================================

    visualization_result: Optional[Dict[str, Any]] = None

    visualization_validation: Optional[Dict[str, Any]] = None

    visualization_status: Optional[str] = None

    visualization_decision: Optional[str] = None

    # ================================================================
    # FORECASTING
    # ================================================================

    forecasting_result: Optional[Dict[str, Any]] = None

    forecasting_status: Optional[str] = None

    forecasting_decision: Optional[str] = None

    # ================================================================
    # INSIGHT
    # ================================================================

    insight_result: Optional[Dict[str, Any]] = None

    insight_validation: Optional[Dict[str, Any]] = None

    insight_status: Optional[str] = None

    insight_decision: Optional[str] = None

    # ================================================================
    # RECOMMENDATION
    # ================================================================

    recommendation_result: Optional[Dict[str, Any]] = None

    recommendation_validation: Optional[Dict[str, Any]] = None

    recommendation_status: Optional[str] = None

    recommendation_decision: Optional[str] = None

    # ================================================================
    # REPORT
    # ================================================================

    report_result: Optional[Dict[str, Any]] = None

    report_validation: Optional[Dict[str, Any]] = None

    report_status: Optional[str] = None

    report_decision: Optional[str] = None

    # ================================================================
    # WORKFLOW CONTROL
    # ================================================================

    current_stage: str = "initialisation"

    workflow_status: str = "initialised"

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    # ================================================================
    # AGENT STATUS
    # ================================================================

    agent_status: Dict[str, str] = field(
        default_factory=lambda: {
            agent: "pending"
            for agent in AGENT_NAMES
        }
    )

    # ================================================================
    # DECISION TRACE
    # ================================================================

    decision_trace: List[Dict[str, Any]] = field(
        default_factory=list
    )

    # ================================================================
    # ERROR / WARNING HELPERS
    # ================================================================

    def add_error(
        self,
        message: str,
    ) -> None:
        """Add a workflow error."""

        self.errors.append(
            str(message)
        )

    def add_warning(
        self,
        message: str,
    ) -> None:
        """Add a workflow warning."""

        self.warnings.append(
            str(message)
        )

    # ================================================================
    # DECISION TRACE
    # ================================================================

    def add_decision(
        self,
        decision: str,
        reason: str,
        evidence: Any,
        action: str,
        result: Any,
        validation_status: str,
    ) -> None:
        """
        Add a structured workflow decision trace entry.

        This method is retained for compatibility with the
        earlier workflow implementation.
        """

        self.decision_trace.append(
            {
                "decision": decision,
                "reason": reason,
                "evidence": evidence,
                "action": action,
                "result": result,
                "validation_status": validation_status,
            }
        )

    # ================================================================
    # AGENT-AWARE DECISION TRACE
    # ================================================================

    def add_decision_trace(
        self,
        agent: str,
        decision: str,
        reason: str,
        evidence: Any,
        action: str,
        result: Any,
        validation_status: str,
    ) -> None:
        """
        Add an agent-aware structured decision trace entry.

        This is used by workflow routing and agent execution
        nodes to maintain a complete decision trace.
        """

        self.decision_trace.append(
            {
                "agent": agent,
                "decision": decision,
                "reason": reason,
                "evidence": evidence,
                "action": action,
                "result": result,
                "validation_status": validation_status,
            }
        )

    # ================================================================
    # AGENT STATUS
    # ================================================================

    def set_agent_status(
        self,
        agent_name: str,
        status: str,
    ) -> None:
        """
        Update an agent's workflow status.
        """

        if agent_name not in AGENT_NAMES:
            raise ValueError(
                f"Unknown agent name: {agent_name}"
            )

        self.agent_status[
            agent_name
        ] = str(status)

    # ================================================================
    # ANALYSIS DATA
    # ================================================================

    def get_analysis_df(
        self,
    ) -> Optional[pd.DataFrame]:
        """
        Return the latest available analysis DataFrame.

        Cleaned data takes precedence over the original dataset.
        """

        if self.cleaned_df is not None:
            return self.cleaned_df

        return self.df

    # ================================================================
    # SERIALIZATION
    # ================================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize workflow state.

        DataFrames are represented by metadata rather than embedding
        the complete DataFrame into the workflow state dictionary.
        """

        data = asdict(self)

        # ------------------------------------------------------------
        # Original DataFrame
        # ------------------------------------------------------------

        if self.df is not None:
            data["df"] = {
                "rows": int(
                    self.df.shape[0]
                ),
                "columns": int(
                    self.df.shape[1]
                ),
            }

        # ------------------------------------------------------------
        # Cleaned DataFrame
        # ------------------------------------------------------------

        if self.cleaned_df is not None:
            data["cleaned_df"] = {
                "rows": int(
                    self.cleaned_df.shape[0]
                ),
                "columns": int(
                    self.cleaned_df.shape[1]
                ),
            }

        return data


# ====================================================================
# STATE FACTORY
# ====================================================================

def create_initial_state(
    df: pd.DataFrame,
) -> WorkflowState:
    """
    Create the initial workflow state.
    """

    if df is None:
        raise ValueError(
            "df cannot be None."
        )

    if not isinstance(
        df,
        pd.DataFrame,
    ):
        raise TypeError(
            "df must be a pandas DataFrame."
        )

    state = WorkflowState(
        df=df,
        current_stage="initialisation",
        workflow_status="initialised",
    )

    return state