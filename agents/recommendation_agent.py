
"""
Groq-powered Recommendation Agent
=================================

Responsibilities:
1. Check insight validation.
2. Identify evidence sources and recommendation scope.
3. Check SQLite for previously generated recommendations.
4. Generate recommendations using the Groq API on a cache miss.
5. Validate recommendations and perform safety checks.
6. Persist only completed, validated results.

Environment variables:
    GROQ_API_KEY
    GROQ_MODEL (optional)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv
from groq import Groq

from analytics.recommendations import (
    Recommendation,
    validate_recommendations,
    serialize_recommendations,
)
from analytics.recommendation_cache import (
    RecommendationCache,
    make_recommendation_cache_key,
)

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
PROMPT_VERSION = "groq-business-recommendations-v1"


# =====================================================================
# RESULT STRUCTURE
# =====================================================================

@dataclass
class RecommendationAgentResult:
    """Structured result returned by the Recommendation Agent."""

    status: str
    recommendations: List[Dict[str, Any]]
    total_recommendations: int
    recommendation_validation: Dict[str, Any]
    evidence_sources: List[str]
    decision_trace: List[str]
    warnings: List[str]
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =====================================================================
# RECOMMENDATION AGENT
# =====================================================================

class RecommendationAgent:
    """Generate, validate and cache Groq-powered recommendations."""

    def __init__(
        self,
        insights: Optional[List[Dict[str, Any]]] = None,
        insight_validation: Optional[Dict[str, Any]] = None,
        forecast_result: Optional[Dict[str, Any]] = None,
        analysis_df: Optional[pd.DataFrame] = None,
        cache: Optional[RecommendationCache] = None,
    ) -> None:
        self.insights = insights or []
        self.insight_validation = insight_validation or {}
        self.forecast_result = forecast_result or {}
        self.analysis_df = analysis_df

        self.cache = (
            cache if cache is not None else RecommendationCache()
        )

        self.recommendations: List[Recommendation] = []
        self.recommendation_validation: Dict[str, Any] = {}
        self.evidence_sources: List[str] = []
        self.decision_trace: List[str] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.status = "initialized"

    # =================================================================
    # CACHE KEY
    # =================================================================

    def _get_cache_key(self) -> Optional[str]:
        """Build a cache key from the dataset and analysis inputs."""

        if self.analysis_df is None:
            return None

        try:
            return make_recommendation_cache_key(
                df=self.analysis_df,
                insights=self.insights,
                insight_validation=self.insight_validation,
                forecast_result=self.forecast_result,
                model=MODEL,
                prompt_version=PROMPT_VERSION,
            )
        except Exception:
            logger.exception("Could not create recommendation cache key.")
            self.warnings.append(
                "Cache key creation failed; recommendations will run without cache."
            )
            return None

    # =================================================================
    # PRECONDITIONS
    # =================================================================

    def check_preconditions(self) -> bool:
        """Check that usable, validated insights are available."""

        self.decision_trace.append(
            "Check Recommendation Agent preconditions."
        )

        if not isinstance(self.insights, list) or not self.insights:
            self.errors.append("No analytical insights were supplied.")
            return False

        if not any(isinstance(item, dict) for item in self.insights):
            self.errors.append(
                "The insights list contains no valid insight objects."
            )
            return False

        if (
            self.insight_validation
            and self.insight_validation.get("overall_status") != "PASSED"
        ):
            self.errors.append("Insight validation did not pass.")
            self.decision_trace.append("Insight validation gate: BLOCKED.")
            return False

        if not self.insight_validation:
            self.warnings.append(
                "Insight validation result was not supplied."
            )

        self.decision_trace.append("Insight preconditions: PASSED.")
        return True

    # =================================================================
    # EVIDENCE IDENTIFICATION
    # =================================================================

    def identify_evidence_sources(self) -> List[str]:
        """Identify the analytical insight types supporting recommendations."""

        sources = set()

        for item in self.insights:
            if not isinstance(item, dict):
                continue

            insight_type = str(
                item.get("insight_type", "")
            ).lower()

            if "sales" in insight_type or "kpi" in insight_type:
                sources.add("validated_kpis")

            if "trend" in insight_type:
                sources.add("validated_trends")

            if (
                "product" in insight_type
                or "regional" in insight_type
                or "region" in insight_type
                or "customer" in insight_type
            ):
                sources.add("validated_rankings")

            if "forecast" in insight_type:
                sources.add("validated_forecasting")

        if self.forecast_result:
            sources.add("validated_forecasting")

        self.evidence_sources = sorted(sources)

        self.decision_trace.append(
            "Evidence sources identified: "
            + (
                ", ".join(self.evidence_sources)
                if self.evidence_sources
                else "No recognised insight types"
            )
        )

        return self.evidence_sources

    # =================================================================
    # RECOMMENDATION SCOPE
    # =================================================================

    def determine_recommendation_scope(self) -> List[str]:
        """Identify recommendation categories supported by the insights."""

        categories = set()

        for item in self.insights:
            if not isinstance(item, dict):
                continue

            insight_type = str(
                item.get("insight_type", "")
            ).lower()

            if "product" in insight_type:
                categories.add("Product")

            if "customer" in insight_type:
                categories.add("Customer")

            if "region" in insight_type:
                categories.add("Regional")

            if "forecast" in insight_type:
                categories.add("Forecast")

            if "sales" in insight_type or "trend" in insight_type:
                categories.add("General")

        result = sorted(categories)

        self.decision_trace.append(
            "Recommendation scope: "
            + (", ".join(result) if result else "Based on supplied insights")
        )

        return result

    # =================================================================
    # GROQ GENERATION
    # =================================================================

    def _generate_with_groq(self) -> List[Recommendation]:
        """Generate structured recommendations using the Groq API."""

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Add it to the project-root .env file."
            )

        # Send analytical findings, not the entire raw CSV.
        compact_insights = []

        for index, insight in enumerate(self.insights):
            if not isinstance(insight, dict):
                continue

            evidence = insight.get("evidence", {})

            compact_insights.append({
                "insight_index": index,
                "insight_type": insight.get("insight_type", "General"),
                "title": insight.get("title", ""),
                "finding": insight.get(
                    "statement",
                    insight.get("insight", ""),
                ),
                "evidence": evidence,
                "confidence": insight.get("confidence", 0),
                "limitations": insight.get("limitations", []),
            })

        if not compact_insights:
            raise ValueError("No usable analytical insights were supplied.")

        prompt = f"""
