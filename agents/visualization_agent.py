"""
Visualization Agent

Coordinates visualization generation from verified EDA results.

Workflow:

EDA Results
    ↓
Visualization Agent
    ↓
Visualization Selection
    ↓
Chart Generation
    ↓
Validation
    ↓
Structured Visualization Results

The agent does not:
- modify the source dataset
- generate business insights
- generate recommendations
- invent analytical values
"""

from typing import Dict, Any, Optional, List

import os
import pandas as pd

from analytics.visualizations import (
    VisualizationAnalyzer
)


class VisualizationAgent:
    """
    Main coordinator for visualization generation.
    """

    AGENT_NAME = "Visualization Agent"

    def __init__(
        self,
        eda_result: Dict[str, Any],
        output_dir: str = (
            "outputs/visualizations"
        )
    ):
        if not isinstance(
            eda_result,
            dict
        ):
            raise TypeError(
                "eda_result must be a dictionary."
            )

        self.eda_result = eda_result

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        self.status = "initialized"

        self.visualization_analyzer = None

        self.kpi_cards: List[
            Dict[str, Any]
        ] = []

        self.charts: List[
            Dict[str, Any]
        ] = []

        self.validation_result: Dict[
            str,
            Any
        ] = {}

        self.result: Dict[
            str,
            Any
        ] = {}

    # ---------------------------------------------------------
    # Initialise analyzer
    # ---------------------------------------------------------

    def initialize_analyzer(
        self
    ) -> VisualizationAnalyzer:
        """
        Initialise the deterministic visualization
        generation module.
        """

        self.visualization_analyzer = (
            VisualizationAnalyzer(
                eda_result=self.eda_result,
                output_dir=self.output_dir
            )
        )

        return self.visualization_analyzer

    # ---------------------------------------------------------
    # Select visualizations
    # ---------------------------------------------------------

    def select_visualizations(
        self
    ) -> Dict[str, Any]:
        """
        Determine which visualization types can be
        generated from the available EDA results.

        This stage selects based on available
        structured analytical data.
        """

        trends = self.eda_result.get(
            "trends",
            {}
        )

        rankings = self.eda_result.get(
            "rankings",
            {}
        )

        kpis = self.eda_result.get(
            "kpis",
            {}
        )

        selections = []

        # KPI cards
        if isinstance(
            kpis,
            dict
        ) and kpis:

            selections.append(
                "kpi_cards"
            )

        # Daily sales
        daily_sales = trends.get(
            "daily_sales"
        )

        if (
            isinstance(
                daily_sales,
                pd.DataFrame
            )
            and not daily_sales.empty
        ):

            selections.append(
                "daily_sales"
            )

        # Monthly sales
        monthly_sales = trends.get(
            "monthly_sales"
        )

        if (
            isinstance(
                monthly_sales,
                pd.DataFrame
            )
            and not monthly_sales.empty
        ):

            selections.append(
                "monthly_sales"
            )

        # Product sales
        product_sales = rankings.get(
            "product_sales"
        )

        if (
            isinstance(
                product_sales,
                pd.DataFrame
            )
            and not product_sales.empty
        ):

            selections.append(
                "product_sales"
            )

        # Product quantity
        product_quantity = rankings.get(
            "product_quantity"
        )

        if (
            isinstance(
                product_quantity,
                pd.DataFrame
            )
            and not product_quantity.empty
        ):

            selections.append(
                "product_quantity"
            )

        # Regional sales
        regional_sales = rankings.get(
            "regional_sales"
        )

        if (
            isinstance(
                regional_sales,
                pd.DataFrame
            )
            and not regional_sales.empty
        ):

            selections.append(
                "regional_sales"
            )

        # Customer sales
        customer_sales = rankings.get(
            "customer_sales"
        )

        if (
            isinstance(
                customer_sales,
                pd.DataFrame
            )
            and not customer_sales.empty
        ):

            selections.append(
                "customer_sales"
            )

        return {
            "selected": selections,
            "count": len(
                selections
            )
        }

    # ---------------------------------------------------------
    # Generate visualizations
    # ---------------------------------------------------------

    def generate(
        self
    ) -> Dict[str, Any]:
        """
        Generate the selected visualizations.
        """

        if (
            self.visualization_analyzer
            is None
        ):

            self.initialize_analyzer()

        selection = (
            self.select_visualizations()
        )

        generated = (
            self.visualization_analyzer
            .generate_all()
        )

        self.kpi_cards = generated.get(
            "kpi_cards",
            []
        )

        self.charts = generated.get(
            "charts",
            []
        )

        return {
            "selection": selection,
            "kpi_cards": self.kpi_cards,
            "charts": self.charts,
            "total_charts": len(
                self.charts
            )
        }

    # ---------------------------------------------------------
    # Validate visualizations
    # ---------------------------------------------------------

    def validate(
        self
    ) -> Dict[str, Any]:
        """
        Validate generated visualization outputs.

        Checks:
        - KPI cards exist when KPI data exists.
        - Charts contain required metadata.
        - Chart files exist.
        - Generated chart count is consistent.
        """

        checks = []

        # -----------------------------------------------------
        # KPI card validation
        # -----------------------------------------------------

        kpis = self.eda_result.get(
            "kpis",
            {}
        )

        if (
            isinstance(
                kpis,
                dict
            )
            and kpis
        ):

            kpi_status = (
                "PASSED"
                if self.kpi_cards
                else "FAILED"
            )

        else:

            kpi_status = "WARNING"

        checks.append({
            "check": "kpi_cards",
            "status": kpi_status,
            "count": len(
                self.kpi_cards
            )
        })

        # -----------------------------------------------------
        # Chart existence validation
        # -----------------------------------------------------

        if self.charts:

            chart_files_valid = all(
                os.path.exists(
                    chart.get(
                        "path",
                        ""
                    )
                )
                for chart in self.charts
            )

            chart_status = (
                "PASSED"
                if chart_files_valid
                else "FAILED"
            )

        else:

            chart_status = "WARNING"

        checks.append({
            "check": "chart_files",
            "status": chart_status,
            "count": len(
                self.charts
            )
        })

        # -----------------------------------------------------
        # Chart metadata validation
        # -----------------------------------------------------

        required_chart_fields = {
            "chart_type",
            "title",
            "path",
            "rows_used",
            "status"
        }

        metadata_valid = all(
            required_chart_fields.issubset(
                chart.keys()
            )
            for chart in self.charts
        )

        if self.charts:

            metadata_status = (
                "PASSED"
                if metadata_valid
                else "FAILED"
            )

        else:

            metadata_status = "WARNING"

        checks.append({
            "check": "chart_metadata",
            "status": metadata_status
        })

        # -----------------------------------------------------
        # Chart row validation
        # -----------------------------------------------------

        invalid_rows = [
            chart
            for chart in self.charts
            if not isinstance(
                chart.get(
                    "rows_used"
                ),
                int
            )
            or chart.get(
                "rows_used"
            ) <= 0
        ]

        if self.charts:

            row_status = (
                "PASSED"
                if not invalid_rows
                else "FAILED"
            )

        else:

            row_status = "WARNING"

        checks.append({
            "check": "chart_rows",
            "status": row_status,
            "invalid_count": len(
                invalid_rows
            )
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
            "total_checks": len(
                checks
            ),
            "passed_checks": sum(
                check["status"] == "PASSED"
                for check in checks
            ),
            "failed_checks": len(
                failed
            ),
            "warning_checks": len(
                warnings
            ),
            "checks": checks
        }

        return self.validation_result

    # ---------------------------------------------------------
    # Complete workflow
    # ---------------------------------------------------------

    def run(
        self
    ) -> Dict[str, Any]:
        """
        Execute the complete Visualization Agent.
        """

        self.status = "running"

        self.initialize_analyzer()

        self.generate()

        self.validate()

        overall_status = (
            self.validation_result.get(
                "overall_status"
            )
        )

        if overall_status == "PASSED":

            self.status = "completed"

        elif overall_status == "WARNING":

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
        Return structured visualization results.
        """

        return {
            "agent": self.AGENT_NAME,

            "status": self.status,

            "selection": (
                self.select_visualizations()
            ),

            "kpi_cards": self.kpi_cards,

            "charts": self.charts,

            "total_charts": len(
                self.charts
            ),

            "validation": (
                self.validation_result
            )
        }

    # ---------------------------------------------------------
    # Getters
    # ---------------------------------------------------------

    def get_kpi_cards(
        self
    ) -> List[Dict[str, Any]]:

        return self.kpi_cards

    def get_charts(
        self
    ) -> List[Dict[str, Any]]:

        return self.charts

    def get_validation_result(
        self
    ) -> Dict[str, Any]:

        return self.validation_result

    def get_result_data(
        self
    ) -> Dict[str, Any]:

        return self.result