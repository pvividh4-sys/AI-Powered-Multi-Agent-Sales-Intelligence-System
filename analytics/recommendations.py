
"""
Evidence-grounded recommendation generator for the
AI-Powered Multi-Agent Sales Intelligence System.

Responsibilities:
- Convert validated insights into actionable recommendations.
- Preserve evidence from the Insight Agent.
- Assign priority using insight confidence.
- Include business implications and analytical limitations.
- Remove duplicate recommendations.
- Avoid unsupported causal claims.

Public API:
    Recommendation
    generate_recommendation(insight, index=1)
    generate_all_recommendations(insights)
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
import math
import re


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class Recommendation:
    recommendation_id: str
    recommendation_type: str
    title: str
    evidence: Dict[str, Any]
    insight: str
    business_implication: str
    recommendation: str
    priority: str
    confidence: float
    limitations: List[str] = field(default_factory=list)
    validation_status: str = "PENDING"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the recommendation to a serialisable dictionary."""
        return asdict(self)


# ============================================================
# GENERAL HELPERS
# ============================================================

def _safe_float(value: Any) -> Optional[float]:
    """Convert a value to a finite float, if possible."""
    try:
        if value is None or isinstance(value, bool):
            return None

        number = float(value)

        if not math.isfinite(number):
            return None

        return number

    except (TypeError, ValueError, OverflowError):
        return None


def _get_insight_type(insight: Dict[str, Any]) -> str:
    """Return the normalised insight category."""
    value = insight.get("insight_type", "")
    return str(value or "").strip().lower().replace("_", " ")


def _get_insight_title(insight: Dict[str, Any]) -> str:
    """Return the insight title."""
    return str(insight.get("title") or "").strip()