You are a senior retail and e-commerce sales intelligence analyst.

Generate between 3 and 5 DISTINCT, actionable recommendations from the
validated findings below. Return fewer if the evidence supports fewer.

Requirements:
1. Every recommendation must refer to a supplied insight.
2. Use specific products, regions, customer groups, metrics or periods
   only when they appear in the evidence.
3. Explain the business implication of the finding.
4. Give a concrete action rather than generic advice.
5. Do not repeat recommendations or merely rephrase the same action.
6. Never invent numbers, trends, business causes or expected results.
7. Separate observed facts from hypotheses that require investigation.
8. State meaningful limitations.
9. Use HIGH, MEDIUM or LOW priority.
10. Confidence must be between 0 and 1.
11. insight_index must match an input insight_index.
12. Return valid JSON only.
13. Use these category labels consistently where applicable:
    Product, Customer, Regional, Forecast, General.
14. Use "Regional", not "Region", for regional recommendations.

Required JSON structure:
{{
  "recommendations": [
    {{
      "insight_index": 0,
      "recommendation_type": "Product",
      "title": "Specific and concise title",
      "business_implication": "Why the observed finding matters",
      "recommendation": "A concrete business action",
      "priority": "MEDIUM",
      "confidence": 0.85,
      "limitations": [
        "A meaningful limitation based on available evidence"
      ]
    }}
  ]
}}

Validated insights:
{json.dumps(compact_insights, ensure_ascii=False, default=str)}

