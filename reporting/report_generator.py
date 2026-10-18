
"""Evidence-grounded report generation for the Sales Intelligence System."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# HELPERS
# ============================================================

def _d(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _l(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []



def _present(value: Any) -> bool:
    """Safely determine whether a value is present, including DataFrames."""
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (dict, list, tuple, set)):
        return len(value) > 0

    # pandas DataFrame and Series expose an `empty` property.
    if hasattr(value, "empty"):
        try:
            return not value.empty
        except (TypeError, ValueError):
            return False

    try:
        return bool(value)
    except (TypeError, ValueError):
        # Avoid crashing on objects with ambiguous truth values.
        return True


def _has_data(value: Any) -> bool:
    """Check for substantive content rather than status metadata alone."""
    if value is None:
        return False

    if isinstance(value, str):
        return value.strip().lower() not in {
            "",
            "n/a",
            "na",
            "none",
            "not available",
            "not_available",
            "no data",
            "no results",
            "unknown",
        }

    if isinstance(value, dict):
        metadata_keys = {
            "status",
            "message",
            "available",
            "validation",
            "error",
        }

        return any(
            _has_data(item)
            for key, item in value.items()
            if key.lower() not in metadata_keys
        )

    if isinstance(value, (list, tuple, set)):
        return any(_has_data(item) for item in value)

    if hasattr(value, "empty"):
        try:
            return not value.empty
        except (TypeError, ValueError):
            return False

    try:
        return bool(value)
    except (TypeError, ValueError):
        return True


def _first(data: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if _present(value):
            return value
    return None


def _number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format(value: Any) -> str:
    number = _number(value)
    if number is None:
        return "N/A"
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}"


def _has_data(value: Any) -> bool:
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {
            "n/a", "na", "none", "not available",
            "not_available", "no data", "no results", "unknown"
        }

    if isinstance(value, dict):
        return any(_has_data(v) for v in value.values())

    if isinstance(value, (list, tuple)):
        return any(_has_data(v) for v in value)

    return True


def _passed(validation: Any) -> bool:
    return (
        str(_d(validation).get("overall_status", "")).upper()
        == "PASSED"
    )


def _unwrap(value: Any, *keys: str) -> Dict[str, Any]:
    """Unwrap common agent-result envelopes."""
    result = _d(value)

    for _ in range(3):
        nested = _first(
            result, *keys, "result", "data", "output"
        )

        if not isinstance(nested, dict) or nested is result:
            break

        result = nested

    return result


def _normalise_list(value: Any, *keys: str) -> List[Any]:
    if isinstance(value, (list, tuple)):
        return list(value)

    if isinstance(value, dict):
        for key in keys:
            if isinstance(value.get(key), list):
                return value[key]

        return [
            {"name": key, "value": item}
            for key, item in value.items()
            if _has_data(item)
        ]

    return []


# ============================================================
# REPORT MODELS
# ============================================================

@dataclass
class ReportSection:
    section_id: str
    title: str
    content: Any
    evidence_source: str
    status: str = "AVAILABLE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    title: str
    report_type: str
    executive_summary: str
    sections: List[Dict[str, Any]] = field(default_factory=list)
    evidence_sources: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    validation_status: str = "PENDING"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# UPSTREAM RESULT NORMALISATION
# ============================================================

def _eda(eda_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    e = _unwrap(
        eda_result, "eda_result", "eda", "analysis"
    )

    nested = _first(
        e, "results", "eda_results", "analysis_results"
    )

    if isinstance(nested, dict):
        merged = dict(nested)
        for key, value in e.items():
            merged.setdefault(key, value)
        e = merged

    summary = _d(e.get("summary"))

    kpis = _first(
        e, "kpis", "kpi_results", "key_performance_indicators"
    )
    trends = _first(
        e, "trends", "trend_results", "sales_trends", "time_series"
    )
    rankings = _first(
        e, "rankings", "ranking_results",
        "top_performers", "performance_rankings"
    )

    if not _present(kpis):
        kpis = _first(summary, "kpis", "kpi_results")

    if not _present(trends):
        trends = _first(summary, "trends", "trend_results")

    if not _present(rankings):
        rankings = _first(summary, "rankings", "ranking_results")

    return {
        "raw": e,
        "dataset": _d(_first(
            e, "dataset", "dataset_overview", "profile"
        )),
        "kpis": _d(kpis),
        "trends": trends if _present(trends) else {},
        "rankings": rankings if _present(rankings) else {},
        "validation": _d(_first(e, "validation", "eda_validation")),
    }


def _forecast(value: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    result = _unwrap(
        value, "forecasting_result", "forecast_result",
        "forecasting", "forecast"
    )

    nested = _first(
        result, "results", "forecast_results", "model_output"
    )

    if isinstance(nested, dict):
        merged = dict(nested)
        for key, item in result.items():
            merged.setdefault(key, item)
        result = merged

    return result


def _insights(value: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = _unwrap(
        value, "insight_result", "insights_result", "insight"
    )

    raw = _first(
        result, "insights", "key_insights",
        "business_insights", "items", "results"
    )

    return [
        item for item in _normalise_list(raw)
        if isinstance(item, dict)
    ]


def _recommendations(
    value: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    result = _unwrap(
        value, "recommendation_result",
        "recommendations_result", "recommendation"
    )

    raw = _first(
        result, "recommendations",
        "business_recommendations", "items", "results"
    )

    return [
        item for item in _normalise_list(raw)
        if isinstance(item, dict)
    ]


def _charts(value: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = _unwrap(
        value, "visualization_result", "visualizations", "visualization"
    )

    raw = _first(result, "charts", "figures", "visuals", "plots")

    return [
        item for item in _normalise_list(raw)
        if isinstance(item, dict)
    ]


# ============================================================
# SECTION BUILDERS
# ============================================================

def build_executive_summary(
    eda_result,
    forecasting_result=None,
    insight_result=None,
    recommendation_result=None,
) -> str:
    kpis = _eda(eda_result)["kpis"]
    parts = []

    metric_labels = {
        "total_sales": "Total sales",
        "total_revenue": "Total revenue",
        "total_orders": "Total orders",
        "total_customers": "Total customers",
        "total_quantity": "Total quantity sold",
        "average_order_value": "Average order value",
    }

    for key, label in metric_labels.items():
        if kpis.get(key) is not None:
            parts.append(f"{label}: {_format(kpis[key])}.")

    forecast = _forecast(forecasting_result)
    evaluation = _d(_first(
        forecast, "evaluation", "model_evaluation", "metrics"
    ))
    model = _first(
        evaluation, "best_model", "selected_model", "model_name"
    )

    if (
        str(forecast.get("status", "")).lower()
        in {"completed", "success", "passed"}
        and model
    ):
        parts.append(
            f"Forecasting completed using the {model} model."
        )

    insights = _insights(insight_result)
    recommendations = _recommendations(recommendation_result)

    if insights:
        parts.append(
            f"{len(insights)} insight(s) were supplied by the Insight Agent."
        )

    if recommendations:
        parts.append(
            f"{len(recommendations)} recommendation(s) were "
            "supplied by the Recommendation Agent."
        )

    return " ".join(parts) or (
        "The report consolidates the available upstream outputs. "
        "Recognised KPI values were not supplied for the summary."
    )


def build_dataset_overview(eda_result, semantic_mapping=None):
    result = dict(_eda(eda_result)["dataset"])

    if semantic_mapping:
        result["semantic_mapping"] = _d(semantic_mapping)

    if not result:
        return {
            "status": "NOT_AVAILABLE",
            "message": "Dataset overview was not supplied by the EDA Agent.",
        }

    return result


def build_data_quality_section(cleaning_result, cleaning_validation):
    validation = _d(cleaning_validation)

    return {
        "cleaning_result": _d(cleaning_result),
        "validation": validation,
        "status": (
            "VALIDATED" if _passed(validation)
            else "NOT_VALIDATED" if validation
            else "NOT_AVAILABLE"
        ),
    }


def build_kpi_section(eda_result):
    kpis = dict(_eda(eda_result)["kpis"])

    if not kpis:
        return {
            "status": "NOT_AVAILABLE",
            "message": "The EDA Agent did not provide KPI values.",
            "metrics": [],
        }

    metrics = [
        {
            "metric": str(name).replace("_", " ").title(),
            "value": value,
        }
        for name, value in kpis.items()
        if not isinstance(value, (dict, list))
    ]

    kpis["metrics"] = metrics
    kpis["status"] = "AVAILABLE" if metrics else "NOT_AVAILABLE"

    return kpis


def build_trend_section(eda_result):
    value = _eda(eda_result)["trends"]

    if isinstance(value, list):
        result = {"items": value}
    elif isinstance(value, dict):
        result = dict(value)
    else:
        result = {}

    if not result:
        return {
            "status": "NOT_AVAILABLE",
            "message": "The EDA Agent did not provide trend results.",
            "items": [],
        }

    items = _first(
        result, "items", "data", "trend_data", "series", "results"
    )

    if isinstance(items, list):
        result["items"] = items

    result["status"] = (
        "AVAILABLE" if _has_data(result) else "NOT_AVAILABLE"
    )

    return result


def build_ranking_section(eda_result):
    value = _eda(eda_result)["rankings"]

    if isinstance(value, list):
        result = {"items": value}
    elif isinstance(value, dict):
        result = dict(value)
    else:
        result = {}

    if not result:
        return {
            "status": "NOT_AVAILABLE",
            "message": "The EDA Agent did not provide ranking results.",
            "items": [],
        }

    items = _first(
        result, "items", "rankings", "top_products",
        "top_categories", "top_regions", "results"
    )

    if isinstance(items, list):
        result["items"] = items

    result["status"] = (
        "AVAILABLE" if _has_data(result) else "NOT_AVAILABLE"
    )

    return result


def build_visualization_section(visualization_result):
    result = _unwrap(
        visualization_result,
        "visualization_result", "visualization", "visualizations"
    )
    charts = _charts(visualization_result)

    return {
        "selection": _l(result.get("selection")),
        "kpi_cards": _l(result.get("kpi_cards")),
        "charts": charts,
        "total_charts": result.get("total_charts", len(charts)),
        "validation": _d(result.get("validation")),
        "status": "AVAILABLE" if charts else "NOT_AVAILABLE",
    }


def build_forecast_section(forecasting_result):
    result = _forecast(forecasting_result)

    if not result:
        return {
            "status": "NOT_AVAILABLE",
            "message": "Forecasting results were not supplied.",
            "forecast_values": [],
            "available": False,
        }

    values = _first(
        result, "forecast_values", "forecasts", "predictions",
        "forecast", "future_predictions"
    )

    return {
        "status": str(result.get("status", "UNKNOWN")).upper(),
        "eligibility": _d(_first(
            result, "eligibility", "forecasting_eligibility"
        )),
        "evaluation": _d(_first(
            result, "evaluation", "model_evaluation", "metrics"
        )),
        "forecast_values": values if values is not None else [],
        "validation": _d(_first(
            result, "validation", "forecast_validation"
        )),
        "message": result.get("message", ""),
        "available": _has_data(values),
    }


def build_insights_section(insight_result):
    return _insights(insight_result)


def build_recommendations_section(recommendation_result):
    return _recommendations(recommendation_result)


def build_limitations(
    capabilities=None,
    forecasting_result=None,
    visualization_result=None,
    eda_result=None,
    insight_result=None,
    recommendation_result=None,
):
    limitations = []

    if _d(capabilities).get("profitability_analysis") is False:
        limitations.append(
            "Profitability analysis is unavailable because the required "
            "profitability fields were not identified."
        )

    forecast = _forecast(forecasting_result)

    if not forecast:
        limitations.append(
            "Forecasting output was not supplied; no forecast values are reported."
        )
    elif str(forecast.get("status", "")).lower() in {
        "not_eligible", "failed", "unavailable"
    }:
        limitations.append(
            "Forecasting was not completed or was not eligible for this dataset."
        )
        for reason in _l(_d(forecast.get("eligibility")).get("reasons")):
            if isinstance(reason, str) and reason.strip():
                limitations.append(f"Forecast eligibility: {reason}")

    if not _charts(visualization_result):
        limitations.append(
            "No chart objects were supplied by the Visualization Agent."
        )

    eda = _eda(eda_result)

    if not eda["kpis"]:
        limitations.append("KPI values were not supplied by the EDA Agent.")

    if not _has_data(eda["trends"]):
        limitations.append("Trend results were not supplied by the EDA Agent.")

    if not _has_data(eda["rankings"]):
        limitations.append("Ranking results were not supplied by the EDA Agent.")

    if not _insights(insight_result):
        limitations.append(
            "No structured insights were supplied by the Insight Agent."
        )

    if not _recommendations(recommendation_result):
        limitations.append(
            "No structured recommendations were supplied by the Recommendation Agent."
        )

    return list(dict.fromkeys(limitations))


# ============================================================
# REPORT CONSTRUCTION
# ============================================================

def generate_report(
    eda_result,
    visualization_result=None,
    forecasting_result=None,
    insight_result=None,
    recommendation_result=None,
    semantic_mapping=None,
    capabilities=None,
    cleaning_result=None,
    cleaning_validation=None,
    eda_validation=None,
    visualization_validation=None,
    insight_validation=None,
    recommendation_validation=None,
):
    """Consolidate upstream outputs; do not invent analytical values."""

    specs = [
        ("dataset_overview", "Dataset Overview",
         build_dataset_overview(eda_result, semantic_mapping), "validated_eda"),
        ("data_quality", "Data Quality Summary",
         build_data_quality_section(cleaning_result, cleaning_validation),
         "validated_cleaning"),
        ("kpis", "KPI Summary",
         build_kpi_section(eda_result), "validated_kpis"),
        ("trends", "Trend Analysis",
         build_trend_section(eda_result), "validated_trends"),
        ("rankings", "Product, Regional and Customer Performance",
         build_ranking_section(eda_result), "validated_rankings"),
        ("visualizations", "Visualizations",
         build_visualization_section(visualization_result),
         "validated_visualizations"),
        ("forecast", "Forecast",
         build_forecast_section(forecasting_result), "validated_forecasting"),
        ("insights", "Key Insights",
         build_insights_section(insight_result), "validated_insights"),
        ("recommendations", "Recommendations",
         build_recommendations_section(recommendation_result),
         "validated_recommendations"),
    ]

    limitations = build_limitations(
        capabilities,
        forecasting_result,
        visualization_result,
        eda_result,
        insight_result,
        recommendation_result,
    )

    specs.append(
        ("limitations", "Limitations", limitations, "workflow_context")
    )

    sections = [
        ReportSection(
            section_id=section_id,
            title=title,
            content=content,
            evidence_source=evidence,
            status="AVAILABLE" if _has_data(content) else "NOT_AVAILABLE",
        ).to_dict()
        for section_id, title, content, evidence in specs
    ]

    report = Report(
        title="Sales Intelligence Report",
        report_type="Executive Sales Intelligence Report",
        executive_summary=build_executive_summary(
            eda_result,
            forecasting_result,
            insight_result,
            recommendation_result,
        ),
        sections=sections,
        evidence_sources=[item[3] for item in specs],
        limitations=limitations,
    ).to_dict()

    report["upstream_validation"] = {
        "eda": _d(eda_validation),
        "visualization": _d(visualization_validation),
        "insight": _d(insight_validation),
        "recommendation": _d(recommendation_validation),
    }

    return report


# ============================================================
# REPORT VALIDATION
# ============================================================

def validate_report(report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate structure and meaningful content in critical sections."""

    result = _d(report)
    checks = []

    required = {
        "title", "report_type", "executive_summary",
        "sections", "evidence_sources", "limitations",
    }

    missing = sorted(required - set(result))

    checks.append({
        "check": "required_report_fields",
        "status": "PASSED" if not missing else "FAILED",
        "missing_fields": missing,
    })

    sections = _l(result.get("sections"))

    checks.append({
        "check": "report_sections",
        "status": "PASSED" if sections else "FAILED",
        "section_count": len(sections),
    })

    required_section_fields = {
        "section_id", "title", "content", "evidence_source", "status"
    }

    invalid = []
    ids = []

    for section in sections:
        if not isinstance(section, dict):
            invalid.append({"error": "section_is_not_a_dictionary"})
            continue

        section_id = str(section.get("section_id", "")).strip()
        ids.append(section_id)

        absent = sorted(required_section_fields - set(section))

        if absent:
            invalid.append({
                "section_id": section_id,
                "missing_fields": absent,
            })

    checks.append({
        "check": "section_structure",
        "status": "PASSED" if not invalid else "FAILED",
        "invalid_sections": invalid,
    })

    duplicates = sorted({
        section_id for section_id in ids
        if section_id and ids.count(section_id) > 1
    })

    checks.append({
        "check": "unique_section_ids",
        "status": "PASSED" if not duplicates else "FAILED",
        "duplicate_section_ids": duplicates,
    })

    missing_evidence = [
        section.get("section_id")
        for section in sections
        if isinstance(section, dict)
        and not str(section.get("evidence_source", "")).strip()
    ]

    checks.append({
        "check": "evidence_traceability",
        "status": (
            "PASSED"
            if _l(result.get("evidence_sources")) and not missing_evidence
            else "FAILED"
        ),
        "missing_evidence_sections": missing_evidence,
    })

    summary = result.get("executive_summary")

    checks.append({
        "check": "executive_summary",
        "status": (
            "PASSED"
            if isinstance(summary, str) and summary.strip()
            else "FAILED"
        ),
    })

    checks.append({
        "check": "limitations",
        "status": (
            "PASSED" if isinstance(result.get("limitations"), list)
            else "FAILED"
        ),
    })

    by_id = {
        section.get("section_id"): section
        for section in sections
        if isinstance(section, dict)
    }

    critical = ("kpis", "trends", "rankings", "insights", "recommendations")
    missing_critical = []
    empty_critical = []

    for section_id in critical:
        section = by_id.get(section_id)

        if section is None:
            missing_critical.append(section_id)
        elif not _has_data(section.get("content")):
            empty_critical.append(section_id)

    checks.append({
        "check": "critical_analytical_sections",
        "status": (
            "PASSED"
            if not missing_critical and not empty_critical
            else "FAILED"
        ),
        "missing_sections": missing_critical,
        "empty_sections": empty_critical,
    })

    forecast_section = by_id.get("forecast", {})
    forecast_content = _d(forecast_section.get("content"))
    forecast_values = forecast_content.get("forecast_values")
    forecast_status = str(forecast_content.get("status", "")).upper()

    if _has_data(forecast_values):
        forecast_check = "PASSED"
    elif forecast_status in {
        "NOT_AVAILABLE", "NOT_ELIGIBLE", "FAILED",
        "UNAVAILABLE", "UNKNOWN", ""
    }:
        # Forecasting is conditional; an unavailable forecast is disclosed,
        # not silently represented as a successful prediction.
        forecast_check = "WARNING"
    else:
        forecast_check = "FAILED"

    checks.append({
        "check": "forecast_content",
        "status": forecast_check,
        "forecast_status": forecast_status or "MISSING",
        "has_forecast_values": _has_data(forecast_values),
    })

    failed = [check for check in checks if check["status"] == "FAILED"]
    warnings = [check for check in checks if check["status"] == "WARNING"]

    return {
        "overall_status": "FAILED" if failed else "PASSED",
        "total_checks": len(checks),
        "passed": sum(check["status"] == "PASSED" for check in checks),
        "failed": len(failed),
        "warnings": len(warnings),
        "checks": checks,
    }


def serialize_report(report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return dict(report) if isinstance(report, dict) else {}


def build_report(**kwargs: Any) -> Dict[str, Any]:
    """Build report and expose validation fields expected by the workflow."""
    report = generate_report(**kwargs)
    validation = validate_report(report)

    report["validation"] = validation
    report["report_validation"] = validation
    report["validation_status"] = validation["overall_status"]
    report["status"] = (
        "completed"
        if validation["overall_status"] == "PASSED"
        else "failed"
    )
    report["total_sections"] = len(_l(report.get("sections")))

    return serialize_report(report)


__all__ = [
    "ReportSection",
    "Report",
    "build_executive_summary",
    "build_dataset_overview",
    "build_data_quality_section",
    "build_kpi_section",
    "build_trend_section",
    "build_ranking_section",
    "build_visualization_section",
    "build_forecast_section",
    "build_insights_section",
    "build_recommendations_section",
    "build_limitations",
    "generate_report",
    "validate_report",
    "serialize_report",
    "build_report",
]
