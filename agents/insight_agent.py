"""
Insight Agent

The Insight Agent converts validated analytical results into
structured, evidence-grounded business insights.

Responsibilities:
    1. Consume validated EDA results.
    2. Consume validated forecasting results when available.
    3. Generate deterministic, evidence-grounded insights.
    4. Validate generated insights.
    5. Prevent unsupported or ungrounded insights.
    6. Store a structured decision trace.
    7. Provide serializable output for shared workflow state.

The agent does NOT:
    - modify the DataFrame
    - perform data cleaning
    - independently alter analytical results
    - invent numerical values
    - make unsupported causal claims
    - use an LLM at this stage

LLM integration will be added later for interpretation and
natural-language synthesis while keeping numerical evidence
grounded in validated analytical results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from analytics.insights import (
    Insight,
    generate_all_insights,
    validate_insights,
)


# =====================================================================
# RESULT STRUCTURE
# =====================================================================

@dataclass
class InsightAgentResult:
    """
    Structured result returned by the Insight Agent.
    """

    status: str
    insights: List[Dict[str, Any]] = field(default_factory=list)

    validation: Dict[str, Any] = field(default_factory=dict)

    total_insights: int = 0

    evidence_sources: List[str] = field(default_factory=list)

    decision_trace: List[Dict[str, Any]] = field(
        default_factory=list
    )

    warnings: List[str] = field(default_factory=list)

    errors: List[str] = field(default_factory=list)

    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent result into a serializable dictionary.
        """

        return {
            "status": self.status,
            "insights": self.insights,
            "validation": self.validation,
            "total_insights": self.total_insights,
            "evidence_sources": self.evidence_sources,
            "decision_trace": self.decision_trace,
            "warnings": self.warnings,
            "errors": self.errors,
            "message": self.message,
        }


# =====================================================================
# INSIGHT AGENT
# =====================================================================

