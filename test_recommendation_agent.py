"""
8.7.5 Recommendation Agent Test
================================

Tests:

1. Dataset-independent agent input
2. Validated insight gate
3. Evidence identification
4. Bounded recommendation scope
5. Recommendation generation
6. Recommendation validation
7. Safety checks
8. Decision trace
9. Serialization
10. Convenience function
11. Failed validation gate
"""

from agents.recommendation_agent import (
    RecommendationAgent,
    run_recommendation_agent,
)


# =====================================================================
# TEST INSIGHTS
# =====================================================================

def create_test_insights():
    """
    Create representative validated insights.
    """

    return [
        {
            "insight_type": "sales_performance",
            "title": "Sales Performance",
            "statement": (
                "Total sales for the analysed dataset are "
                "476160.0."
            ),
            "evidence": {
                "total_sales": 476160.0,
                "metric": "total_sales",
            },
            "metric": "total_sales",
            "value": 476160.0,
            "comparison": None,
            "significance": "high",
            "confidence": 0.95,
            "limitations": [
                "Sales performance alone does not establish "
                "business causality."
            ],
        },
        {
            "insight_type": "product_performance",
            "title": "Top Product Category",
            "statement": (
                "Electronics generated the highest sales among "
                "the available product categories."
            ),
            "evidence": {
                "product_category": "Electronics",
                "sales": 166955.0,
                "metric": "product_sales",
            },
            "metric": "product_sales",
            "value": 166955.0,
            "comparison": "highest",
            "significance": "high",
            "confidence": 0.95,
            "limitations": [
                "Product sales do not establish the exact "
                "business cause."
            ],
        },
        {
            "insight_type": "regional_performance",
            "title": "Top Region",
            "statement": (
                "San Francisco generated the highest regional "
                "sales in the dataset."
            ),
            "evidence": {
                "city": "San Francisco",
                "sales": 71335.0,
                "metric": "regional_sales",
            },
            "metric": "regional_sales",
            "value": 71335.0,
            "comparison": "highest",
            "significance": "high",
            "confidence": 0.95,
            "limitations": [
                "Regional sales do not establish the exact "
                "business cause."
            ],
        },
        {
            "insight_type": "customer_concentration",
            "title": "Customer Sales Concentration",
            "statement": (
                "A small group of customers contributes a "
                "relatively important share of observed sales."
            ),
            "evidence": {
                "top_customer": "CUST015",
                "top_customer_sales": 5000.0,
                "metric": "customer_sales",
            },
            "metric": "customer_sales",
            "value": 5000.0,
            "comparison": "top customers",
            "significance": "medium",
            "confidence": 0.90,
            "limitations": [
                "Customer concentration does not establish "
                "future customer retention."
            ],
        },
        {
            "insight_type": "forecast_performance",
            "title": "Forecast Outlook",
            "statement": (
                "The forecast indicates a potential increase "
                "in future sales."
            ),
            "evidence": {
                "model": "Exponential Smoothing",
                "mae": 786.8074,
                "horizon": 7,
            },
            "metric": "forecast",
            "value": 786.8074,
            "comparison": "future outlook",
            "significance": "medium",
            "confidence": 0.85,
            "limitations": [
                "Forecast values are estimates rather than "
                "guarantees."
            ],
        },
    ]


# =====================================================================
# VALIDATION RESULT
# =====================================================================

def create_validated_insight_result():
    """
    Simulate the validated output of the Insight Agent.
    """

    return {
        "overall_status": "PASSED",
        "total_checks": 12,
        "passed": 12,
        "failed": 0,
        "warnings": 0,
    }


# =====================================================================
# MAIN TEST
# =====================================================================