def _get_insight_statement(insight: Dict[str, Any]) -> str:
    """Support the existing statement field and common alternatives."""
    for key in ("statement", "insight", "description", "summary"):
        value = insight.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def _get_insight_evidence(
    insight: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Preserve structured evidence without inventing measurements.

    Non-dictionary evidence is wrapped so that the existing
    Recommendation dataclass can continue to use a dictionary.
    """
    evidence = insight.get("evidence")

    if isinstance(evidence, dict):
        return evidence.copy()

    if isinstance(evidence, list):
        return {"items": evidence.copy()} if evidence else {}

    if evidence is not None and str(evidence).strip():
        return {"details": str(evidence).strip()}

    # Some insight producers store supporting metrics separately.
    supporting_metrics = insight.get("supporting_metrics")

    if isinstance(supporting_metrics, dict) and supporting_metrics:
        return supporting_metrics.copy()

    if isinstance(supporting_metrics, list) and supporting_metrics:
        return {"supporting_metrics": supporting_metrics.copy()}

    return {}


def _get_insight_confidence(insight: Dict[str, Any]) -> float:
    """Normalise confidence to the range 0.0–1.0."""
    confidence = _safe_float(insight.get("confidence"))

    if confidence is None:
        return 0.0

    # Accommodate confidence values expressed on a 0–100 scale.
    if 1.0 < confidence <= 100.0:
        confidence /= 100.0

    return max(0.0, min(1.0, confidence))


def _priority_from_confidence(confidence: float) -> str:
    """
    Assign a provisional priority from confidence.

    Priority is not a measure of financial impact or urgency.
    """
    if confidence >= 0.90:
        return "HIGH"

    if confidence >= 0.75:
        return "MEDIUM"

    return "LOW"


def _base_limitation(insight: Dict[str, Any]) -> List[str]:
    """Build limitations without overstating what the data proves."""
    limitations = [
        "The recommendation is based on the analytical evidence supplied "
        "by the Insight Agent.",
        "The observed pattern does not, by itself, establish its exact "
        "business cause.",
        "Validate the recommendation against operational context before "
        "making a major business decision.",
    ]

    existing = insight.get("limitations")

    if isinstance(existing, list):
        for item in existing:
            text = str(item).strip()

            if text and text not in limitations:
                limitations.append(text)

    elif isinstance(existing, str) and existing.strip():
        if existing.strip() not in limitations:
            limitations.append(existing.strip())

    return limitations


def _contains_any(text: str, keywords: List[str]) -> bool:
    """Check for keywords as whole words or word stems."""
    return any(keyword in text for keyword in keywords)


def _make_recommendation(
    insight: Dict[str, Any],
    index: int,
    category: str,
    title: str,
    implication: str,
    action: str,
) -> Recommendation:
    """Construct a recommendation using the existing public schema."""
    confidence = _get_insight_confidence(insight)

    return Recommendation(
        recommendation_id=f"REC-{category.upper()}-{index:03d}",
        recommendation_type=category,
        title=title,
        evidence=_get_insight_evidence(insight),
        insight=_get_insight_statement(insight),
        business_implication=implication,
        recommendation=action,
        priority=_priority_from_confidence(confidence),
        confidence=confidence,
        limitations=_base_limitation(insight),
    )


def _normalise_for_deduplication(value: Any) -> str:
    """Normalise text to detect repeated recommendations."""
    text = str(value or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text


# ============================================================
# PRODUCT RECOMMENDATIONS
# ============================================================

def _product_recommendation(
    insight: Dict[str, Any],
    index: int,
) -> Optional[Recommendation]:
    insight_type = _get_insight_type(insight)
    statement = _get_insight_statement(insight)
    title = _get_insight_title(insight)

    if "product" not in insight_type and "categor" not in insight_type:
        return None

    text = f"{title} {statement}".lower()

    if _contains_any(
        text,
        ["declin", "decreas", "drop", "fall", "underperform", "weak"],
    ):
        return _make_recommendation(
            insight,
            index,
            "Product",
            f"Investigate declining product performance: "
            f"{title or 'identified product'}",
            (
                "The observed product or category performance may indicate "
                "reduced demand or another commercial issue requiring review."
            ),
            (
                "Review the product's sales history, stock availability, "
                "pricing, customer demand and promotional activity. Compare "
                "these factors across relevant periods before deciding "
                "whether to change pricing, inventory or promotion."
            ),
        )

    if _contains_any(
        text,
        ["highest", "top performing", "best performing", "strongest", "leading"],
    ):
        return _make_recommendation(
            insight,
            index,
            "Product",
            f"Review high-performing product: {title or 'identified product'}",
            (
                "The identified product or category is a strong performer "
                "under the metric described in the insight."
            ),
            (
                "Monitor demand and inventory availability for the "
                "identified product. Examine which measurable factors "
                "coincide with its performance before applying the same "
                "approach to other products."
            ),
        )

    if _contains_any(text, ["profit", "margin", "cost", "discount"]):
        return _make_recommendation(
            insight,
            index,
            "Product",
            f"Review product profitability: {title or 'identified product'}",
            (
                "The insight identifies a product-level financial pattern "
                "that may affect commercial performance."
            ),
            (
                "Compare revenue with available cost, margin and discount "
                "data. Review the contribution of the affected products "
                "before changing prices or promotional policies."
            ),
        )

    return _make_recommendation(
        insight,
        index,
        "Product",
        f"Monitor product performance: {title or 'product analysis'}",
        (
            "The product-level finding may be relevant to assortment, "
            "inventory and sales planning."
        ),
        (
            "Track the relevant product metric over time and compare it "
            "with other products or categories using consistent measures. "
            "Investigate material changes before taking action."
        ),
    )


# ============================================================
# CUSTOMER RECOMMENDATIONS
# ============================================================

def _customer_recommendation(
    insight: Dict[str, Any],
    index: int,
) -> Optional[Recommendation]:
    insight_type = _get_insight_type(insight)

    if "customer" not in insight_type or "customer" not in (
        _get_insight_title(insight) + " " + _get_insight_statement(insight)
    ).lower():
        # The category alone can be sufficient if the insight is valid.
        if "customer" not in insight_type:
            return None

    title = _get_insight_title(insight)
    text = f"{title} {_get_insight_statement(insight)}".lower()

    if _contains_any(
        text,
        [
            "concentration",
            "top customer",
            "top customers",
            "high-value",
            "high value",
            "largest customer",
            "customer contribution",
        ],
    ):
        return _make_recommendation(
            insight,
            index,
            "Customer",
            "Review customer concentration and retention",
            (
                "A material share of observed sales may be associated "
                "with a limited set of customers."
            ),
            (
                "Measure the proportion of sales contributed by leading "
                "customers and monitor changes over time. Consider "
                "appropriate retention and engagement activities while "
                "evaluating the business's exposure to customer loss."
            ),
        )

    if _contains_any(
        text,
        ["declin", "inactive", "lost customer", "churn", "decreas"],
    ):
        return _make_recommendation(
            insight,
            index,
            "Customer",
            "Investigate changes in customer activity",
            (
                "The observed customer-level pattern may indicate a change "
                "in engagement, purchasing frequency or sales contribution."
            ),
            (
                "Compare customer activity across equivalent periods. "
                "Identify which customer groups account for the change "
                "and investigate available order frequency, recency and "
                "sales-value measures before designing retention actions."
            ),
        )

    return _make_recommendation(
        insight,
        index,
        "Customer",
        "Monitor customer sales behaviour",
        (
            "The customer-level finding may help inform customer "
            "management and sales planning."
        ),
        (
            "Track the relevant customer metric over time and segment "
            "customers using available purchasing behaviour. Base "
            "engagement decisions on observed patterns rather than "
            "assuming a particular reason for customer behaviour."
        ),
    )


# ============================================================
# REGIONAL RECOMMENDATIONS
# ============================================================

def _regional_recommendation(
    insight: Dict[str, Any],
    index: int,
) -> Optional[Recommendation]:
    insight_type = _get_insight_type(insight)

    if not any(word in insight_type for word in ("regional", "region", "geograph")):
        return None

    title = _get_insight_title(insight)
    text = f"{title} {_get_insight_statement(insight)}".lower()

    if _contains_any(
        text,
        ["declin", "decreas", "drop", "fall", "low", "underperform", "weak"],
    ):
        return _make_recommendation(
            insight,
            index,
            "Regional",
            "Investigate weaker regional performance",
            (
                "The observed regional pattern identifies an area that "
                "may require further commercial investigation."
            ),
            (
                "Compare regional sales across equivalent periods and "
                "review available product mix, order volume, customer "
                "activity and distribution information. Investigate "
                "differences before changing regional investment."
            ),
        )

    if _contains_any(
        text,
        ["highest", "top", "strongest", "leading", "high growth"],
    ):
        return _make_recommendation(
            insight,
            index,
            "Regional",
            "Evaluate practices in high-performing regions",
            (
                "The identified region performs strongly under the "
                "metric described in the insight."
            ),
            (
                "Examine product mix, order patterns and other available "
                "regional metrics. Determine whether the observed "
                "performance is consistent over time before considering "
                "whether comparable practices could work in other regions."
            ),
        )

    return _make_recommendation(
        insight,
        index,
        "Regional",
        "Monitor regional sales performance",
        (
            "The regional finding may support geographic sales planning."
        ),
        (
            "Monitor the relevant regional metric over time and compare "
            "regions using consistent periods and measures. Investigate "
            "meaningful differences before reallocating resources."
        ),
    )


# ============================================================
# FORECAST RECOMMENDATIONS
# ============================================================

def _forecast_recommendation(
    insight: Dict[str, Any],
    index: int,
) -> Optional[Recommendation]:
    insight_type = _get_insight_type(insight)
    text = (
        f"{_get_insight_title(insight)} "
        f"{_get_insight_statement(insight)}"
    ).lower()

    if "forecast" not in insight_type and "forecast" not in text:
        return None

    if _contains_any(text, ["declin", "decreas", "fall", "drop"]):
        action = (
            "Compare the forecast with recent actual sales and historical "
            "seasonality. Review inventory, demand and other available "
            "business indicators, and prepare contingency options if the "
            "decline is supported by subsequent observations."
        )
        implication = (
            "The forecast suggests a possible decline, subject to the "
            "model's accuracy and the stability of historical patterns."
        )
        title = "Review potential forecasted sales decline"

    elif _contains_any(text, ["growth", "increas", "rise", "upward"]):
        action = (
            "Compare forecasted demand with inventory capacity and recent "
            "actual results. Monitor forecast errors as new observations "
            "arrive before committing to additional stock or resources."
        )
        implication = (
            "The forecast suggests potential growth but does not guarantee "
            "that future sales will follow the predicted pattern."
        )
        title = "Monitor forecasted sales growth"

    else:
        action = (
            "Monitor forecast values against actual sales as new data "
            "arrives. Review evaluation metrics and compare performance "
            "with a simple baseline before using the forecast for "
            "operational planning."
        )
        implication = (
            "The forecast provides a planning estimate whose usefulness "
            "depends on out-of-sample performance and changing conditions."
        )
        title = "Monitor forecast reliability"

    return _make_recommendation(
        insight,
        index,
        "Forecast",
        title,
        implication,
        action,
    )


# ============================================================
# GENERAL / SALES RECOMMENDATIONS
# ============================================================

def _general_recommendation(
    insight: Dict[str, Any],
    index: int,
) -> Optional[Recommendation]:
    statement = _get_insight_statement(insight)
    title = _get_insight_title(insight)

    if not statement:
        return None

    text = f"{title} {statement}".lower()

    if _contains_any(
        text,
        ["declin", "decreas", "drop", "fall", "negative growth"],
    ):
        action = (
            "Compare the affected sales metric across equivalent periods. "
            "Break down the change by available products, customers and "
            "regions, then investigate the largest observed contributors."
        )
        implication = (
            "The observed decline may affect sales planning and warrants "
            "investigation of the segments contributing to the change."
        )
        recommendation_title = "Investigate declining sales performance"

    elif _contains_any(
        text,
        ["growth", "increas", "rise", "positive trend"],
    ):
        action = (
            "Verify that the growth pattern persists across comparable "
            "periods. Identify the segments contributing to the change "
            "and monitor relevant operational constraints before "
            "expanding investment."
        )
        implication = (
            "The observed growth may represent an opportunity if it "
            "persists and can be supported operationally."
        )
        recommendation_title = "Validate and monitor sales growth"

    elif _contains_any(text, ["anomal", "outlier", "unusual", "spike"]):
        action = (
            "Check the affected records and compare the unusual value "
            "with historical patterns and related business metrics. "
            "Determine whether it reflects a data issue or a genuine "
            "business event before changing the analysis."
        )
        implication = (
            "The unusual pattern may materially affect summary metrics "
            "and should be understood before drawing conclusions."
        )
        recommendation_title = "Investigate unusual sales patterns"

    elif _contains_any(text, ["profit", "margin", "cost", "discount"]):
        action = (
            "Review the available revenue, cost, margin and discount "
            "metrics together. Compare results across relevant segments "
            "before making pricing or cost-management decisions."
        )
        implication = (
            "The finding may affect financial performance, but its "
            "commercial impact depends on the measures available."
        )
        recommendation_title = "Review financial performance drivers"

    else:
        action = (
            "Track the identified metric over time, compare it with "
            "relevant segments and investigate material changes. "
            "Use additional business context before committing to "
            "a major operational decision."
        )
        implication = (
            "The observed pattern may be useful for business planning "
            "and requires context-specific interpretation."
        )
        recommendation_title = "Investigate observed sales pattern"

    return _make_recommendation(
        insight,
        index,
        "General",
        recommendation_title,
        implication,
        action,
    )


# ============================================================
# SINGLE INSIGHT -> RECOMMENDATION
# ============================================================

def generate_recommendation(
    insight: Dict[str, Any],
    index: int = 1,
) -> Optional[Recommendation]:
    """
    Generate one recommendation from one structured insight.

    Returns None when the input is invalid, the statement is missing,
    or the insight has no supporting evidence.
    """
    if not isinstance(insight, dict):
        return None

    statement = _get_insight_statement(insight)
    evidence = _get_insight_evidence(insight)

    if not statement or not evidence:
        return None

    insight_type = _get_insight_type(insight)
    title = _get_insight_title(insight)
    text = f"{insight_type} {title} {statement}".lower()

    # Route to the most specific relevant category first.
    if "forecast" in text:
        result = _forecast_recommendation(insight, index)
        if result is not None:
            return result

    if "product" in insight_type or "categor" in insight_type:
        result = _product_recommendation(insight, index)
        if result is not None:
            return result

    if "customer" in insight_type:
        result = _customer_recommendation(insight, index)
        if result is not None:
            return result

    if any(word in insight_type for word in ("regional", "region", "geograph")):
        result = _regional_recommendation(insight, index)
        if result is not None:
            return result

    return _general_recommendation(insight, index)


# ============================================================
# MULTIPLE INSIGHTS -> RECOMMENDATIONS
# ============================================================

def generate_all_recommendations(
    insights: List[Dict[str, Any]],
) -> List[Recommendation]:
    """
    Generate recommendations from a list of insights.

    Duplicate detection uses category, title, action and insight text.
    The first occurrence is retained to preserve stable output order.
    """
    if not isinstance(insights, list):
        return []

    recommendations: List[Recommendation] = []
    seen = set()

    for source_index, insight in enumerate(insights, start=1):
        recommendation = generate_recommendation(
            insight=insight,
            index=source_index,
        )

        if recommendation is None:
            continue

        deduplication_key = (
            recommendation.recommendation_type.lower(),
            _normalise_for_deduplication(recommendation.title),
            _normalise_for_deduplication(recommendation.recommendation),
            _normalise_for_deduplication(recommendation.insight),
        )

        if deduplication_key in seen:
            continue

        seen.add(deduplication_key)
        recommendations.append(recommendation)

    # Renumber sequentially after duplicate removal.
    category_counts: Dict[str, int] = {}

    for recommendation in recommendations:
        category = recommendation.recommendation_type.upper()
        category_counts[category] = category_counts.get(category, 0) + 1

        recommendation.recommendation_id = (
            f"REC-{category}-{category_counts[category]:03d}"
        )

    return recommendations


# ============================================================
# RECOMMENDATION VALIDATION
# ============================================================

def validate_recommendations(
    recommendations: List[Recommendation],
) -> Dict[str, Any]:
    """
    Validate generated recommendations before they are used
    by the Recommendation Agent.
    """
    errors: List[str] = []
    checked = 0

    if not isinstance(recommendations, list):
        return {
            "overall_status": "FAILED",
            "total_recommendations": 0,
            "passed": 0,
            "failed": 1,
            "errors": ["Recommendations must be provided as a list."],
        }

    for index, item in enumerate(recommendations, start=1):
        checked += 1

        if not isinstance(item, Recommendation):
            errors.append(
                f"Item {index} is not a Recommendation instance."
            )
            continue

        if not item.recommendation_id:
            errors.append(f"Item {index} has no recommendation ID.")

        if not item.recommendation_type:
            errors.append(f"Item {index} has no recommendation type.")

        if not item.title or not item.title.strip():
            errors.append(f"Item {index} has no title.")

        if not isinstance(item.evidence, dict) or not item.evidence:
            errors.append(
                f"{item.recommendation_id}: missing supporting evidence."
            )

        if not item.insight or not item.insight.strip():
            errors.append(
                f"{item.recommendation_id}: missing source insight."
            )

        if not item.recommendation or not item.recommendation.strip():
            errors.append(
                f"{item.recommendation_id}: missing action."
            )

        if not item.business_implication or not item.business_implication.strip():
            errors.append(
                f"{item.recommendation_id}: missing business implication."
            )

        if not item.limitations:
            errors.append(
                f"{item.recommendation_id}: missing limitations."
            )

        if item.priority not in {"HIGH", "MEDIUM", "LOW"}:
            errors.append(
                f"{item.recommendation_id}: invalid priority."
            )

        if not 0.0 <= item.confidence <= 1.0:
            errors.append(
                f"{item.recommendation_id}: confidence must be between 0 and 1."
            )

    passed = checked - len(errors)

    overall_status = "PASSED" if not errors else "FAILED"

    # Update individual statuses only when the entire batch is valid.
    for item in recommendations:
        if isinstance(item, Recommendation):
            item.validation_status = overall_status

    
    return {
    "overall_status": overall_status,
    "total_checks": checked,
    "passed": passed if not errors else 0,
    "failed": len(errors),
    "total_recommendations": len(recommendations),
    "errors": errors,
}


# ============================================================
# RECOMMENDATION SERIALIZATION
# ============================================================

def serialize_recommendations(
    recommendations: List[Recommendation],
) -> List[Dict[str, Any]]:
    """Convert recommendations into dictionaries for agent output."""
    if not isinstance(recommendations, list):
        return []

    return [
        item.to_dict()
        for item in recommendations
        if isinstance(item, Recommendation)
    ]
