"""
Ranking Analytics

Performs deterministic ranking analysis on cleaned
retail sales data.

Supported rankings:
- Product Category
- City / Region
- Customer
- Product Category by Quantity

This module does not modify the input DataFrame.
It does not generate business recommendations.
"""

from typing import Dict, Any, Optional

import pandas as pd


class RankingAnalyzer:
    """
    Calculates business rankings from cleaned sales data.
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
                "Ranking Analyzer cannot process "
                "an empty DataFrame."
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

        Supports both:

        "product": "Product Category"

        and:

        "product": {
            "column": "Product Category",
            "confidence": 0.95
        }
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

    def _prepare_numeric_column(
        self,
        semantic_name: str
    ) -> Optional[str]:
        """
        Validate that a semantic column exists
        and contains usable numeric values.
        """

        column = self._get_semantic_column(
            semantic_name
        )

        if column is None:
            return None

        numeric_values = pd.to_numeric(
            self.df[column],
            errors="coerce"
        )

        if numeric_values.notna().sum() == 0:
            return None

        return column

    def _top_n(
        self,
        grouped: pd.DataFrame,
        n: int
    ) -> pd.DataFrame:
        """
        Return the top N rows from a ranking.
        """

        n = max(
            1,
            int(n)
        )

        return (
            grouped
            .head(n)
            .reset_index(drop=True)
        )

    # ---------------------------------------------------------
    # Product rankings
    # ---------------------------------------------------------

    def product_sales(
        self,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Rank product categories by total sales.
        """

        product_column = (
            self._get_semantic_column(
                "product"
            )
        )

        sales_column = (
            self._prepare_numeric_column(
                "sales"
            )
        )

        if (
            product_column is None
            or sales_column is None
        ):
            return pd.DataFrame(
                columns=[
                    "product",
                    "sales"
                ]
            )

        data = self.df[
            [
                product_column,
                sales_column
            ]
        ].copy()

        data["sales"] = pd.to_numeric(
            data[sales_column],
            errors="coerce"
        )

        data = data[
            data["sales"].notna()
        ]

        ranking = (
            data.groupby(
                product_column
            )["sales"]
            .sum()
            .reset_index()
        )

        ranking.columns = [
            "product",
            "sales"
        ]

        ranking = ranking.sort_values(
            "sales",
            ascending=False
        )

        return self._top_n(
            ranking,
            top_n
        )

    def product_quantity(
        self,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Rank product categories by total quantity.
        """

        product_column = (
            self._get_semantic_column(
                "product"
            )
        )

        quantity_column = (
            self._prepare_numeric_column(
                "quantity"
            )
        )

        if (
            product_column is None
            or quantity_column is None
        ):
            return pd.DataFrame(
                columns=[
                    "product",
                    "quantity"
                ]
            )

        data = self.df[
            [
                product_column,
                quantity_column
            ]
        ].copy()

        data["quantity"] = pd.to_numeric(
            data[quantity_column],
            errors="coerce"
        )

        data = data[
            data["quantity"].notna()
        ]

        ranking = (
            data.groupby(
                product_column
            )["quantity"]
            .sum()
            .reset_index()
        )

        ranking.columns = [
            "product",
            "quantity"
        ]

        ranking = ranking.sort_values(
            "quantity",
            ascending=False
        )

        return self._top_n(
            ranking,
            top_n
        )

    # ---------------------------------------------------------
    # Regional / City rankings
    # ---------------------------------------------------------

    def regional_sales(
        self,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Rank regions/cities by total sales.
        """

        region_column = (
            self._get_semantic_column(
                "region"
            )
        )

        sales_column = (
            self._prepare_numeric_column(
                "sales"
            )
        )

        if (
            region_column is None
            or sales_column is None
        ):
            return pd.DataFrame(
                columns=[
                    "region",
                    "sales"
                ]
            )

        data = self.df[
            [
                region_column,
                sales_column
            ]
        ].copy()

        data["sales"] = pd.to_numeric(
            data[sales_column],
            errors="coerce"
        )

        data = data[
            data["sales"].notna()
        ]

        ranking = (
            data.groupby(
                region_column
            )["sales"]
            .sum()
            .reset_index()
        )

        ranking.columns = [
            "region",
            "sales"
        ]

        ranking = ranking.sort_values(
            "sales",
            ascending=False
        )

        return self._top_n(
            ranking,
            top_n
        )

    # ---------------------------------------------------------
    # Customer rankings
    # ---------------------------------------------------------

    def customer_sales(
        self,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Rank customers by total sales.
        """

        customer_column = (
            self._get_semantic_column(
                "customer"
            )
        )

        sales_column = (
            self._prepare_numeric_column(
                "sales"
            )
        )

        if (
            customer_column is None
            or sales_column is None
        ):
            return pd.DataFrame(
                columns=[
                    "customer",
                    "sales"
                ]
            )

        data = self.df[
            [
                customer_column,
                sales_column
            ]
        ].copy()

        data["sales"] = pd.to_numeric(
            data[sales_column],
            errors="coerce"
        )

        data = data[
            data["sales"].notna()
        ]

        ranking = (
            data.groupby(
                customer_column
            )["sales"]
            .sum()
            .reset_index()
        )

        ranking.columns = [
            "customer",
            "sales"
        ]

        ranking = ranking.sort_values(
            "sales",
            ascending=False
        )

        return self._top_n(
            ranking,
            top_n
        )

    # ---------------------------------------------------------
    # Complete ranking analysis
    # ---------------------------------------------------------

    def analyze(
        self,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Run all supported ranking analyses.
        """

        return {
            "product_sales": self.product_sales(
                top_n
            ),
            "product_quantity": self.product_quantity(
                top_n
            ),
            "regional_sales": self.regional_sales(
                top_n
            ),
            "customer_sales": self.customer_sales(
                top_n
            )
        }


# -------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------

def analyze_rankings(
    df: pd.DataFrame,
    semantic_mapping: Optional[Dict[str, Any]] = None,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Convenience function for ranking analysis.
    """

    analyzer = RankingAnalyzer(
        df=df,
        semantic_mapping=semantic_mapping
    )

    return analyzer.analyze(
        top_n=top_n
    )