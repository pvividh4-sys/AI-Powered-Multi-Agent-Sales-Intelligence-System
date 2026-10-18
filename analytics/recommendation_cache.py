
"""Persistent cache for validated recommendation results."""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd


CACHE_VERSION = "recommendation-cache-v1"

DEFAULT_DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "cache"
    / "recommendations.sqlite3"
)


def _json_safe(value: Any) -> Any:
    if value is None or value is pd.NA or value is pd.NaT:
        return None

    if isinstance(value, dict):
        return {
            str(k): _json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()

    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())

    if isinstance(value, (str, int, bool)):
        return value

    return str(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _json_safe(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def dataframe_fingerprint(df: pd.DataFrame) -> str:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    digest = hashlib.sha256()

    metadata = {
        "columns": [str(c) for c in df.columns],
        "dtypes": [str(dtype) for dtype in df.dtypes],
        "shape": list(df.shape),
        "index_names": [str(n) for n in df.index.names],
        "index_dtype": str(df.index.dtype),
    }

    digest.update(_canonical_json(metadata).encode("utf-8"))

    row_hashes = pd.util.hash_pandas_object(
        df,
        index=True,
        categorize=True,
    )

    digest.update(row_hashes.to_numpy(dtype="uint64").tobytes())

    return digest.hexdigest()


def make_recommendation_cache_key(
    *,
    df: pd.DataFrame,
    insights: list[dict[str, Any]],
    insight_validation: dict[str, Any],
    forecast_result: dict[str, Any],
    model: str = "deterministic",
    prompt_version: str = "rules-v1",
    analysis_config: Optional[dict[str, Any]] = None,
) -> str:
    payload = {
        "cache_version": CACHE_VERSION,
        "dataset_fingerprint": dataframe_fingerprint(df),
        "insights": insights,
        "insight_validation": insight_validation,
        "forecast_result": forecast_result,
        "model": model,
        "prompt_version": prompt_version,
        "analysis_config": analysis_config or {},
    }

    return hashlib.sha256(
        _canonical_json(payload).encode("utf-8")
    ).hexdigest()



def is_cacheable_result(result: dict[str, Any]) -> bool:
    """Return True only for complete, validated recommendation results."""

    if not isinstance(result, dict):
        return False

    if result.get("status") != "completed":
        return False

    # Failed or incomplete runs must never be cached.
    errors = result.get("errors")
    if not isinstance(errors, list) or errors:
        return False

    # Overall validation must explicitly pass.
    validation = result.get("recommendation_validation")
    if not isinstance(validation, dict):
        return False

    if validation.get("overall_status") != "PASSED":
        return False

    # Require a non-empty list of recommendations.
    recommendations = result.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        return False

    # The reported count must match the actual result.
    if result.get("total_recommendations") != len(recommendations):
        return False

    # Validate the required fields of every recommendation.
    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            return False

        if recommendation.get("validation_status") != "PASSED":
            return False

        evidence = recommendation.get("evidence")
        if not isinstance(evidence, dict) or not evidence:
            return False

        limitations = recommendation.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            return False

        action = recommendation.get("recommendation")
        if not isinstance(action, str) or not action.strip():
            return False

    return True


class RecommendationCache:
    def __init__(
        self,
        db_path: str | Path = DEFAULT_DB_PATH,
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self.db_path,
            timeout=10,
        )

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recommendation_results (
                    cache_key TEXT PRIMARY KEY,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    cache_version TEXT NOT NULL
                )
                """
            )

    def get(
        self,
        cache_key: str,
    ) -> Optional[dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT result_json, cache_version
                FROM recommendation_results
                WHERE cache_key = ?
                """,
                (cache_key,),
            ).fetchone()

            if row is None:
                return None

            result_json, stored_version = row

            try:
                result = json.loads(result_json)
            except (TypeError, json.JSONDecodeError):
                connection.execute(
                    """
                    DELETE FROM recommendation_results
                    WHERE cache_key = ?
                    """,
                    (cache_key,),
                )
                return None

            if (
                stored_version != CACHE_VERSION
                or not is_cacheable_result(result)
            ):
                connection.execute(
                    """
                    DELETE FROM recommendation_results
                    WHERE cache_key = ?
                    """,
                    (cache_key,),
                )
                return None

            return result

    def put(
        self,
        cache_key: str,
        result: dict[str, Any],
    ) -> bool:
        if not is_cacheable_result(result):
            return False

        result_json = _canonical_json(result)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO recommendation_results
                    (cache_key, result_json, cache_version)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    result_json = excluded.result_json,
                    created_at = CURRENT_TIMESTAMP,
                    cache_version = excluded.cache_version
                """,
                (cache_key, result_json, CACHE_VERSION),
            )

        return True

    def delete(self, cache_key: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM recommendation_results
                WHERE cache_key = ?
                """,
                (cache_key,),
            )
