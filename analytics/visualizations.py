"""
Visualization Analytics

Creates deterministic visualization specifications and charts
from verified EDA results.

This module:
- Does not modify the source dataset.
- Does not generate business insights.
- Does not generate recommendations.
- Uses Python/Matplotlib for actual chart generation.
"""

from typing import Dict, Any, Optional, List

import os

import pandas as pd
import matplotlib.pyplot as plt


class VisualizationAnalyzer:
    """
    Creates charts from structured EDA results.
    """

    def __init__(
        self,
        eda_result: Dict[str, Any],
        output_dir: str = "outputs/visualizations"
    ):
        if not isinstance(eda_result, dict):
            raise TypeError(
                "eda_result must be a dictionary."
            )

        self.eda_result = eda_result

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        self.generated_charts: List[
            Dict[str, Any]
        ] = []

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _get_dataframe(
        self,
        section: str,
        key: str
    ) -> Optional[pd.DataFrame]:
        """
        Safely retrieve a DataFrame from the EDA result.
        """

        section_data = self.eda_result.get(
            section,
            {}
        )

        if not isinstance(
            section_data,
            dict
        ):
            return None

        dataframe = section_data.get(
            key
        )

        if isinstance(
            dataframe,
            pd.DataFrame
        ):
            return dataframe.copy()

        return None

    def _save_chart(
        self,
        filename: str
    ) -> str:
        """
        Return the output path for a chart.
        """

        return os.path.join(
            self.output_dir,
            filename
        )

    def _record_chart(
        self,
        chart_type: str,
        title: str,
        path: str,
        rows: int
    ) -> Dict[str, Any]:
        """
        Record metadata about a generated chart.
        """

        record = {
            "chart_type": chart_type,
            "title": title,
            "path": path,
            "rows_used": rows,
            "status": "generated"
        }

        self.generated_charts.append(
            record
        )

        return record

    # ---------------------------------------------------------
    # KPI specification
    # ---------------------------------------------------------

    def create_kpi_cards(self) -> List[Dict[str, Any]]:
        """
        Create structured KPI card specifications.

        KPI cards are not plotted as Matplotlib charts.
        They are intended for the Streamlit dashboard.
        """

        kpis = self.eda_result.get(
            "kpis",
            {}
        )

        if not isinstance(kpis, dict):
            return []

        cards = []

        labels = {
            "total_sales": "Total Sales",
            "total_quantity": "Total Quantity",
            "total_orders": "Total Orders",
            "total_customers": "Total Customers",
            "average_order_value": "Average Order Value",
            "average_quantity_per_order": (
                "Average Quantity per Order"
            ),
            "average_selling_price": (
                "Average Selling Price"
            )
        }

        for key, label in labels.items():

            value = kpis.get(
                key
            )

            if value is None:
                continue

            cards.append({
                "key": key,
                "label": label,
                "value": value,
                "status": "available"
            })

        return cards

    # ---------------------------------------------------------
    # Daily sales chart
    # ---------------------------------------------------------

    def plot_daily_sales(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a daily sales line chart.
        """

        dataframe = self._get_dataframe(
            "trends",
            "daily_sales"
        )

        if (
            dataframe is None
            or dataframe.empty
        ):
            return None

        required_columns = {
            "date",
            "sales"
        }

        if not required_columns.issubset(
            dataframe.columns
        ):
            return None

        dataframe["date"] = pd.to_datetime(
            dataframe["date"],
            errors="coerce"
        )

        dataframe["sales"] = pd.to_numeric(
            dataframe["sales"],
            errors="coerce"
        )

        dataframe = dataframe.dropna(
            subset=[
                "date",
                "sales"
            ]
        )

        if dataframe.empty:
            return None

        path = self._save_chart(
            "daily_sales.png"
        )

        plt.figure(
            figsize=(10, 5)
        )

        plt.plot(
            dataframe["date"],
            dataframe["sales"]
        )

        plt.title(
            "Daily Sales Trend"
        )

        plt.xlabel(
            "Date"
        )

        plt.ylabel(
            "Sales"
        )

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()

        return self._record_chart(
            chart_type="line",
            title="Daily Sales Trend",
            path=path,
            rows=len(dataframe)
        )

    # ---------------------------------------------------------
    # Monthly sales chart
    # ---------------------------------------------------------

    def plot_monthly_sales(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a monthly sales line chart.
        """

        dataframe = self._get_dataframe(
            "trends",
            "monthly_sales"
        )

        if (
            dataframe is None
            or dataframe.empty
        ):
            return None

        required_columns = {
            "month",
            "sales"
        }

        if not required_columns.issubset(
            dataframe.columns
        ):
            return None

        dataframe["sales"] = pd.to_numeric(
            dataframe["sales"],
            errors="coerce"
        )

        dataframe = dataframe.dropna(
            subset=[
                "sales"
            ]
        )

        if dataframe.empty:
            return None

        path = self._save_chart(
            "monthly_sales.png"
        )

        plt.figure(
            figsize=(10, 5)
        )

        plt.plot(
            dataframe["month"],
            dataframe["sales"],
            marker="o"
        )

        plt.title(
            "Monthly Sales Trend"
        )

        plt.xlabel(
            "Month"
        )

        plt.ylabel(
            "Sales"
        )

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()

        return self._record_chart(
            chart_type="line",
            title="Monthly Sales Trend",
            path=path,
            rows=len(dataframe)
        )

    # ---------------------------------------------------------
    # Product sales chart
    # ---------------------------------------------------------

    def plot_product_sales(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a product-category sales bar chart.
        """

        dataframe = self._get_dataframe(
            "rankings",
            "product_sales"
        )

        if (
            dataframe is None
            or dataframe.empty
        ):
            return None

        required_columns = {
            "product",
            "sales"
        }

        if not required_columns.issubset(
            dataframe.columns
        ):
            return None

        dataframe["sales"] = pd.to_numeric(
            dataframe["sales"],
            errors="coerce"
        )

        dataframe = dataframe.dropna(
            subset=[
                "sales"
            ]
        )

        if dataframe.empty:
            return None

        path = self._save_chart(
            "product_sales.png"
        )

        plt.figure(
            figsize=(9, 5)
        )

        plt.bar(
            dataframe["product"],
            dataframe["sales"]
        )

        plt.title(
            "Sales by Product Category"
        )

        plt.xlabel(
            "Product Category"
        )

        plt.ylabel(
            "Sales"
        )

        plt.xticks(
            rotation=30
        )

        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()

        return self._record_chart(
            chart_type="bar",
            title="Sales by Product Category",
            path=path,
            rows=len(dataframe)
        )

    # ---------------------------------------------------------
    # Product quantity chart
    # ---------------------------------------------------------

    def plot_product_quantity(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a product-category quantity bar chart.
        """

        dataframe = self._get_dataframe(
            "rankings",
            "product_quantity"
        )

        if (
            dataframe is None
            or dataframe.empty
        ):
            return None

        required_columns = {
            "product",
            "quantity"
        }

        if not required_columns.issubset(
            dataframe.columns
        ):
            return None

        dataframe["quantity"] = pd.to_numeric(
            dataframe["quantity"],
            errors="coerce"
        )

        dataframe = dataframe.dropna(
            subset=[
                "quantity"
            ]
        )

        if dataframe.empty:
            return None

        path = self._save_chart(
            "product_quantity.png"
        )

        plt.figure(
            figsize=(9, 5)
        )

        plt.bar(
            dataframe["product"],
            dataframe["quantity"]
        )

        plt.title(
            "Quantity by Product Category"
        )

        plt.xlabel(
            "Product Category"
        )

        plt.ylabel(
            "Quantity"
        )

        plt.xticks(
            rotation=30
        )

        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()

        return self._record_chart(
            chart_type="bar",
            title="Quantity by Product Category",
            path=path,
            rows=len(dataframe)
        )

    # ---------------------------------------------------------
    # Regional sales chart
    # ---------------------------------------------------------

    def plot_regional_sales(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a regional sales bar chart.
        """

        dataframe = self._get_dataframe(
            "rankings",
            "regional_sales"
        )

        if (
            dataframe is None
            or dataframe.empty
        ):
            return None

        required_columns = {
            "region",
            "sales"
        }

        if not required_columns.issubset(
            dataframe.columns
        ):
            return None

        dataframe["sales"] = pd.to_numeric(
            dataframe["sales"],
            errors="coerce"
        )

        dataframe = dataframe.dropna(
            subset=[
                "sales"
            ]
        )

        if dataframe.empty:
            return None

        # Reverse the ranking so the highest
        # value appears at the top of a horizontal chart.
        dataframe = dataframe.sort_values(
            "sales",
            ascending=True
        )

        path = self._save_chart(
            "regional_sales.png"
        )

        plt.figure(
            figsize=(10, 6)
        )

        plt.barh(
            dataframe["region"],
            dataframe["sales"]
        )

        plt.title(
            "Sales by Region"
        )

        plt.xlabel(
            "Sales"
        )

        plt.ylabel(
            "Region"
        )

        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()

        return self._record_chart(
            chart_type="bar_horizontal",
            title="Sales by Region",
            path=path,
            rows=len(dataframe)
        )

    # ---------------------------------------------------------
    # Customer sales chart
    # ---------------------------------------------------------

    def plot_customer_sales(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a top-customer sales bar chart.
        """

        dataframe = self._get_dataframe(
            "rankings",
            "customer_sales"
        )

        if (
            dataframe is None
            or dataframe.empty
        ):
            return None

        required_columns = {
            "customer",
            "sales"
        }

        if not required_columns.issubset(
            dataframe.columns
        ):
            return None

        dataframe["sales"] = pd.to_numeric(
            dataframe["sales"],
            errors="coerce"
        )

        dataframe = dataframe.dropna(
            subset=[
                "sales"
            ]
        )

        if dataframe.empty:
            return None

        dataframe = dataframe.sort_values(
            "sales",
            ascending=True
        )

        path = self._save_chart(
            "customer_sales.png"
        )

        plt.figure(
            figsize=(10, 6)
        )

        plt.barh(
            dataframe["customer"],
            dataframe["sales"]
        )

        plt.title(
            "Top Customers by Sales"
        )

        plt.xlabel(
            "Sales"
        )

        plt.ylabel(
            "Customer"
        )

        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()

        return self._record_chart(
            chart_type="bar_horizontal",
            title="Top Customers by Sales",
            path=path,
            rows=len(dataframe)
        )

    # ---------------------------------------------------------
    # Complete visualization generation
    # ---------------------------------------------------------

    def generate_all(
        self
    ) -> Dict[str, Any]:
        """
        Generate all currently supported visualizations.
        """

        self.generated_charts = []

        kpi_cards = (
            self.create_kpi_cards()
        )

        chart_methods = [
            self.plot_daily_sales,
            self.plot_monthly_sales,
            self.plot_product_sales,
            self.plot_product_quantity,
            self.plot_regional_sales,
            self.plot_customer_sales
        ]

        for method in chart_methods:
            method()

        return {
            "kpi_cards": kpi_cards,
            "charts": self.generated_charts,
            "total_charts": len(
                self.generated_charts
            ),
            "status": (
                "completed"
                if self.generated_charts
                else "no_charts_generated"
            )
        }


# -------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------

def generate_visualizations(
    eda_result: Dict[str, Any],
    output_dir: str = "outputs/visualizations"
) -> Dict[str, Any]:
    """
    Convenience function for visualization generation.
    """

    analyzer = VisualizationAnalyzer(
        eda_result=eda_result,
        output_dir=output_dir
    )

    return analyzer.generate_all()