def main():

    print()
    print("=" * 70)
    print("8.7.5 RECOMMENDATION AGENT TEST")
    print("=" * 70)

    # ---------------------------------------------------------------
    # 1. Prepare inputs
    # ---------------------------------------------------------------

    insights = create_test_insights()

    insight_validation = (
        create_validated_insight_result()
    )

    print()
    print("INPUT PREPARATION")
    print(
        f"Total Insights: {len(insights)}"
    )

    assert len(insights) > 0

    print("Insight Input: PASSED")

    # ---------------------------------------------------------------
    # 2. Create agent
    # ---------------------------------------------------------------

    agent = RecommendationAgent(
        insights=insights,
        insight_validation=insight_validation,
        forecast_result={
            "status": "completed",
            "best_model": "Exponential Smoothing",
            "best_mae": 786.8074,
        },
    )

    assert agent is not None

    print("Recommendation Agent Creation: PASSED")

    # ---------------------------------------------------------------
    # 3. Test preconditions
    # ---------------------------------------------------------------

    preconditions = (
        agent.check_preconditions()
    )

    assert preconditions is True

    print("Preconditions: PASSED")

    # ---------------------------------------------------------------
    # 4. Test evidence identification
    # ---------------------------------------------------------------

    evidence_sources = (
        agent.identify_evidence_sources()
    )

    print()
    print(
        "EVIDENCE SOURCES"
    )

    print(
        evidence_sources
    )

    assert (
        "validated_kpis"
        in evidence_sources
    )

    assert (
        "validated_rankings"
        in evidence_sources
    )

    assert (
        "validated_forecasting"
        in evidence_sources
    )

    print("Evidence Identification: PASSED")

    # ---------------------------------------------------------------
    # 5. Test bounded recommendation scope
    # ---------------------------------------------------------------

    scope = (
        agent.determine_recommendation_scope()
    )

    print()
    print(
        "RECOMMENDATION SCOPE"
    )

    print(scope)

    assert "Product" in scope
    assert "Customer" in scope
    assert "Regional" in scope
    assert "Forecast" in scope

    print("Bounded Recommendation Scope: PASSED")

    # ---------------------------------------------------------------
    # 6. Generate recommendations
    # ---------------------------------------------------------------

    recommendations = (
        agent.generate_recommendations()
    )

    print()
    print(
        "GENERATED RECOMMENDATIONS"
    )

    print(
        f"Total Recommendations: "
        f"{len(recommendations)}"
    )

    assert len(
        recommendations
    ) > 0

    print("Recommendation Generation: PASSED")

    # ---------------------------------------------------------------
    # 7. Display recommendations
    # ---------------------------------------------------------------

    for recommendation in recommendations:

        print()
        print(
            f"ID         : "
            f"{recommendation.recommendation_id}"
        )

        print(
            f"Type       : "
            f"{recommendation.recommendation_type}"
        )

        print(
            f"Priority   : "
            f"{recommendation.priority}"
        )

        print(
            f"Confidence : "
            f"{recommendation.confidence}"
        )

        print(
            f"Action     : "
            f"{recommendation.recommendation}"
        )

    # ---------------------------------------------------------------
    # 8. Validate recommendations
    # ---------------------------------------------------------------

    validation = (
        agent.validate()
    )

    print()
    print(
        "RECOMMENDATION VALIDATION"
    )

    print(
        f"Overall Status: "
        f"{validation['overall_status']}"
    )

    print(
        f"Total Checks: "
        f"{validation['total_checks']}"
    )

    print(
        f"Passed: "
        f"{validation['passed']}"
    )

    print(
        f"Failed: "
        f"{validation['failed']}"
    )

    assert (
        validation[
            "overall_status"
        ]
        == "PASSED"
    )

    assert (
        validation[
            "failed"
        ]
        == 0
    )

    print(
        "Recommendation Validation: PASSED"
    )

    # ---------------------------------------------------------------
    # 9. Safety check
    # ---------------------------------------------------------------

    safety = (
        agent.safety_check()
    )

    assert safety is True

    print(
        "Recommendation Safety Check: PASSED"
    )

    # ---------------------------------------------------------------
    # 10. Run complete agent
    # ---------------------------------------------------------------

    result = agent.run()

    print()
    print(
        "AGENT RESULT"
    )

    print(
        f"Agent Status: "
        f"{result.status}"
    )

    print(
        f"Total Recommendations: "
        f"{result.total_recommendations}"
    )

    assert (
        result.status
        == "completed"
    )

    assert (
        result.total_recommendations
        > 0
    )

    print(
        "Recommendation Agent Execution: PASSED"
    )

    # ---------------------------------------------------------------
    # 11. Check evidence sources
    # ---------------------------------------------------------------

    assert (
        "validated_rankings"
        in result.evidence_sources
    )

    assert (
        "validated_forecasting"
        in result.evidence_sources
    )

    print(
        "Evidence Source Integration: PASSED"
    )

    # ---------------------------------------------------------------
    # 12. Check recommendation categories
    # ---------------------------------------------------------------

    categories = {
        recommendation[
            "recommendation_type"
        ]
        for recommendation
        in result.recommendations
    }

    print()
    print(
        "RECOMMENDATION CATEGORIES"
    )

    print(
        sorted(categories)
    )

    assert "Product" in categories
    assert "Customer" in categories
    assert "Regional" in categories
    assert "Forecast" in categories

    print(
        "Recommendation Category Coverage: PASSED"
    )

    # ---------------------------------------------------------------
    # 13. Evidence and limitation safety
    # ---------------------------------------------------------------

    for recommendation in result.recommendations:

        assert recommendation[
            "evidence"
        ]

        assert recommendation[
            "limitations"
        ]

        assert recommendation[
            "recommendation"
        ]

    print(
        "Evidence and Limitation Safety: PASSED"
    )

    # ---------------------------------------------------------------
    # 14. Decision trace
    # ---------------------------------------------------------------

    assert len(
        result.decision_trace
    ) > 0

    print()
    print(
        "DECISION TRACE"
    )

    for number, decision in enumerate(
        result.decision_trace,
        start=1,
    ):

        print(
            f"{number}. {decision}"
        )

    assert any(
        "preconditions"
        in decision.lower()
        for decision
        in result.decision_trace
    )

    assert any(
        "evidence"
        in decision.lower()
        for decision
        in result.decision_trace
    )

    assert any(
        "validation"
        in decision.lower()
        for decision
        in result.decision_trace
    )

    print(
        "Decision Trace: PASSED"
    )

    # ---------------------------------------------------------------
    # 15. Error check
    # ---------------------------------------------------------------

    assert result.errors == []

    print(
        "Agent Errors: NONE"
    )

    # ---------------------------------------------------------------
    # 16. Serialization
    # ---------------------------------------------------------------

    serialized = (
        result.to_dict()
    )

    assert isinstance(
        serialized,
        dict,
    )

    assert (
        serialized[
            "status"
        ]
        == "completed"
    )

    assert (
        "recommendations"
        in serialized
    )

    assert (
        "recommendation_validation"
        in serialized
    )

    assert (
        "decision_trace"
        in serialized
    )

    print(
        "Serialization: PASSED"
    )

    # ---------------------------------------------------------------
    # 17. Failed insight validation gate
    # ---------------------------------------------------------------

    failed_agent = RecommendationAgent(
        insights=insights,
        insight_validation={
            "overall_status": "FAILED",
            "total_checks": 12,
            "passed": 10,
            "failed": 2,
        },
    )

    failed_result = (
        failed_agent.run()
    )

    assert (
        failed_result.status
        == "blocked"
    )

    assert (
        failed_result.total_recommendations
        == 0
    )

    assert len(
        failed_result.errors
    ) > 0

    print(
        "Failed Insight Validation Gate: PASSED"
    )

    # ---------------------------------------------------------------
    # 18. Convenience function
    # ---------------------------------------------------------------

    convenience_result = (
        run_recommendation_agent(
            insights=insights,
            insight_validation=(
                insight_validation
            ),
            forecast_result={
                "status": "completed",
                "best_model": "Exponential Smoothing",
                "best_mae": 786.8074,
            },
        )
    )

    assert (
        convenience_result.status
        == "completed"
    )

    assert (
        convenience_result.total_recommendations
        > 0
    )

    print(
        "Convenience Function: PASSED"
    )

    # ---------------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "8.7.5 RECOMMENDATION AGENT TEST: PASSED"
    )
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()