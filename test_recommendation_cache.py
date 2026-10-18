
import json

import pandas as pd
import analytics.recommendation_cache as cache_module

from analytics.recommendation_cache import (
    RecommendationCache,
    make_recommendation_cache_key,
)
from agents.recommendation_agent import (
    RecommendationAgent,
    RecommendationAgentResult,
    MODEL,
    PROMPT_VERSION,
)



from copy import deepcopy

from analytics.recommendation_cache import is_cacheable_result


def test_incomplete_recommendation_results_are_not_cacheable():
    valid_result = {
        "status": "completed",
        "recommendations": [{
            "title": "Review sales",
            "evidence": {"source": "Sales data"},
            "limitations": ["Limited dataset"],
            "recommendation": "Review sales performance.",
            "validation_status": "PASSED",
        }],
        "total_recommendations": 1,
        "recommendation_validation": {
            "overall_status": "PASSED"
        },
        "evidence_sources": ["Insight Agent"],
        "decision_trace": [],
        "warnings": [],
        "errors": [],
    }

    assert is_cacheable_result(valid_result) is True

    # Each mutation makes the result unsuitable for caching.
    mutations = []

    failed_with_errors = deepcopy(valid_result)
    failed_with_errors["errors"] = ["Generation warning treated as an error"]
    mutations.append(failed_with_errors)

    missing_count = deepcopy(valid_result)
    missing_count["total_recommendations"] = 0
    mutations.append(missing_count)

    empty_recommendations = deepcopy(valid_result)
    empty_recommendations["recommendations"] = []
    empty_recommendations["total_recommendations"] = 0
    mutations.append(empty_recommendations)

    missing_evidence = deepcopy(valid_result)
    missing_evidence["recommendations"][0]["evidence"] = {}
    mutations.append(missing_evidence)

    missing_limitations = deepcopy(valid_result)
    missing_limitations["recommendations"][0]["limitations"] = []
    mutations.append(missing_limitations)

    blank_action = deepcopy(valid_result)
    blank_action["recommendations"][0]["recommendation"] = "  "
    mutations.append(blank_action)

    failed_item_validation = deepcopy(valid_result)
    failed_item_validation["recommendations"][0]["validation_status"] = "FAILED"
    mutations.append(failed_item_validation)

    for invalid_result in mutations:
        assert is_cacheable_result(invalid_result) is False


def test_cache_round_trip_and_dataset_identity(tmp_path):
    db_path = tmp_path / "recommendations.sqlite3"
    cache = RecommendationCache(db_path)

    df = pd.DataFrame({
        "Product": ["A", "B"],
        "Sales": [100, 200],
    })
    insights = [{"insight": "Product B has higher sales"}]
    insight_validation = {"overall_status": "PASSED"}
    forecast_result = {"status": "not_available"}

    key = make_recommendation_cache_key(
        df=df,
        insights=insights,
        insight_validation=insight_validation,
        forecast_result=forecast_result,
    )

    result = {
        "status": "completed",
        "recommendations": [{
            "title": "Review product performance",
            "evidence": {"source": "Product B has higher sales"},
            "limitations": ["Based on the supplied dataset"],
            "recommendation": "Review the sales performance of Product B.",
            "validation_status": "PASSED",
        }],
        "total_recommendations": 1,
        "recommendation_validation": {"overall_status": "PASSED"},
        "evidence_sources": ["Insight Agent"],
        "decision_trace": ["Validation passed"],
        "warnings": [],
        "errors": [],
    }

    assert cache.get(key) is None
    assert cache.put(key, result) is True
    assert cache.get(key) == json.loads(json.dumps(result))

    changed_df = df.copy()
    changed_df.loc[0, "Sales"] = 150

    changed_key = make_recommendation_cache_key(
        df=changed_df,
        insights=insights,
        insight_validation=insight_validation,
        forecast_result=forecast_result,
    )

    assert changed_key != key
    assert cache.get(changed_key) is None


