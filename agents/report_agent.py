"""
Report Agent
============

8.8.2 Report Agent

Purpose:
    Consolidate validated EDA, visualization, forecasting, insight and
    recommendation outputs into one evidence-grounded Sales Intelligence
    Report.

The Report Agent does not perform new analytics and does not modify the
source dataset.

It:
    1. Enforces upstream validation gates.
    2. Delegates deterministic structured-report construction to
       reporting.report_generator.
    3. Validates the structured report.
    4. Delegates professional DOCX rendering to
       reporting.word_report_generator.
    5. Verifies the generated Word report.
    6. Returns the structured report and Word-report metadata.
"""

from __future__ import annotations

import os

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from reporting.report_generator import (
    build_report,
    serialize_report,
    validate_report,
)

from reporting.word_report_generator import (
    build_word_report,
)


# =====================================================================
# RESULT OBJECT
# =====================================================================


@dataclass
class ReportAgentResult:
    """Structured result returned by the Report Agent."""

    status: str

    report: Dict[str, Any] = field(default_factory=dict)

    report_validation: Dict[str, Any] = field(
        default_factory=dict
    )

    total_sections: int = 0

    evidence_sources: List[str] = field(
        default_factory=list
    )

    decision_trace: List[Dict[str, Any]] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    message: str = ""

    # -------------------------------------------------------------
    # Word report output
    # -------------------------------------------------------------

    word_report_path: str = ""

    word_report_status: str = "not_generated"

    word_report_error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Report Agent result."""

        return asdict(self)


# =====================================================================
# REPORT AGENT
# =====================================================================


class ReportAgent:
    """Agent responsible only for validated report consolidation."""

    AGENT_NAME = "Report Agent"

    def __init__(
        self,
        eda_result: Optional[Dict[str, Any]] = None,
        visualization_result: Optional[Dict[str, Any]] = None,
        forecasting_result: Optional[Dict[str, Any]] = None,
        insight_result: Optional[Dict[str, Any]] = None,
        recommendation_result: Optional[Dict[str, Any]] = None,
        semantic_mapping: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        cleaning_result: Optional[Dict[str, Any]] = None,
        cleaning_validation: Optional[Dict[str, Any]] = None,
        eda_validation: Optional[Dict[str, Any]] = None,
        visualization_validation: Optional[Dict[str, Any]] = None,
        insight_validation: Optional[Dict[str, Any]] = None,
        recommendation_validation: Optional[Dict[str, Any]] = None,

        # ---------------------------------------------------------
        # Word report configuration
        # ---------------------------------------------------------

        dataset_name: Optional[str] = None,
        word_report_output_directory: str = "reports",
        word_report_filename: str = "Sales_Intelligence_Report.docx",
    ) -> None:

        self.eda_result = eda_result or {}

        self.visualization_result = (
            visualization_result or {}
        )

        self.forecasting_result = (
            forecasting_result or {}
        )

        self.insight_result = (
            insight_result or {}
        )

        self.recommendation_result = (
            recommendation_result or {}
        )

        self.semantic_mapping = (
            semantic_mapping or {}
        )

        self.capabilities = (
            capabilities or {}
        )

        self.cleaning_result = (
            cleaning_result or {}
        )

        self.cleaning_validation = (
            cleaning_validation or {}
        )

        self.eda_validation = (
            eda_validation or {}
        )

        self.visualization_validation = (
            visualization_validation or {}
        )

        self.insight_validation = (
            insight_validation or {}
        )

        self.recommendation_validation = (
            recommendation_validation or {}
        )

        # ---------------------------------------------------------
        # Word report configuration
        # ---------------------------------------------------------

        self.dataset_name = (
            dataset_name
            or "Uploaded Dataset"
        )

        self.word_report_output_directory = (
            word_report_output_directory
            or "reports"
        )

        self.word_report_filename = (
            word_report_filename
            or "Sales_Intelligence_Report.docx"
        )


    # =================================================================
    # VALIDATION HELPERS
    # =================================================================

    @staticmethod
    def _passed(validation: Any) -> bool:
        """Return True when a validation result passed."""

        return (
            isinstance(validation, dict)
            and str(
                validation.get(
                    "overall_status",
                    "",
                )
            ).upper()
            == "PASSED"
        )


    @staticmethod
    def _status(result: Any) -> str:
        """Return normalized result status."""

        if not isinstance(result, dict):
            return ""

        return str(
            result.get(
                "status",
                "",
            )
        ).lower()


    # =================================================================
    # PRECONDITIONS
    # =================================================================

    def check_preconditions(self) -> bool:
        """
        Check whether required upstream results and validation
        gates are available.
        """

        required_results = [
            (
                "EDA",
                self.eda_result,
            ),
            (
                "Visualization",
                self.visualization_result,
            ),
            (
                "Insight",
                self.insight_result,
            ),
            (
                "Recommendation",
                self.recommendation_result,
            ),
        ]

        for name, result in required_results:

            if not isinstance(
                result,
                dict,
            ) or not result:

                return False

        required_validations = [
            (
                "EDA",
                self.eda_validation,
            ),
            (
                "Visualization",
                self.visualization_validation,
            ),
            (
                "Insight",
                self.insight_validation,
            ),
            (
                "Recommendation",
                self.recommendation_validation,
            ),
        ]

        return all(
            self._passed(validation)
            for _, validation
            in required_validations
        )


    # =================================================================
    # EVIDENCE IDENTIFICATION
    # =================================================================

    def identify_evidence_sources(
        self,
    ) -> List[str]:
        """
        Identify the bounded analytical evidence sources used
        by the Report Agent.
        """

        sources = [
            "validated_eda",
            "validated_cleaning",
            "validated_kpis",
            "validated_trends",
            "validated_rankings",
            "validated_visualizations",
            "validated_forecasting",
            "validated_insights",
            "validated_recommendations",
            "workflow_context",
        ]

        # Forecasting is conditional.
        if not self.forecasting_result:

            sources.remove(
                "validated_forecasting"
            )

        return sources


    # =================================================================
    # DECISION TRACE
    # =================================================================

    def _build_trace(
        self,
        decision: str,
        reason: str,
        evidence: Any,
        action: str,
        result: str,
        validation_status: str,
    ) -> Dict[str, Any]:

        return {
            "decision": decision,
            "reason": reason,
            "evidence": evidence,
            "action": action,
            "result": result,
            "validation_status": validation_status,
        }


    # =================================================================
    # WORD REPORT GENERATION
    # =================================================================

    def _generate_word_report(
        self,
        report: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the professional DOCX report from the already
        validated structured report.

        No new analytics are performed here.
        """

        result = {
            "status": "not_generated",
            "path": "",
            "error": "",
        }

        try:

            output_path = build_word_report(
                report=report,
                output_directory=(
                    self.word_report_output_directory
                ),
                filename=self.word_report_filename,
                dataset_name=self.dataset_name,
            )

            if not output_path:

                result["status"] = "failed"

                result["error"] = (
                    "Word report generator returned "
                    "an empty output path."
                )

                return result

            if not os.path.isfile(
                output_path
            ):

                result["status"] = "failed"

                result["error"] = (
                    "Word report file was not created: "
                    f"{output_path}"
                )

                return result

            file_size = os.path.getsize(
                output_path
            )

            if file_size <= 0:

                result["status"] = "failed"

                result["error"] = (
                    "Generated Word report is empty: "
                    f"{output_path}"
                )

                return result

            result["status"] = "generated"

            result["path"] = os.path.abspath(
                output_path
            )

            return result

        except Exception as exc:

            result["status"] = "failed"

            result["error"] = (
                f"Word report generation failed: {exc}"
            )

            return result


    # =================================================================
    # MAIN EXECUTION
    # =================================================================

    def run(self) -> ReportAgentResult:
        """
        Generate, validate and return the final structured report
        together with the professional Word report.
        """

        trace: List[Dict[str, Any]] = []

        warnings: List[str] = []

        errors: List[str] = []

        word_report_path = ""

        word_report_status = (
            "not_generated"
        )

        word_report_error = ""


        # -------------------------------------------------------------
        # 1. Preconditions
        # -------------------------------------------------------------

        trace.append(
            self._build_trace(
                decision=(
                    "Check Report Agent preconditions"
                ),
                reason=(
                    "The report may only consolidate "
                    "validated upstream outputs."
                ),
                evidence={
                    "eda_validation":
                        self.eda_validation,

                    "visualization_validation":
                        self.visualization_validation,

                    "insight_validation":
                        self.insight_validation,

                    "recommendation_validation":
                        self.recommendation_validation,
                },
                action=(
                    "Evaluate required upstream "
                    "validation gates."
                ),
                result=(
                    "Validation gates evaluated."
                ),
                validation_status="PENDING",
            )
        )


        if not self.check_preconditions():

            errors.append(
                "Report generation requires non-empty "
                "EDA, visualization, insight and "
                "recommendation results with passed "
                "validation gates."
            )

            trace.append(
                self._build_trace(
                    decision=(
                        "Block report generation"
                    ),
                    reason=(
                        "One or more required upstream "
                        "results or validation gates are "
                        "missing or failed."
                    ),
                    evidence={},
                    action=(
                        "Do not generate the final report."
                    ),
                    result=(
                        "Report generation blocked."
                    ),
                    validation_status="FAILED",
                )
            )

            return ReportAgentResult(
                status="failed",
                report={},
                report_validation={},
                total_sections=0,
                evidence_sources=[],
                decision_trace=trace,
                warnings=warnings,
                errors=errors,
                message=(
                    "Report Agent validation "
                    "gate failed."
                ),
                word_report_path="",
                word_report_status=(
                    "not_generated"
                ),
                word_report_error="",
            )


        # -------------------------------------------------------------
        # 2. Evidence identification
        # -------------------------------------------------------------

        evidence_sources = (
            self.identify_evidence_sources()
        )

        trace.append(
            self._build_trace(
                decision=(
                    "Identify report evidence"
                ),
                reason=(
                    "Use only validated analytical "
                    "and upstream workflow outputs."
                ),
                evidence={
                    "evidence_sources":
                        evidence_sources
                },
                action=(
                    "Map validated outputs to "
                    "report sections."
                ),
                result=(
                    f"Identified "
                    f"{len(evidence_sources)} "
                    "evidence source(s)."
                ),
                validation_status="PASSED",
            )
        )


        # -------------------------------------------------------------
        # 3. Generate structured report
        # -------------------------------------------------------------

        try:

            report = build_report(
                eda_result=self.eda_result,

                visualization_result=(
                    self.visualization_result
                ),

                forecasting_result=(
                    self.forecasting_result
                    or None
                ),

                insight_result=(
                    self.insight_result
                ),

                recommendation_result=(
                    self.recommendation_result
                ),

                semantic_mapping=(
                    self.semantic_mapping
                ),

                capabilities=(
                    self.capabilities
                ),

                cleaning_result=(
                    self.cleaning_result
                ),

                cleaning_validation=(
                    self.cleaning_validation
                ),

                eda_validation=(
                    self.eda_validation
                ),

                visualization_validation=(
                    self.visualization_validation
                ),

                insight_validation=(
                    self.insight_validation
                ),

                recommendation_validation=(
                    self.recommendation_validation
                ),
            )

        except Exception as exc:

            errors.append(
                f"Report generation failed: {exc}"
            )

            trace.append(
                self._build_trace(
                    decision=(
                        "Generate report"
                    ),
                    reason=(
                        "Delegate deterministic "
                        "report construction to the "
                        "Report Generator."
                    ),
                    evidence={
                        "evidence_sources":
                            evidence_sources
                    },
                    action=(
                        "Call build_report()."
                    ),
                    result=(
                        "Report generation raised "
                        "an exception."
                    ),
                    validation_status="FAILED",
                )
            )

            return ReportAgentResult(
                status="failed",
                report={},
                report_validation={},
                total_sections=0,
                evidence_sources=evidence_sources,
                decision_trace=trace,
                warnings=warnings,
                errors=errors,
                message=(
                    "Report Agent could not "
                    "generate the report."
                ),
                word_report_path="",
                word_report_status=(
                    "not_generated"
                ),
                word_report_error="",
            )


        trace.append(
            self._build_trace(
                decision=(
                    "Generate consolidated report"
                ),
                reason=(
                    "All required upstream "
                    "validation gates passed."
                ),
                evidence={
                    "evidence_sources":
                        evidence_sources
                },
                action=(
                    "Build the structured "
                    "Sales Intelligence Report."
                ),
                result=(
                    f"Generated "
                    f"{len(report.get('sections', []))} "
                    "report sections."
                ),
                validation_status="PENDING",
            )
        )


        # -------------------------------------------------------------
        # 4. Validate structured report
        # -------------------------------------------------------------

        report_validation = validate_report(
            report
        )

        report["validation"] = (
            report_validation
        )

        report["validation_status"] = (
            report_validation.get(
                "overall_status",
                "FAILED",
            )
        )


        if (
            report_validation.get(
                "overall_status"
            )
            != "PASSED"
        ):

            errors.append(
                "Generated report failed "
                "report-structure validation."
            )

            status = "failed"

        else:

            status = "completed"


        trace.append(
            self._build_trace(
                decision=(
                    "Validate final report"
                ),
                reason=(
                    "Confirm required report fields, "
                    "section structure, evidence "
                    "traceability, executive summary "
                    "and limitations."
                ),
                evidence=(
                    report_validation
                ),
                action=(
                    "Run validate_report()."
                ),
                result=(
                    "Report validation status: "
                    f"{report_validation.get(
                        'overall_status',
                        'FAILED'
                    )}."
                ),
                validation_status=(
                    report_validation.get(
                        "overall_status",
                        "FAILED",
                    )
                ),
            )
        )


        # -------------------------------------------------------------
        # 5. Generate Word report
        # -------------------------------------------------------------

        if status == "completed":

            word_report_result = (
                self._generate_word_report(
                    report=report
                )
            )

            word_report_status = (
                word_report_result["status"]
            )

            word_report_path = (
                word_report_result["path"]
            )

            word_report_error = (
                word_report_result["error"]
            )


            if word_report_status == "generated":

                trace.append(
                    self._build_trace(
                        decision=(
                            "Generate professional "
                            "Word report"
                        ),
                        reason=(
                            "The structured report "
                            "passed validation and can "
                            "now be rendered into the "
                            "final DOCX deliverable."
                        ),
                        evidence={
                            "report_validation":
                                report_validation,

                            "dataset_name":
                                self.dataset_name,

                            "word_report_path":
                                word_report_path,
                        },
                        action=(
                            "Call build_word_report() "
                            "and verify the generated "
                            "DOCX file."
                        ),
                        result=(
                            "Word report generated "
                            "and verified successfully."
                        ),
                        validation_status="PASSED",
                    )
                )

            else:

                errors.append(
                    word_report_error
                    or (
                        "Word report generation "
                        "failed."
                    )
                )

                trace.append(
                    self._build_trace(
                        decision=(
                            "Generate professional "
                            "Word report"
                        ),
                        reason=(
                            "The structured report "
                            "passed validation but the "
                            "DOCX rendering step failed."
                        ),
                        evidence={
                            "report_validation":
                                report_validation,

                            "word_report_error":
                                word_report_error,
                        },
                        action=(
                            "Call build_word_report() "
                            "and verify the generated "
                            "DOCX file."
                        ),
                        result=(
                            "Word report generation "
                            "failed."
                        ),
                        validation_status="FAILED",
                    )
                )

                status = "failed"


        # -------------------------------------------------------------
        # 6. Forecast warning
        # -------------------------------------------------------------

        if self._status(
            self.forecasting_result
        ) in {
            "not_eligible",
            "not_available",
            "skipped",
        }:

            warnings.append(
                "Forecasting was unavailable or "
                "not eligible; the report "
                "discloses this limitation."
            )


        # -------------------------------------------------------------
        # 7. Final trace
        # -------------------------------------------------------------

        final_validation_status = (
            "PASSED"
            if status == "completed"
            else "FAILED"
        )


        trace.append(
            self._build_trace(
                decision=(
                    "Finalize Report Agent result"
                ),
                reason=(
                    "Return the validated report "
                    "and Word-report deliverable "
                    "without modifying analytical "
                    "evidence."
                ),
                evidence={
                    "structured_report_validation":
                        report.get(
                            "validation_status"
                        ),

                    "word_report_status":
                        word_report_status,

                    "word_report_path":
                        word_report_path,
                },
                action=(
                    "Serialize the report into "
                    "shared workflow state and "
                    "return Word-report metadata."
                ),
                result=(
                    f"Report Agent status: "
                    f"{status}."
                ),
                validation_status=(
                    final_validation_status
                ),
            )
        )


        # -------------------------------------------------------------
        # 8. Return final result
        # -------------------------------------------------------------

        if status == "completed":

            message = (
                "Sales Intelligence Report "
                "generated, validated and "
                "rendered to Word successfully."
            )

        else:

            message = (
                "Sales Intelligence Report "
                "generation or Word rendering "
                "failed."
            )


        return ReportAgentResult(
            status=status,

            report=serialize_report(
                report
            ),

            report_validation=(
                report_validation
            ),

            total_sections=len(
                report.get(
                    "sections",
                    [],
                )
            ),

            evidence_sources=(
                evidence_sources
            ),

            decision_trace=trace,

            warnings=warnings,

            errors=errors,

            message=message,

            word_report_path=(
                word_report_path
            ),

            word_report_status=(
                word_report_status
            ),

            word_report_error=(
                word_report_error
            ),
        )