Forecast results:
{json.dumps(self.forecast_result, ensure_ascii=False, default=str)}
"""

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate evidence-grounded business "
                        "recommendations. Do not invent evidence. "
                        "Return only the requested JSON object."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Groq returned an empty response.")

        payload = json.loads(content)
        items = payload.get("recommendations")

        if not isinstance(items, list) or not items:
            raise ValueError(
                "Groq did not return a non-empty recommendations list."
            )

        recommendations: List[Recommendation] = []

        # Normalise equivalent category names across all recommendations.
        category_aliases = {
            "region": "Regional",
            "regional": "Regional",
            "product": "Product",
            "customer": "Customer",
            "forecast": "Forecast",
            "general": "General",
        }

        for item in items[:5]:
            if not isinstance(item, dict):
                continue

            try:
                insight_index = int(item["insight_index"])

                source = next(
                    (
                        insight
                        for index, insight in enumerate(self.insights)
                        if index == insight_index
                        and isinstance(insight, dict)
                    ),
                    None,
                )

                if source is None:
                    continue

                statement = str(
                    source.get(
                        "statement",
                        source.get("insight", ""),
                    )
                ).strip()

                evidence = source.get("evidence", {})

                # Preserve actual evidence from the source insight.
                if not isinstance(evidence, dict) or not evidence:
                    continue

                title = str(item.get("title", "")).strip()
                implication = str(
                    item.get("business_implication", "")
                ).strip()
                action = str(item.get("recommendation", "")).strip()

                limitations = item.get("limitations")
                if not isinstance(limitations, list):
                    continue

                limitations = [
                    str(value).strip()
                    for value in limitations
                    if str(value).strip()
                ]

                priority = str(
                    item.get("priority", "MEDIUM")
                ).upper()

                confidence = float(item.get("confidence", 0.0))

                if priority not in {"LOW", "MEDIUM", "HIGH"}:
                    continue

                if not 0.0 <= confidence <= 1.0:
                    continue

                if not all([statement, title, implication, action]):
                    continue

                if not limitations:
                    continue

                # Fix: map "Region" to "Regional" and standardise
                # other known categories without changing unknown labels.
                raw_type = str(
                    item.get("recommendation_type")
                    or source.get("insight_type")
                    or "General"
                ).strip()

                recommendation_type = category_aliases.get(
                    raw_type.casefold(),
                    raw_type,
                )

                recommendations.append(
                    Recommendation(
                        recommendation_id=(
                            f"REC-LLM-{len(recommendations) + 1:03d}"
                        ),
                        recommendation_type=recommendation_type,
                        title=title,
                        evidence=evidence,
                        insight=statement,
                        business_implication=implication,
                        recommendation=action,
                        priority=priority,
                        confidence=confidence,
                        limitations=limitations,
                    )
                )

            except (KeyError, TypeError, ValueError):
                logger.warning(
                    "Ignoring a malformed recommendation returned by Groq."
                )

        if not recommendations:
            raise ValueError(
                "No Groq recommendations passed the input checks."
            )

        # The existing validation engine remains authoritative.
        validation = validate_recommendations(recommendations)

        if validation.get("overall_status") != "PASSED":
            raise ValueError(
                "Groq recommendations failed recommendation validation."
            )

        return recommendations

    # =================================================================
    # GENERATE RECOMMENDATIONS
    # =================================================================

    def generate_recommendations(self) -> List[Recommendation]:
        """Generate recommendations using the configured Groq API."""

        self.decision_trace.append(
            "Generate evidence-grounded recommendations using Groq."
        )

        self.recommendations = self._generate_with_groq()

        self.decision_trace.append(
            f"Generated {len(self.recommendations)} recommendations."
        )

        return self.recommendations

    # =================================================================
    # VALIDATION
    # =================================================================

    def validate(self) -> Dict[str, Any]:
        """Validate generated recommendations."""

        self.recommendation_validation = validate_recommendations(
            self.recommendations
        )

        self.decision_trace.append(
            "Recommendation validation: "
            + str(
                self.recommendation_validation.get("overall_status")
            )
        )

        return self.recommendation_validation

    # =================================================================
    # SAFETY CHECK
    # =================================================================

    def safety_check(self) -> bool:
        """Require evidence, limitations, an action and passed validation."""

        safe = True

        for item in self.recommendations:
            if not item.evidence:
                self.errors.append(
                    f"{item.recommendation_id} has no evidence."
                )
                safe = False

            if not item.limitations:
                self.errors.append(
                    f"{item.recommendation_id} has no limitations."
                )
                safe = False

            if not item.recommendation.strip():
                self.errors.append(
                    f"{item.recommendation_id} has no actionable recommendation."
                )
                safe = False

            if item.validation_status != "PASSED":
                self.errors.append(
                    f"{item.recommendation_id} did not pass validation."
                )
                safe = False

        self.decision_trace.append(
            "Recommendation safety check: "
            + ("PASSED" if safe else "FAILED")
        )

        return safe

    # =================================================================
    # RUN AGENT
    # =================================================================

    
    def run(self) -> RecommendationAgentResult:
        """Run the agent with persistent caching and validation."""

        self.status = "running"
        self.decision_trace.append(
            "Recommendation Agent execution started."
        )

        # 1. Preconditions
        if not self.check_preconditions():
            self.status = "blocked"
            return self._build_result()

        # 2. Cache lookup
        cache_key = self._get_cache_key()

        if cache_key is not None:
            try:
                cached_result = self.cache.get(cache_key)

                if cached_result is not None:
                    # Return the cached result with an explicit cache-hit
                    # message in the returned decision trace.
                    cached_trace = list(
                        cached_result.get("decision_trace", [])
                    )
                    cached_trace.append(
                        "Recommendations loaded from SQLite cache."
                    )
                    cached_result["decision_trace"] = cached_trace

                    return RecommendationAgentResult(**cached_result)

            except Exception:
                logger.exception(
                    "Recommendation cache lookup failed; "
                    "continuing with Groq."
                )
                self.warnings.append(
                    "Cache lookup failed; recommendations "
                    "will be generated again."
                )

        # 3. Evidence and scope
        self.identify_evidence_sources()
        self.determine_recommendation_scope()

        # 4. Generate, validate, safety-check and cache.
        try:
            self.generate_recommendations()

            # 5. Validate
            validation = self.validate()

            if validation.get("overall_status") != "PASSED":
                self.status = "failed"
                self.errors.append(
                    "Recommendation validation failed."
                )
                return self._build_result()

            # 6. Safety
            if not self.safety_check():
                self.status = "failed"
                return self._build_result()

            # 7. Complete
            self.status = "completed"
            self.decision_trace.append(
                "Recommendation Agent execution completed."
            )

            result = self._build_result()

            # 8. Cache only successful, validated results.
            if cache_key is not None:
                try:
                    stored = self.cache.put(
                        cache_key,
                        result.to_dict(),
                    )

                    if stored:
                        self.decision_trace.append(
                            "Validated recommendations saved to SQLite."
                        )
                        result.decision_trace = list(
                            self.decision_trace
                        )
                    else:
                        self.warnings.append(
                            "Result did not meet the cacheability "
                            "requirements."
                        )
                        result.warnings = list(self.warnings)

                except Exception:
                    logger.exception(
                        "Could not persist recommendations to SQLite."
                    )
                    self.warnings.append(
                        "SQLite caching failed."
                    )
                    result.warnings = list(self.warnings)

            return result

        except Exception as exc:
            logger.exception("Recommendation generation failed.")
            self.status = "failed"
            self.errors.append(str(exc))
            self.decision_trace.append(
                "Recommendation generation failed; "
                "result was not cached."
            )
            return self._build_result()

    # =================================================================
    # RESULT
    # =================================================================

    def _build_result(self) -> RecommendationAgentResult:
        """Build the structured agent result."""

        return RecommendationAgentResult(
            status=self.status,
            recommendations=serialize_recommendations(
                self.recommendations
            ),
            total_recommendations=len(self.recommendations),
            recommendation_validation=self.recommendation_validation,
            evidence_sources=self.evidence_sources,
            decision_trace=self.decision_trace,
            warnings=self.warnings,
            errors=self.errors,
        )


# =====================================================================
# CONVENIENCE FUNCTION
# =====================================================================

def run_recommendation_agent(
    insights: List[Dict[str, Any]],
    insight_validation: Optional[Dict[str, Any]] = None,
    forecast_result: Optional[Dict[str, Any]] = None,
    analysis_df: Optional[pd.DataFrame] = None,
) -> RecommendationAgentResult:
    """Convenience function for running the Recommendation Agent."""

    agent = RecommendationAgent(
        insights=insights,
        insight_validation=insight_validation,
        forecast_result=forecast_result,
        analysis_df=analysis_df,
    )

    return agent.run()
