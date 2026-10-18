"""
KPI Analytics

Calculates verified business KPIs from cleaned retail sales data.

This module performs deterministic numerical analysis.
It does not use an LLM and does not modify the input DataFrame.
"""

from typing import Dict, Any, Optional

import pandas as pd


class KPIAnalyzer:
    """
    Calculates core sales and business KPIs.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        semantic_mapping: Optional[Dict[str, Any]] = None
    ):
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "df must be a pandas DataFrame."
            )

        if df.empty:
            raise ValueError(
                "KPI Analyzer cannot process an empty DataFrame."
            )

        self.df = df.copy()

        self.semantic_mapping = (
            semantic_mapping or {}
        )

    # ---------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------

    def _get_semantic_column(
        self,
        semantic_name: str
    ) -> Optional[str]:
        """
        Get the actual DataFrame column associated
        with a semantic field.

        Supports mappings such as:

        "sales": "Total Amount"

        or:

        "sales": {
            "column": "Total Amount",
            "confidence": 0.95
        }
        """

        mapping = self.semantic_mapping.get(
            semantic_name
        )

        if isinstance(mapping, dict):
            column = mapping.get("column")
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

    def _numeric_column(
        self,
        column: Optional[str]
    ) -> Optional[pd.Series]:
        """
        Return a numeric Series if the column
        exists and contains numeric data.
        """

        if column is None:
            return None

        series = pd.to_numeric(
            self.df[column],
            errors="coerce"
        )

        if series.notna().sum() == 0:
            return None

        return series

    # ---------------------------------------------------------
    # Individual KPI calculations
    # ---------------------------------------------------------

    def total_sales(self) -> Optional[float]:
        """
        Calculate total sales/revenue.
        """

        sales_column = self._get_semantic_column(
            "sales"
        )

        sales = self._numeric_column(
            sales_column
        )

        if sales is None:
            return None

        return float(sales.sum())

    def total_quantity(self) -> Optional[float]:
        """
        Calculate total quantity sold.
        """

        quantity_column = self._get_semantic_column(
            "quantity"
        )

        quantity = self._numeric_column(
            quantity_column
        )

        if quantity is None:
            return None

        return float(quantity.sum())

    def total_orders(self) -> int:
        """
        Calculate number of orders.

        If an Order ID semantic mapping exists,
        unique Order IDs are counted.

        Otherwise, the number of rows is used
        as a fallback.
        """

        order_column = self._get_semantic_column(
            "order_id"
        )

        if order_column is not None:
            return int(
                self.df[order_column]
                .nunique()
            )

        return int(len(self.df))

    def total_customers(self) -> Optional[int]:
        """
        Calculate number of unique customers.
        """

        customer_column = self._get_semantic_column(
            "customer"
        )

        if customer_column is None:
            return None

        return int(
            self.df[customer_column]
            .nunique()
        )

    def average_order_value(self) -> Optional[float]:
        """
        Calculate average sales value per order.
        """

        sales = self.total_sales()
        orders = self.total_orders()

        if sales is None or orders == 0:
            return None

        return float(
            sales / orders
        )

    def average_quantity_per_order(
        self
    ) -> Optional[float]:
        """
        Calculate average quantity per order.
        """

        quantity = self.total_quantity()
        orders = self.total_orders()

        if quantity is None or orders == 0:
            return None

        return float(
            quantity / orders
        )

    def average_selling_price(
        self
    ) -> Optional[float]:
        """
        Calculate average selling price.

        Uses the sales value divided by quantity.
        """

        sales = self.total_sales()
        quantity = self.total_quantity()

        if (
            sales is None
            or quantity is None
            or quantity == 0
        ):
            return None

        return float(
            sales / quantity
        )

    # ---------------------------------------------------------
    # Complete KPI analysis
    # ---------------------------------------------------------

    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all supported KPIs.

        Returns a structured dictionary that can
        be consumed by the EDA Agent and later
        by the Insight/Recommendation Agents.
        """

        return {
            "total_sales": self.total_sales(),
            "total_quantity": self.total_quantity(),
            "total_orders": self.total_orders(),
            "total_customers": self.total_customers(),
            "average_order_value": (
                self.average_order_value()
            ),
            "average_quantity_per_order": (
                self.average_quantity_per_order()
            ),
            "average_selling_price": (
                self.average_selling_price()
            ),
        }


# -------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------

def calculate_kpis(
    df: pd.DataFrame,
    semantic_mapping: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for calculating KPIs.
    """

    analyzer = KPIAnalyzer(
        df=df,
        semantic_mapping=semantic_mapping
    )

    return analyzer.calculate_all()