def test_failed_result_is_not_cached(tmp_path):
    cache = RecommendationCache(tmp_path / "recommendations.sqlite3")

    failed_result = {
        "status": "failed",
        "recommendations": [],
        "recommendation_validation": {"overall_status": "FAILED"},
    }

    assert cache.put("failed-result-key", failed_result) is False
    assert cache.get("failed-result-key") is None


def test_recommendation_agent_uses_persistent_cache(
    tmp_path, monkeypatch
):
    db_path = tmp_path / "recommendations.sqlite3"
    cache = RecommendationCache(db_path)

    df = pd.DataFrame({
        "Product": ["A", "B"],
        "Sales": [100, 200],
    })
    insights = [{"insight": "Product B has higher sales"}]
    insight_validation = {"overall_status": "PASSED"}
    forecast_result = {"status": "not_available"}

    generation_calls = {"count": 0}

    recommendation_data = [{
    "title": "Review product performance",
    "evidence": {"source": "Product B has higher sales"},
    "limitations": ["Based on the supplied dataset"],
    "recommendation": "Review the sales performance of Product B.",
    "validation_status": "PASSED",
    }]

    def make_agent():
        agent = RecommendationAgent(
            insights=insights,
            insight_validation=insight_validation,
            forecast_result=forecast_result,
            analysis_df=df,
            cache=cache,
        )

        # Isolate cache integration from recommendation-generation
        # logic, which is covered by the existing agent tests.
        monkeypatch.setattr(
            agent, "check_preconditions", lambda: True
        )
        monkeypatch.setattr(
            agent, "identify_evidence_sources", lambda: None
        )
        monkeypatch.setattr(
            agent, "determine_recommendation_scope", lambda: None
        )

        def generate():
            generation_calls["count"] += 1

        monkeypatch.setattr(
            agent, "generate_recommendations", generate
        )
        monkeypatch.setattr(
            agent, "validate",
            lambda: {"overall_status": "PASSED"},
        )
        monkeypatch.setattr(
            agent, "safety_check", lambda: True
        )

        def build_result():
            return RecommendationAgentResult(
                status=agent.status,
                recommendations=recommendation_data,
                total_recommendations=len(recommendation_data),
                recommendation_validation={
                    "overall_status": "PASSED"
                },
                evidence_sources=["Insight Agent"],
                decision_trace=list(agent.decision_trace),
                warnings=list(agent.warnings),
                errors=list(agent.errors),
            )

        monkeypatch.setattr(agent, "_build_result", build_result)
        return agent

    # First run: generate and persist the result.
    first_result = make_agent().run()

    assert first_result.status == "completed"
    assert generation_calls["count"] == 1

    # Confirm a completed result was persisted under the expected key.
    key = make_recommendation_cache_key(
        df=df,
        insights=insights,
        insight_validation=insight_validation,
        forecast_result=forecast_result,
        model=MODEL,
        prompt_version=PROMPT_VERSION,
    )
    assert cache.get(key) is not None

    # Second run: retrieve the same result without generating again.
    second_result = make_agent().run()

    assert second_result.status == "completed"
    assert generation_calls["count"] == 1

    assert (
        second_result.recommendations
        == first_result.recommendations
    )
    assert (
        second_result.recommendation_validation
        == first_result.recommendation_validation
    )
    assert (
        second_result.evidence_sources
        == first_result.evidence_sources
    )
#    print("SECOND RESULT TRACE:", second_result.decision_trace)
#    print("AGENT SOURCE:", __import__("inspect").getsourcefile(RecommendationAgent))
    assert any(
        "loaded from SQLite cache" in item
        for item in second_result.decision_trace
    )

    
def test_cache_persists_across_independent_instances(tmp_path):
    db_path = tmp_path / "persistent_recommendations.sqlite3"

    first_cache = RecommendationCache(db_path)

    key = "independent-instance-persistence-test"

    result = {
        "status": "completed",
        "recommendations": [{
            "title": "Review sales performance",
            "evidence": {"source": "Sales increased in the observed period"},
            "limitations": ["Based on the supplied dataset"],
            "recommendation": "Review the sales trend before changing stock levels.",
            "validation_status": "PASSED",
        }],
        "total_recommendations": 1,
        "recommendation_validation": {
            "overall_status": "PASSED"
        },
        "evidence_sources": ["Insight Agent"],
        "decision_trace": ["Recommendation validation: PASSED"],
        "warnings": [],
        "errors": [],
    }

    # Write using the first cache instance.
    assert first_cache.put(key, result) is True
    assert first_cache.get(key) == result

    # Create an independent instance pointing to the same SQLite file.
    second_cache = RecommendationCache(db_path)

    # The second instance must retrieve the result from disk.
    assert second_cache.get(key) == result


