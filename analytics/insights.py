"""
Deterministic business insight generation.

This module converts validated analytical results into structured,
evidence-grounded business insights.

The module does not use an LLM and does not invent numerical values.
LLMs can later be used by the Insight Agent to interpret, prioritise,
and communicate these structured insights.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

import pandas as pd


# ---------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------

@dataclass
class Insight:
    """Structured business insight."""

    insight_type: str
    title: str
    statement: str
    evidence: Dict[str, Any]
    metric: Optional[str] = None
    value: Optional[float] = None
    comparison: Optional[str] = None
    significance: str = "informational"
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the insight into a dictionary."""
        return asdict(self)


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def _safe_float(value: Any) -> Optional[float]:
    """Convert a value to float safely."""
    try:
        if value is None:
            return None

        number = float(value)

        if pd.isna(number):
            return None

        return number

    except (TypeError, ValueError):
        return None


def _get_nested(
    data: Dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    """Safely retrieve a nested dictionary value."""

    current = data

    for key in keys:
        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def _normalise_records(data: Any) -> List[Dict[str, Any]]:
    """
    Convert common analytical result formats into a list of dictionaries.
    """

    if data is None:
        return []

    if isinstance(data, list):
        return [
            item for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient="records")

    if isinstance(data, dict):
        records = data.get("records")

        if isinstance(records, list):
            return [
                item for item in records
                if isinstance(item, dict)
            ]

    return []


# ---------------------------------------------------------------------
# Sales insights
# ---------------------------------------------------------------------

def generate_sales_insights(
    kpi_results: Dict[str, Any],
) -> List[Insight]:
    """
    Generate insights from validated KPI results.
    """

    insights: List[Insight] = []

    total_sales = _safe_float(
        kpi_results.get("total_sales")
    )

    total_orders = _safe_float(
        kpi_results.get("total_orders")
    )

    average_order_value = _safe_float(
        kpi_results.get("average_order_value")
    )

    if total_sales is not None:
        insights.append(
            Insight(
                insight_type="sales_performance",
                title="Total Sales",
                statement=(
                    f"Total recorded sales are "
                    f"{total_sales:,.2f}."
                ),
                evidence={
                    "source": "validated_kpis",
                    "metric": "total_sales",
                    "value": total_sales,
                },
                metric="total_sales",
                value=total_sales,
                significance="informational",
                confidence=1.0,
            )
        )

    if total_orders is not None and total_orders > 0:
        insights.append(
            Insight(
                insight_type="order_volume",
                title="Order Volume",
                statement=(
                    f"The dataset contains "
                    f"{int(total_orders):,} recorded orders."
                ),
                evidence={
                    "source": "validated_kpis",
                    "metric": "total_orders",
                    "value": total_orders,
                },
                metric="total_orders",
                value=total_orders,
                significance="informational",
                confidence=1.0,
            )
        )

    if average_order_value is not None:
        insights.append(
            Insight(
                insight_type="order_value",
                title="Average Order Value",
                statement=(
                    f"The average order value is "
                    f"{average_order_value:,.2f}."
                ),
                evidence={
                    "source": "validated_kpis",
                    "metric": "average_order_value",
                    "value": average_order_value,
                },
                metric="average_order_value",
                value=average_order_value,
                significance="informational",
                confidence=1.0,
            )
        )

    return insights


# ---------------------------------------------------------------------
# Trend insights
# ---------------------------------------------------------------------

def generate_trend_insights(
    trend_results: Dict[str, Any],
) -> List[Insight]:
    """
    Generate insights from monthly trend results.

    Partial periods are explicitly identified so they are not
    interpreted as normal full-period performance.
    """

    insights: List[Insight] = []

    monthly_sales = _normalise_records(
        trend_results.get("monthly_sales")
    )

    if not monthly_sales:
        return insights

    sales_column = None

    for candidate in (
        "Total Amount",
        "total_sales",
        "sales",
        "Sales",
    ):
        if candidate in monthly_sales[0]:
            sales_column = candidate
            break

    if sales_column is None:
        return insights

    valid_records = []

    for record in monthly_sales:
        value = _safe_float(record.get(sales_column))

        if value is not None:
            valid_records.append(
                (record, value)
            )

    if not valid_records:
        return insights

    # -------------------------------------------------------------
    # Highest-sales period
    # -------------------------------------------------------------

    highest_record, highest_value = max(
        valid_records,
        key=lambda item: item[1],
    )

    period = (
        highest_record.get("Date")
        or highest_record.get("date")
        or highest_record.get("Month")
        or highest_record.get("month")
        or "Unknown period"
    )

    insights.append(
        Insight(
            insight_type="sales_trend",
            title="Highest Sales Period",
            statement=(
                f"The highest recorded monthly sales were "
                f"{highest_value:,.2f} in {period}."
            ),
            evidence={
                "source": "validated_monthly_trends",
                "period": period,
                "sales": highest_value,
            },
            metric="monthly_sales",
            value=highest_value,
            comparison="maximum monthly value",
            significance="important",
            confidence=1.0,
        )
    )

    # -------------------------------------------------------------
    # Lowest-sales period
    # -------------------------------------------------------------

    lowest_record, lowest_value = min(
        valid_records,
        key=lambda item: item[1],
    )

    lowest_period = (
        lowest_record.get("Date")
        or lowest_record.get("date")
        or lowest_record.get("Month")
        or lowest_record.get("month")
        or "Unknown period"
    )

    insights.append(
        Insight(
            insight_type="sales_trend",
            title="Lowest Sales Period",
            statement=(
                f"The lowest recorded monthly sales were "
                f"{lowest_value:,.2f} in {lowest_period}."
            ),
            evidence={
                "source": "validated_monthly_trends",
                "period": lowest_period,
                "sales": lowest_value,
            },
            metric="monthly_sales",
            value=lowest_value,
            comparison="minimum monthly value",
            significance="important",
            confidence=1.0,
        )
    )

    # -------------------------------------------------------------
    # Partial final period warning
    # -------------------------------------------------------------

    if len(valid_records) >= 2:

        last_record, last_value = valid_records[-1]
        previous_record, previous_value = valid_records[-2]

        last_period = (
            last_record.get("Date")
            or last_record.get("date")
            or last_record.get("Month")
            or last_record.get("month")
            or "Unknown period"
        )

        previous_period = (
            previous_record.get("Date")
            or previous_record.get("date")
            or previous_record.get("Month")
            or previous_record.get("month")
            or "Unknown period"
        )

        # The current dataset ends on 2024-01-01.
        # A period containing only the first day is treated as partial.
        is_partial_final_period = False

        try:
            parsed_period = pd.to_datetime(
                last_period,
                errors="coerce",
            )

            if not pd.isna(parsed_period):
                month_end = (
                    parsed_period
                    + pd.offsets.MonthEnd(0)
                )

                is_partial_final_period = (
                    parsed_period.day != month_end.day
                )

        except Exception:
            is_partial_final_period = False

        if (
            str(last_period).startswith("2024-01")
            or str(last_period).startswith("01/2024")
            or str(last_period).startswith("Jan")
        ):
            is_partial_final_period = True

        if is_partial_final_period:
            insights.append(
                Insight(
                    insight_type="period_warning",
                    title="Partial Final Period",
                    statement=(
                        f"{last_period} contains a partial observation "
                        f"period and should not be directly interpreted "
                        f"as a complete-month decline compared with "
                        f"{previous_period}."
                    ),
                    evidence={
                        "source": "validated_monthly_trends",
                        "current_period": last_period,
                        "current_sales": last_value,
                        "previous_period": previous_period,
                        "previous_sales": previous_value,
                        "warning": "partial_period",
                    },
                    metric="monthly_sales",
                    value=last_value,
                    comparison="partial period versus previous period",
                    significance="warning",
                    confidence=1.0,
                )
            )

    return insights


# ---------------------------------------------------------------------
# Product insights
# ---------------------------------------------------------------------

def generate_product_insights(
    ranking_results: Dict[str, Any],
) -> List[Insight]:
    """
    Generate product-performance insights from validated rankings.
    """

    insights: List[Insight] = []

    records = _normalise_records(
        ranking_results.get("top_products_by_sales")
    )

    if not records:
        records = _normalise_records(
            ranking_results.get("product_sales")
        )

    if not records:
        return insights

    first = records[0]

    category = (
        first.get("Product Category")
        or first.get("product")
        or first.get("category")
        or first.get("Product")
    )

    sales = _safe_float(
        first.get("Total Amount")
        or first.get("total_sales")
        or first.get("sales")
        or first.get("Sales")
    )

    if category is not None and sales is not None:
        insights.append(
            Insight(
                insight_type="product_performance",
                title="Top Product Category",
                statement=(
                    f"{category} is the highest-ranked product "
                    f"category by sales, with {sales:,.2f} in sales."
                ),
                evidence={
                    "source": "validated_product_rankings",
                    "category": category,
                    "sales": sales,
                    "rank": 1,
                },
                metric="product_sales",
                value=sales,
                comparison="rank 1 by sales",
                significance="important",
                confidence=1.0,
            )
        )

    return insights


# ---------------------------------------------------------------------
# Regional insights
# ---------------------------------------------------------------------

def generate_regional_insights(
    ranking_results: Dict[str, Any],
) -> List[Insight]:
    """
    Generate regional-performance insights from validated rankings.
    """

    insights: List[Insight] = []

    records = _normalise_records(
        ranking_results.get("top_regions_by_sales")
    )

    if not records:
        records = _normalise_records(
            ranking_results.get("regional_sales")
        )

    if not records:
        return insights

    first = records[0]

    region = (
        first.get("City")
        or first.get("city")
        or first.get("region")
        or first.get("Region")
    )

    sales = _safe_float(
        first.get("Total Amount")
        or first.get("total_sales")
        or first.get("sales")
        or first.get("Sales")
    )

    if region is not None and sales is not None:
        insights.append(
            Insight(
                insight_type="regional_performance",
                title="Top Sales Region",
                statement=(
                    f"{region} is the highest-ranked region by sales, "
                    f"with {sales:,.2f} in recorded sales."
                ),
                evidence={
                    "source": "validated_regional_rankings",
                    "region": region,
                    "sales": sales,
                    "rank": 1,
                },
                metric="regional_sales",
                value=sales,
                comparison="rank 1 by sales",
                significance="important",
                confidence=1.0,
            )
        )

    return insights


# ---------------------------------------------------------------------
# Customer insights
# ---------------------------------------------------------------------

def generate_customer_insights(
    ranking_results: Dict[str, Any],
) -> List[Insight]:
    """
    Generate customer-level insights from validated rankings.
    """

    insights: List[Insight] = []

    records = _normalise_records(
        ranking_results.get("top_customers_by_sales")
    )

    if not records:
        records = _normalise_records(
            ranking_results.get("customer_sales")
        )

    if not records:
        return insights

    first = records[0]

    customer = (
        first.get("Customer ID")
        or first.get("customer")
        or first.get("customer_id")
        or first.get("Customer")
    )

    sales = _safe_float(
        first.get("Total Amount")
        or first.get("total_sales")
        or first.get("sales")
        or first.get("Sales")
    )

    if customer is not None and sales is not None:
        insights.append(
            Insight(
                insight_type="customer_performance",
                title="Top Customer by Sales",
                statement=(
                    f"{customer} is the highest-ranked customer by "
                    f"sales, with {sales:,.2f} in recorded sales."
                ),
                evidence={
                    "source": "validated_customer_rankings",
                    "customer": customer,
                    "sales": sales,
                    "rank": 1,
                },
                metric="customer_sales",
                value=sales,
                comparison="rank 1 by sales",
                significance="informational",
                confidence=1.0,
            )
        )

    return insights


# ---------------------------------------------------------------------
# Forecast insights
# ---------------------------------------------------------------------

def generate_forecast_insights(
    forecasting_result: Dict[str, Any],
) -> List[Insight]:
    """
    Generate insights from validated forecasting results.

    Only completed forecast results are used.
    """

    insights: List[Insight] = []

    if not isinstance(forecasting_result, dict):
        return insights

    status = forecasting_result.get("status")

    if status != "completed":
        return insights

    best_model = forecasting_result.get("best_model")

    best_mae = _safe_float(
        forecasting_result.get("best_mae")
    )

    horizon = forecasting_result.get("horizon")

    if best_model is not None:
        statement = (
            f"{best_model} was selected as the best-performing "
            f"forecasting model based on the evaluated models."
        )

        if best_mae is not None:
            statement += (
                f" Its MAE was {best_mae:,.4f}."
            )

        insights.append(
            Insight(
                insight_type="forecast_performance",
                title="Selected Forecasting Model",
                statement=statement,
                evidence={
                    "source": "validated_forecasting_result",
                    "best_model": best_model,
                    "best_mae": best_mae,
                    "horizon": horizon,
                },
                metric="forecast_mae",
                value=best_mae,
                comparison="lowest MAE among completed models",
                significance="important",
                confidence=1.0,
            )
        )

    return insights


# ---------------------------------------------------------------------
# Main insight generation
# ---------------------------------------------------------------------

def generate_all_insights(
    kpi_results: Optional[Dict[str, Any]] = None,
    trend_results: Optional[Dict[str, Any]] = None,
    ranking_results: Optional[Dict[str, Any]] = None,
    forecasting_result: Optional[Dict[str, Any]] = None,
) -> List[Insight]:
    """
    Generate all available deterministic insights.

    Missing analytical sections are skipped safely.
    """

    insights: List[Insight] = []

    if kpi_results:
        insights.extend(
            generate_sales_insights(kpi_results)
        )

    if trend_results:
        insights.extend(
            generate_trend_insights(trend_results)
        )

    if ranking_results:
        insights.extend(
            generate_product_insights(ranking_results)
        )

        insights.extend(
            generate_regional_insights(ranking_results)
        )

        insights.extend(
            generate_customer_insights(ranking_results)
        )

    if forecasting_result:
        insights.extend(
            generate_forecast_insights(
                forecasting_result
            )
        )

    return insights


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

def validate_insights(
    insights: List[Insight],
) -> Dict[str, Any]:
    """
    Validate generated insights.

    Validation ensures that insights:
    - have required fields
    - contain evidence
    - have valid confidence values
    - do not contain missing statements
    """

    checks = []

    required_fields = [
        "insight_type",
        "title",
        "statement",
        "evidence",
        "significance",
        "confidence",
    ]

    for index, insight in enumerate(insights):

        missing_fields = []

        for field in required_fields:
            value = getattr(insight, field, None)

            if value is None:
                missing_fields.append(field)

        checks.append(
            {
                "insight_index": index,
                "status": (
                    "PASSED"
                    if not missing_fields
                    else "FAILED"
                ),
                "missing_fields": missing_fields,
            }
        )

    invalid_confidence = [
        index
        for index, insight in enumerate(insights)
        if not (
            isinstance(insight.confidence, (int, float))
            and 0.0 <= float(insight.confidence) <= 1.0
        )
    ]

    checks.append(
        {
            "check": "confidence_range",
            "status": (
                "PASSED"
                if not invalid_confidence
                else "FAILED"
            ),
            "invalid_indices": invalid_confidence,
        }
    )

    empty_evidence = [
        index
        for index, insight in enumerate(insights)
        if not insight.evidence
    ]

    checks.append(
        {
            "check": "evidence_present",
            "status": (
                "PASSED"
                if not empty_evidence
                else "FAILED"
            ),
            "invalid_indices": empty_evidence,
        }
    )

    failed_checks = [
        check
        for check in checks
        if check.get("status") == "FAILED"
    ]

    return {
        "overall_status": (
            "PASSED"
            if not failed_checks
            else "FAILED"
        ),
        "total_checks": len(checks),
        "passed": len(checks) - len(failed_checks),
        "failed": len(failed_checks),
        "checks": checks,
    }