"""
EDA Agent

Coordinates deterministic exploratory data analysis.

Workflow:

Cleaned Data
    ↓
KPI Analysis
    ↓
Trend Analysis
    ↓
Ranking Analysis
    ↓
EDA Validation
    ↓
Structured EDA Results

The EDA Agent does not:
- modify the dataset
- generate visualisations
- generate business recommendations
- generate unsupported natural-language insights

Numerical calculations are performed by the analytics modules.
"""

from typing import Dict, Any, Optional

import pandas as pd

from analytics.kpis import KPIAnalyzer
from analytics.trends import TrendAnalyzer
from analytics.rankings import RankingAnalyzer


class EDAAgent:
    """
    Main coordinator for Exploratory Data Analysis.
    """

    AGENT_NAME = "EDA Agent"

    def __init__(
        self,
        df: pd.DataFrame,
        semantic_mapping: Optional[Dict[str, Any]] = None,
        cleaning_validation: Optional[Dict[str, Any]] = None
    ):
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "df must be a pandas DataFrame."
            )

        if df.empty:
            raise ValueError(
                "EDA Agent cannot process an empty DataFrame."
            )

        self.df = df.copy()

        self.semantic_mapping = (
            semantic_mapping or {}
        )

        self.cleaning_validation = (
            cleaning_validation or {}
        )

        self.status = "initialized"

        self.kpis: Dict[str, Any] = {}
        self.trends: Dict[str, Any] = {}
        self.rankings: Dict[str, Any] = {}

        self.validation_result: Dict[str, Any] = {}

        self.result: Dict[str, Any] = {}

    # ---------------------------------------------------------
    # Semantic mapping helper
    # ---------------------------------------------------------

    def _get_semantic_column(
        self,
        semantic_name: str
    ) -> Optional[str]:
        """
        Return the actual DataFrame column associated
        with a semantic field.
        """

        mapping = self.semantic_mapping.get(
            semantic_name
        )

        if isinstance(mapping, dict):
            column = mapping.get(
                "column"
            )

        elif isinstance(mapping, str):
            column = mapping

        else:
            column = None

        if (
            column is not None
            and column in self.df.columns
        ):
            return column

        return None

    # ---------------------------------------------------------
    # KPI analysis
    # ---------------------------------------------------------

    def run_kpi_analysis(
        self
    ) -> Dict[str, Any]:
        """
        Execute KPI analysis.
        """

        analyzer = KPIAnalyzer(
            df=self.df,
            semantic_mapping=self.semantic_mapping
        )

        self.kpis = analyzer.calculate_all()

        return self.kpis

    # ---------------------------------------------------------
    # Trend analysis
    # ---------------------------------------------------------

    def run_trend_analysis(
        self
    ) -> Dict[str, Any]:
        """
        Execute time-based trend analysis.
        """

        date_column = (
            self._get_semantic_column(
                "date"
            )
        )

        sales_column = (
            self._get_semantic_column(
                "sales"
            )
        )

        if date_column is None:
            self.trends = {
                "status": "not_available",
                "reason": (
                    "No valid date column was "
                    "identified."
                )
            }

            return self.trends

        if sales_column is None:
            self.trends = {
                "status": "not_available",
                "reason": (
                    "No valid sales column was "
                    "identified."
                )
            }

            return self.trends

        analyzer = TrendAnalyzer(
            df=self.df,
            semantic_mapping=self.semantic_mapping
        )

        self.trends = analyzer.analyze()

        self.trends["status"] = "available"

        return self.trends

    # ---------------------------------------------------------
    # Ranking analysis
    # ---------------------------------------------------------

    def run_ranking_analysis(
        self,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Execute product, regional and customer
        ranking analysis.
        """

        analyzer = RankingAnalyzer(
            df=self.df,
            semantic_mapping=self.semantic_mapping
        )

        self.rankings = analyzer.analyze(
            top_n=top_n
        )

        return self.rankings

    # ---------------------------------------------------------
    # EDA validation
    # ---------------------------------------------------------

    def validate_results(
        self
    ) -> Dict[str, Any]:
        """
        Validate that the EDA results contain
        usable analytical outputs.

        This validation does not attempt to prove
        business correctness beyond basic structural
        and numerical checks.
        """

        checks = []

        # -----------------------------------------------------
        # Dataset check
        # -----------------------------------------------------

        dataset_check = {
            "check": "dataset_not_empty",
            "status": (
                "PASSED"
                if not self.df.empty
                else "FAILED"
            ),
            "details": {
                "rows": len(self.df),
                "columns": len(self.df.columns)
            }
        }

        checks.append(
            dataset_check
        )

        # -----------------------------------------------------
        # KPI check
        # -----------------------------------------------------

        required_kpis = [
            "total_sales",
            "total_quantity",
            "total_orders"
        ]

        missing_kpis = [
            key
            for key in required_kpis
            if self.kpis.get(key) is None
        ]

        kpi_check = {
            "check": "kpi_results",
            "status": (
                "PASSED"
                if not missing_kpis
                else "WARNING"
            ),
            "details": {
                "missing_kpis": missing_kpis
            }
        }

        checks.append(
            kpi_check
        )

        # -----------------------------------------------------
        # Trend check
        # -----------------------------------------------------

        if (
            self.trends
            and self.trends.get("status")
            != "not_available"
        ):

            monthly_sales = self.trends.get(
                "monthly_sales"
            )

            trend_available = (
                isinstance(
                    monthly_sales,
                    pd.DataFrame
                )
                and not monthly_sales.empty
            )

            trend_status = (
                "PASSED"
                if trend_available
                else "WARNING"
            )

        else:

            trend_status = "WARNING"

        checks.append({
            "check": "trend_results",
            "status": trend_status
        })

        # -----------------------------------------------------
        # Ranking check
        # -----------------------------------------------------

        ranking_keys = [
            "product_sales",
            "product_quantity",
            "regional_sales",
            "customer_sales"
        ]

        missing_rankings = [
            key
            for key in ranking_keys
            if (
                key not in self.rankings
                or not isinstance(
                    self.rankings[key],
                    pd.DataFrame
                )
                or self.rankings[key].empty
            )
        ]

        ranking_check = {
            "check": "ranking_results",
            "status": (
                "PASSED"
                if not missing_rankings
                else "WARNING"
            ),
            "details": {
                "missing_rankings": missing_rankings
            }
        }

        checks.append(
            ranking_check
        )

        # -----------------------------------------------------
        # Cleaning validation check
        # -----------------------------------------------------

        cleaning_status = (
            self.cleaning_validation.get(
                "overall_status"
            )
        )

        if cleaning_status == "PASSED":

            cleaning_check_status = "PASSED"

        elif cleaning_status in {
            "WARNING",
            "WARN"
        }:

            cleaning_check_status = "WARNING"

        elif cleaning_status:

            cleaning_check_status = "FAILED"

        else:

            cleaning_check_status = "WARNING"

        checks.append({
            "check": "cleaning_validation",
            "status": cleaning_check_status,
            "details": {
                "cleaning_status": cleaning_status
            }
        })

        # -----------------------------------------------------
        # Overall status
        # -----------------------------------------------------

        failed = [
            check
            for check in checks
            if check["status"] == "FAILED"
        ]

        warnings = [
            check
            for check in checks
            if check["status"] == "WARNING"
        ]

        if failed:
            overall_status = "FAILED"

        elif warnings:
            overall_status = "WARNING"

        else:
            overall_status = "PASSED"

        self.validation_result = {
            "overall_status": overall_status,
            "total_checks": len(checks),
            "passed_checks": sum(
                check["status"] == "PASSED"
                for check in checks
            ),
            "failed_checks": len(failed),
            "warning_checks": len(warnings),
            "checks": checks
        }

        return self.validation_result

    # ---------------------------------------------------------
    # Complete EDA workflow
    # ---------------------------------------------------------

    def run(
        self,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Execute the complete EDA workflow.
        """

        self.status = "running"

        self.run_kpi_analysis()

        self.run_trend_analysis()

        self.run_ranking_analysis(
            top_n=top_n
        )

        self.validate_results()

        if (
            self.validation_result
            .get("overall_status")
            == "PASSED"
        ):

            self.status = "completed"

        elif (
            self.validation_result
            .get("overall_status")
            == "WARNING"
        ):

            self.status = (
                "completed_with_warnings"
            )

        else:

            self.status = "failed"

        self.result = self.get_result()

        return self.result

    # ---------------------------------------------------------
    # Structured result
    # ---------------------------------------------------------

    def get_result(
        self
    ) -> Dict[str, Any]:
        """
        Return the complete structured EDA result.
        """

        return {
            "agent": self.AGENT_NAME,
            "status": self.status,

            "dataset": {
                "rows": len(self.df),
                "columns": len(self.df.columns)
            },

            "kpis": self.kpis,

            "trends": self.trends,

            "rankings": self.rankings,

            "validation": self.validation_result
        }

    # ---------------------------------------------------------
    # Getters
    # ---------------------------------------------------------

    def get_kpis(
        self
    ) -> Dict[str, Any]:

        return self.kpis

    def get_trends(
        self
    ) -> Dict[str, Any]:

        return self.trends

    def get_rankings(
        self
    ) -> Dict[str, Any]:

        return self.rankings

    def get_validation_result(
        self
    ) -> Dict[str, Any]:

        return self.validation_result

    def get_result_data(
        self
    ) -> Dict[str, Any]:

        return self.result