def test_cache_key_changes_when_inputs_or_versions_change():
    df = pd.DataFrame({
        "Product": ["A", "B"],
        "Sales": [100, 200],
    })

    insights = [{"insight": "Product B has higher sales"}]
    insight_validation = {"overall_status": "PASSED"}
    forecast_result = {"status": "not_available"}

    base = make_recommendation_cache_key(
        df=df,
        insights=insights,
        insight_validation=insight_validation,
        forecast_result=forecast_result,
        model="deterministic",
        prompt_version="rules-v1",
        analysis_config={"mode": "standard"},
    )

    # Changing the dataset must change the key.
    changed_df = df.copy()
    changed_df.loc[0, "Sales"] = 101

    assert make_recommendation_cache_key(
        df=changed_df,
        insights=insights,
        insight_validation=insight_validation,
        forecast_result=forecast_result,
        model="deterministic",
        prompt_version="rules-v1",
        analysis_config={"mode": "standard"},
    ) != base

    # Changing the insights must change the key.
    assert make_recommendation_cache_key(
        df=df,
        insights=[{"insight": "Different insight"}],
        insight_validation=insight_validation,
        forecast_result=forecast_result,
        model="deterministic",
        prompt_version="rules-v1",
        analysis_config={"mode": "standard"},
    ) != base

    # Changing validation or forecast inputs must change the key.
    assert make_recommendation_cache_key(
        df=df,
        insights=insights,
        insight_validation={"overall_status": "FAILED"},
        forecast_result=forecast_result,
        model="deterministic",
        prompt_version="rules-v1",
        analysis_config={"mode": "standard"},
    ) != base

    assert make_recommendation_cache_key(
        df=df,
        insights=insights,
        insight_validation=insight_validation,
        forecast_result={"status": "available"},
        model="deterministic",
        prompt_version="rules-v1",
        analysis_config={"mode": "standard"},
    ) != base

    # Changing the model, prompt version or analysis configuration
    # must also change the key.
    for overrides in (
        {"model": "groq-model-example"},
        {"prompt_version": "rules-v2"},
        {"analysis_config": {"mode": "strict"}},
    ):
        arguments = {
            "df": df,
            "insights": insights,
            "insight_validation": insight_validation,
            "forecast_result": forecast_result,
            "model": "deterministic",
            "prompt_version": "rules-v1",
            "analysis_config": {"mode": "standard"},
        }
        arguments.update(overrides)

        assert make_recommendation_cache_key(
            **arguments
        ) != base


def test_old_cache_version_is_rejected(tmp_path, monkeypatch):
    db_path = tmp_path / "versioned_recommendations.sqlite3"
    cache = RecommendationCache(db_path)

    key = "version-invalidation-test"

    valid_result = {
        "status": "completed",
        "recommendations": [{
            "title": "Review sales",
            "evidence": {"source": "Sales data"},
            "limitations": ["Limited dataset"],
            "recommendation": "Review sales performance.",
            "validation_status": "PASSED",
        }],
        "total_recommendations": 1,
        "recommendation_validation": {
            "overall_status": "PASSED"
        },
        "evidence_sources": ["Insight Agent"],
        "decision_trace": [],
        "warnings": [],
        "errors": [],
    }

    # Store using the currently configured cache version.
    assert cache.put(key, valid_result) is True
    assert cache.get(key) == valid_result

    # Simulate an application upgrade.
    monkeypatch.setattr(
        cache_module,
        "CACHE_VERSION",
        "recommendation-cache-test-v2",
    )

    # An entry written under the old version must not be reused.
    assert cache.get(key) is None
