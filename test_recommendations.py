
from analytics.recommendations import generate_all_recommendations


insights = [
    {
        "insight_type": "product",
        "title": "Declining product sales",
        "statement": "Product A sales declined during the observed period.",
        "evidence": {
            "product": "Product A",
            "change_percent": -15.0,
        },
        "confidence": 0.92,
    },
    {
        # Exact duplicate of the first insight
        "insight_type": "product",
        "title": "Declining product sales",
        "statement": "Product A sales declined during the observed period.",
        "evidence": {
            "product": "Product A",
            "change_percent": -15.0,
        },
        "confidence": 0.92,
    },
    {
        "insight_type": "regional",
        "title": "Regional performance",
        "statement": "The West region recorded the highest sales.",
        "evidence": {
            "region": "West",
            "sales": 125000,
        },
        "confidence": 0.88,
    },
]


recommendations = generate_all_recommendations(insights)

print(f"Input insights: {len(insights)}")
print(f"Recommendations generated: {len(recommendations)}")

for recommendation in recommendations:
    print(
        recommendation.recommendation_id,
        "|",
        recommendation.recommendation_type,
        "|",
        recommendation.title,
    )

# The duplicate product recommendation should be removed.
assert len(insights) == 3
assert len(recommendations) == 2

assert recommendations[0].recommendation_type == "Product"
assert recommendations[1].recommendation_type == "Regional"

print("\nPASS: Duplicate recommendation test passed.")