class InsightAgent:
    """
    Insight Agent.

    The agent consumes validated analytical outputs and generates
    evidence-grounded business insights.

    Numerical calculations are performed by deterministic analytical
    modules. The Insight Agent only interprets the already validated
    results.
    """

    AGENT_NAME = "Insight Agent"

    def __init__(
        self,
        minimum_confidence: float = 0.80,
    ) -> None:
        """
        Initialise the Insight Agent.

        Parameters
        ----------
        minimum_confidence:
            Minimum confidence required for an insight to be accepted.
        """

        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError(
                "minimum_confidence must be between 0.0 and 1.0."
            )

        self.minimum_confidence = minimum_confidence

    # -----------------------------------------------------------------
    # Public execution method
    # -----------------------------------------------------------------

    def run(
        self,
        kpi_results: Optional[Dict[str, Any]] = None,
        trend_results: Optional[Dict[str, Any]] = None,
        ranking_results: Optional[Dict[str, Any]] = None,
        forecasting_result: Optional[Dict[str, Any]] = None,
        eda_validation: Optional[Dict[str, Any]] = None,
        forecasting_validation: Optional[Dict[str, Any]] = None,
    ) -> InsightAgentResult:
        """
        Execute the Insight Agent.

        Parameters
        ----------
        kpi_results:
            Validated KPI results from the EDA stage.

        trend_results:
            Validated trend results from the EDA stage.

        ranking_results:
            Validated ranking results from the EDA stage.

        forecasting_result:
            Validated forecasting result. Optional because forecasting
            is conditional.

        eda_validation:
            Validation result produced by the EDA Agent.

        forecasting_validation:
            Validation result produced by the Forecasting Agent.

        Returns
        -------
        InsightAgentResult
            Structured and serializable agent result.
        """

        decision_trace: List[Dict[str, Any]] = []
        warnings: List[str] = []
        errors: List[str] = []

        # -------------------------------------------------------------
        # 1. Determine available evidence
        # -------------------------------------------------------------

        evidence_sources = self._identify_evidence_sources(
            kpi_results=kpi_results,
            trend_results=trend_results,
            ranking_results=ranking_results,
            forecasting_result=forecasting_result,
        )

        decision_trace.append(
            self._trace(
                decision="Identify analytical evidence",
                reason=(
                    "Determine which validated analytical outputs "
                    "are available for grounded insight generation."
                ),
                evidence={
                    "available_sources": evidence_sources,
                },
                action="Inspect analytical result availability.",
                result=(
                    f"{len(evidence_sources)} evidence source(s) "
                    "available."
                ),
                validation_status="PENDING",
            )
        )

        # -------------------------------------------------------------
        # 2. Validate EDA precondition
        # -------------------------------------------------------------

        eda_ok = self._validation_passed(
            eda_validation
        )

        if eda_validation is not None:
            decision_trace.append(
                self._trace(
                    decision="Validate EDA precondition",
                    reason=(
                        "Insights based on EDA results should only be "
                        "generated when the EDA validation has passed."
                    ),
                    evidence={
                        "eda_validation": eda_validation,
                    },
                    action="Check EDA validation status.",
                    result=(
                        "EDA validation PASSED."
                        if eda_ok
                        else "EDA validation did not pass."
                    ),
                    validation_status=(
                        "PASSED"
                        if eda_ok
                        else "FAILED"
                    ),
                )
            )

        # If EDA validation was explicitly supplied and failed,
        # do not generate insights from unvalidated EDA results.
        if eda_validation is not None and not eda_ok:
            errors.append(
                "EDA validation did not pass. "
                "Insight generation was blocked."
            )

            decision_trace.append(
                self._trace(
                    decision="Block insight generation",
                    reason=(
                        "Validated analytical evidence is required "
                        "before generating business insights."
                    ),
                    evidence={
                        "eda_validation": eda_validation,
                    },
                    action="Do not generate insights.",
                    result="Insight generation blocked.",
                    validation_status="FAILED",
                )
            )

            return InsightAgentResult(
                status="failed",
                insights=[],
                validation={
                    "overall_status": "FAILED",
                    "reason": (
                        "EDA validation did not pass."
                    ),
                },
                total_insights=0,
                evidence_sources=evidence_sources,
                decision_trace=decision_trace,
                warnings=warnings,
                errors=errors,
                message=(
                    "Insight generation was blocked because "
                    "EDA validation did not pass."
                ),
            )

        # -------------------------------------------------------------
        # 3. Check analytical evidence
        # -------------------------------------------------------------

        if not evidence_sources:
            warnings.append(
                "No analytical evidence was supplied."
            )

            decision_trace.append(
                self._trace(
                    decision="Check analytical evidence",
                    reason=(
                        "Insights require at least one analytical "
                        "evidence source."
                    ),
                    evidence={},
                    action="Do not generate unsupported insights.",
                    result="No evidence available.",
                    validation_status="FAILED",
                )
            )

            return InsightAgentResult(
                status="not_eligible",
                insights=[],
                validation={
                    "overall_status": "PASSED",
                    "reason": "No analytical evidence available.",
                },
                total_insights=0,
                evidence_sources=[],
                decision_trace=decision_trace,
                warnings=warnings,
                errors=errors,
                message=(
                    "Insight generation skipped because no "
                    "analytical evidence was available."
                ),
            )

        # -------------------------------------------------------------
        # 4. Generate deterministic insights
        # -------------------------------------------------------------

        decision_trace.append(
            self._trace(
                decision="Generate evidence-grounded insights",
                reason=(
                    "Convert validated analytical results into "
                    "structured business insights."
                ),
                evidence={
                    "evidence_sources": evidence_sources,
                },
                action=(
                    "Run deterministic insight-generation "
                    "functions."
                ),
                result="Insight generation executed.",
                validation_status="PENDING",
            )
        )

        try:
            generated_insights = generate_all_insights(
                kpi_results=kpi_results,
                trend_results=trend_results,
                ranking_results=ranking_results,
                forecasting_result=forecasting_result,
            )

        except Exception as exc:
            errors.append(
                f"Insight generation failed: {exc}"
            )

            decision_trace.append(
                self._trace(
                    decision="Generate insights",
                    reason=(
                        "Insight generation encountered an "
                        "execution error."
                    ),
                    evidence={
                        "error": str(exc),
                    },
                    action="Stop insight generation.",
                    result="Generation failed.",
                    validation_status="FAILED",
                )
            )

            return InsightAgentResult(
                status="failed",
                insights=[],
                validation={
                    "overall_status": "FAILED",
                    "reason": str(exc),
                },
                total_insights=0,
                evidence_sources=evidence_sources,
                decision_trace=decision_trace,
                warnings=warnings,
                errors=errors,
                message=(
                    "Insight generation failed."
                ),
            )

        # -------------------------------------------------------------
        # 5. Apply confidence policy
        # -------------------------------------------------------------

        accepted_insights, rejected_insights = (
            self._apply_confidence_policy(
                generated_insights
            )
        )

        if rejected_insights:
            warnings.append(
                f"{len(rejected_insights)} insight(s) were "
                "excluded because their confidence was below "
                f"{self.minimum_confidence:.2f}."
            )

        decision_trace.append(
            self._trace(
                decision="Apply insight confidence policy",
                reason=(
                    "Only insights meeting the configured "
                    "confidence threshold should be retained."
                ),
                evidence={
                    "minimum_confidence": (
                        self.minimum_confidence
                    ),
                    "generated": len(generated_insights),
                    "accepted": len(accepted_insights),
                    "rejected": len(rejected_insights),
                },
                action="Filter low-confidence insights.",
                result=(
                    f"{len(accepted_insights)} insight(s) accepted."
                ),
                validation_status="PASSED",
            )
        )

        # -------------------------------------------------------------
        # 6. Convert insights to dictionaries
        # -------------------------------------------------------------

        serialized_insights = [
            insight.to_dict()
            for insight in accepted_insights
        ]

        # -------------------------------------------------------------
        # 7. Validate generated insights
        # -------------------------------------------------------------

        validation = validate_insights(
            accepted_insights
        )

        validation_status = validation.get(
            "overall_status",
            "FAILED",
        )

        decision_trace.append(
            self._trace(
                decision="Validate generated insights",
                reason=(
                    "Ensure every generated insight has the "
                    "required structure, evidence, and confidence."
                ),
                evidence={
                    "total_insights": len(
                        accepted_insights
                    ),
                    "validation": validation,
                },
                action="Run insight validation.",
                result=(
                    "Insight validation PASSED."
                    if validation_status == "PASSED"
                    else "Insight validation FAILED."
                ),
                validation_status=validation_status,
            )
        )

        if validation_status != "PASSED":
            errors.append(
                "Generated insight validation failed."
            )

            return InsightAgentResult(
                status="failed",
                insights=serialized_insights,
                validation=validation,
                total_insights=len(
                    serialized_insights
                ),
                evidence_sources=evidence_sources,
                decision_trace=decision_trace,
                warnings=warnings,
                errors=errors,
                message=(
                    "Insight generation completed but "
                    "validation failed."
                ),
            )

        # -------------------------------------------------------------
        # 8. Forecasting validation awareness
        # -------------------------------------------------------------

        if forecasting_result is not None:

            forecast_ok = self._validation_passed(
                forecasting_validation
            )

            if forecasting_validation is not None:
                decision_trace.append(
                    self._trace(
                        decision="Validate forecasting evidence",
                        reason=(
                            "Forecast-based insights should only "
                            "use validated forecasting results."
                        ),
                        evidence={
                            "forecasting_validation": (
                                forecasting_validation
                            ),
                        },
                        action=(
                            "Check forecasting validation "
                            "status."
                        ),
                        result=(
                            "Forecast validation PASSED."
                            if forecast_ok
                            else "Forecast validation did not pass."
                        ),
                        validation_status=(
                            "PASSED"
                            if forecast_ok
                            else "WARNING"
                        ),
                    )
                )

                if not forecast_ok:
                    warnings.append(
                        "Forecasting evidence was supplied but "
                        "forecast validation did not pass."
                    )

        # -------------------------------------------------------------
        # 9. Final status
        # -------------------------------------------------------------

        final_status = (
            "completed"
            if serialized_insights
            else "not_eligible"
        )

        decision_trace.append(
            self._trace(
                decision="Complete Insight Agent execution",
                reason=(
                    "Return only validated, evidence-grounded "
                    "insights to shared workflow state."
                ),
                evidence={
                    "total_insights": len(
                        serialized_insights
                    ),
                    "validation_status": validation_status,
                },
                action="Store structured insight result.",
                result=(
                    f"{len(serialized_insights)} validated "
                    "insight(s) returned."
                ),
                validation_status=validation_status,
            )
        )

        return InsightAgentResult(
            status=final_status,
            insights=serialized_insights,
            validation=validation,
            total_insights=len(
                serialized_insights
            ),
            evidence_sources=evidence_sources,
            decision_trace=decision_trace,
            warnings=warnings,
            errors=errors,
            message=(
                "Insight Agent completed successfully."
            ),
        )

    # -----------------------------------------------------------------
    # Evidence identification
    # -----------------------------------------------------------------

    @staticmethod
    def _identify_evidence_sources(
        kpi_results: Optional[Dict[str, Any]],
        trend_results: Optional[Dict[str, Any]],
        ranking_results: Optional[Dict[str, Any]],
        forecasting_result: Optional[Dict[str, Any]],
    ) -> List[str]:
        """
        Identify which analytical evidence sources are available.
        """

        sources: List[str] = []

        if isinstance(kpi_results, dict) and kpi_results:
            sources.append("validated_kpis")

        if isinstance(trend_results, dict) and trend_results:
            sources.append("validated_trends")

        if isinstance(ranking_results, dict) and ranking_results:
            sources.append("validated_rankings")

        if (
            isinstance(forecasting_result, dict)
            and forecasting_result
            and forecasting_result.get("status")
            == "completed"
        ):
            sources.append("validated_forecasting")

        return sources

    # -----------------------------------------------------------------
    # Validation helper
    # -----------------------------------------------------------------

    @staticmethod
    def _validation_passed(
        validation: Optional[Dict[str, Any]],
    ) -> bool:
        """
        Determine whether a validation result passed.

        If validation is not supplied, the agent does not assume
        failure. This allows standalone use while workflow integration
        can provide explicit validation results.
        """

        if validation is None:
            return True

        if not isinstance(validation, dict):
            return False

        status = validation.get(
            "overall_status"
        )

        if status is None:
            status = validation.get(
                "status"
            )

        return str(status).upper() == "PASSED"

    # -----------------------------------------------------------------
    # Confidence policy
    # -----------------------------------------------------------------

    def _apply_confidence_policy(
        self,
        insights: List[Insight],
    ) -> tuple[List[Insight], List[Insight]]:
        """
        Separate accepted and rejected insights according to
        the configured confidence threshold.
        """

        accepted: List[Insight] = []
        rejected: List[Insight] = []

        for insight in insights:

            confidence = insight.confidence

            try:
                confidence_value = float(
                    confidence
                )
            except (TypeError, ValueError):
                confidence_value = 0.0

            if (
                confidence_value
                >= self.minimum_confidence
            ):
                accepted.append(insight)
            else:
                rejected.append(insight)

        return accepted, rejected

    # -----------------------------------------------------------------
    # Decision trace
    # -----------------------------------------------------------------

    @staticmethod
    def _trace(
        decision: str,
        reason: str,
        evidence: Dict[str, Any],
        action: str,
        result: str,
        validation_status: str,
    ) -> Dict[str, Any]:
        """
        Create a standardised decision-trace entry.

        Required project structure:
            Decision
            Reason
            Evidence / Preconditions
            Action
            Result
            Validation Status
        """

        return {
            "decision": decision,
            "reason": reason,
            "evidence": evidence,
            "action": action,
            "result": result,
            "validation_status": validation_status,
        }


# =====================================================================
# CONVENIENCE FUNCTION
# =====================================================================

def run_insight_agent(
    kpi_results: Optional[Dict[str, Any]] = None,
    trend_results: Optional[Dict[str, Any]] = None,
    ranking_results: Optional[Dict[str, Any]] = None,
    forecasting_result: Optional[Dict[str, Any]] = None,
    eda_validation: Optional[Dict[str, Any]] = None,
    forecasting_validation: Optional[Dict[str, Any]] = None,
    minimum_confidence: float = 0.80,
) -> InsightAgentResult:
    """
    Convenience function for running the Insight Agent.
    """

    agent = InsightAgent(
        minimum_confidence=minimum_confidence
    )

    return agent.run(
        kpi_results=kpi_results,
        trend_results=trend_results,
        ranking_results=ranking_results,
        forecasting_result=forecasting_result,
        eda_validation=eda_validation,
        forecasting_validation=forecasting_validation,
    )