# =====================================================================
# CONVENIENCE FUNCTION
# =====================================================================


def run_report_agent(
    eda_result: Dict[str, Any],
    visualization_result: Dict[str, Any],
    forecasting_result: Optional[Dict[str, Any]],
    insight_result: Dict[str, Any],
    recommendation_result: Dict[str, Any],
    semantic_mapping: Optional[Dict[str, Any]] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    cleaning_result: Optional[Dict[str, Any]] = None,
    cleaning_validation: Optional[Dict[str, Any]] = None,
    eda_validation: Optional[Dict[str, Any]] = None,
    visualization_validation: Optional[Dict[str, Any]] = None,
    insight_validation: Optional[Dict[str, Any]] = None,
    recommendation_validation: Optional[Dict[str, Any]] = None,

    # -------------------------------------------------------------
    # Word report configuration
    # -------------------------------------------------------------

    dataset_name: Optional[str] = None,

    word_report_output_directory: str = "reports",

    word_report_filename: str = (
        "Sales_Intelligence_Report.docx"
    ),
) -> ReportAgentResult:
    """Convenience function for running the Report Agent."""

    agent = ReportAgent(
        eda_result=eda_result,

        visualization_result=(
            visualization_result
        ),

        forecasting_result=(
            forecasting_result
        ),

        insight_result=(
            insight_result
        ),

        recommendation_result=(
            recommendation_result
        ),

        semantic_mapping=(
            semantic_mapping
        ),

        capabilities=(
            capabilities
        ),

        cleaning_result=(
            cleaning_result
        ),

        cleaning_validation=(
            cleaning_validation
        ),

        eda_validation=(
            eda_validation
        ),

        visualization_validation=(
            visualization_validation
        ),

        insight_validation=(
            insight_validation
        ),

        recommendation_validation=(
            recommendation_validation
        ),

        dataset_name=(
            dataset_name
        ),

        word_report_output_directory=(
            word_report_output_directory
        ),

        word_report_filename=(
            word_report_filename
        ),
    )

    return agent.run()


# =====================================================================
# PUBLIC API
# =====================================================================


__all__ = [
    "ReportAgent",
    "ReportAgentResult",
    "run_report_agent",
]