"""
Trend Analytics

Performs deterministic time-based sales analysis.

This module:
- Uses the Planner semantic mapping for Date and Sales.
- Converts dates safely.
- Calculates daily and monthly sales.
- Calculates daily and monthly quantity.
- Calculates period-over-period changes.
- Does not modify the input DataFrame.
- Does not generate business explanations.
"""

from typing import Dict, Any, Optional

import pandas as pd


class TrendAnalyzer:
    """
    Performs time-based trend analysis on cleaned sales data.
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
                "Trend Analyzer cannot process "
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

        Supports:

        "date": "Date"

        or:

        "date": {
            "column": "Date",
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

    def _prepare_data(self) -> pd.DataFrame:
        """
        Prepare a working DataFrame containing
        valid datetime and numeric business values.
        """

        date_column = self._get_semantic_column(
            "date"
        )

        sales_column = self._get_semantic_column(
            "sales"
        )

        quantity_column = (
            self._get_semantic_column(
                "quantity"
            )
        )

        if date_column is None:
            raise ValueError(
                "A valid date column is required "
                "for trend analysis."
            )

        if sales_column is None:
            raise ValueError(
                "A valid sales column is required "
                "for trend analysis."
            )

        result = self.df.copy()

        result["_eda_date"] = pd.to_datetime(
            result[date_column],
            errors="coerce",
            dayfirst=True
        )

        result["_eda_sales"] = pd.to_numeric(
            result[sales_column],
            errors="coerce"
        )

        if quantity_column is not None:
            result["_eda_quantity"] = pd.to_numeric(
                result[quantity_column],
                errors="coerce"
            )
        else:
            result["_eda_quantity"] = None

        result = result[
            result["_eda_date"].notna()
        ]

        result = result[
            result["_eda_sales"].notna()
        ]

        result = result.sort_values(
            "_eda_date"
        )

        return result

    # ---------------------------------------------------------
    # Date coverage
    # ---------------------------------------------------------

    def date_coverage(self) -> Dict[str, Any]:
        """
        Return the date range and number of
        valid observations.
        """

        data = self._prepare_data()

        if data.empty:
            return {
                "start_date": None,
                "end_date": None,
                "days": 0,
                "observations": 0
            }

        start_date = data["_eda_date"].min()
        end_date = data["_eda_date"].max()

        return {
            "start_date": start_date.strftime(
                "%Y-%m-%d"
            ),
            "end_date": end_date.strftime(
                "%Y-%m-%d"
            ),
            "days": int(
                (
                    end_date - start_date
                ).days + 1
            ),
            "observations": int(
                len(data)
            )
        }

    # ---------------------------------------------------------
    # Daily trends
    # ---------------------------------------------------------

    def daily_sales(self) -> pd.DataFrame:
        """
        Calculate daily sales.
        """

        data = self._prepare_data()

        if data.empty:
            return pd.DataFrame(
                columns=[
                    "date",
                    "sales"
                ]
            )

        daily = (
            data.groupby(
                data["_eda_date"].dt.date
            )["_eda_sales"]
            .sum()
            .reset_index()
        )

        daily.columns = [
            "date",
            "sales"
        ]

        daily["date"] = pd.to_datetime(
            daily["date"]
        )

        return daily.sort_values(
            "date"
        ).reset_index(drop=True)

    def daily_quantity(self) -> pd.DataFrame:
        """
        Calculate daily quantity.
        """

        data = self._prepare_data()

        if data.empty:
            return pd.DataFrame(
                columns=[
                    "date",
                    "quantity"
                ]
            )

        if data["_eda_quantity"].notna().sum() == 0:
            return pd.DataFrame(
                columns=[
                    "date",
                    "quantity"
                ]
            )

        daily = (
            data.groupby(
                data["_eda_date"].dt.date
            )["_eda_quantity"]
            .sum()
            .reset_index()
        )

        daily.columns = [
            "date",
            "quantity"
        ]

        daily["date"] = pd.to_datetime(
            daily["date"]
        )

        return daily.sort_values(
            "date"
        ).reset_index(drop=True)

    # ---------------------------------------------------------
    # Monthly trends
    # ---------------------------------------------------------

    def monthly_sales(self) -> pd.DataFrame:
        """
        Calculate monthly sales.
        """

        data = self._prepare_data()

        if data.empty:
            return pd.DataFrame(
                columns=[
                    "month",
                    "sales"
                ]
            )

        data["_month"] = (
            data["_eda_date"]
            .dt.to_period("M")
        )

        monthly = (
            data.groupby(
                "_month"
            )["_eda_sales"]
            .sum()
            .reset_index()
        )

        monthly.columns = [
            "month",
            "sales"
        ]

        monthly["month"] = (
            monthly["month"]
            .astype(str)
        )

        return monthly.reset_index(
            drop=True
        )

    def monthly_quantity(self) -> pd.DataFrame:
        """
        Calculate monthly quantity.
        """

        data = self._prepare_data()

        if data.empty:
            return pd.DataFrame(
                columns=[
                    "month",
                    "quantity"
                ]
            )

        if data["_eda_quantity"].notna().sum() == 0:
            return pd.DataFrame(
                columns=[
                    "month",
                    "quantity"
                ]
            )

        data["_month"] = (
            data["_eda_date"]
            .dt.to_period("M")
        )

        monthly = (
            data.groupby(
                "_month"
            )["_eda_quantity"]
            .sum()
            .reset_index()
        )

        monthly.columns = [
            "month",
            "quantity"
        ]

        monthly["month"] = (
            monthly["month"]
            .astype(str)
        )

        return monthly.reset_index(
            drop=True
        )

    # ---------------------------------------------------------
    # Change calculations
    # ---------------------------------------------------------

    @staticmethod
    def calculate_period_change(
        series: pd.Series
    ) -> pd.DataFrame:
        """
        Calculate absolute and percentage
        period-over-period changes.
        """

        result = pd.DataFrame({
            "value": series
        })

        result["absolute_change"] = (
            result["value"].diff()
        )

        previous = (
            result["value"].shift(1)
        )

        result["percentage_change"] = (
            result["value"]
            .pct_change()
            .replace(
                [float("inf"), float("-inf")],
                pd.NA
            )
            * 100
        )

        # If the previous value is zero,
        # percentage change is undefined.
        result.loc[
            previous == 0,
            "percentage_change"
        ] = pd.NA

        return result

    def monthly_sales_with_change(
        self
    ) -> pd.DataFrame:
        """
        Monthly sales with period-over-period
        absolute and percentage changes.
        """

        monthly = self.monthly_sales()

        if monthly.empty:
            return monthly

        changes = self.calculate_period_change(
            monthly["sales"]
        )

        monthly["absolute_change"] = (
            changes["absolute_change"]
        )

        monthly["percentage_change"] = (
            changes["percentage_change"]
        )

        return monthly

    # ---------------------------------------------------------
    # Complete trend analysis
    # ---------------------------------------------------------

    def analyze(self) -> Dict[str, Any]:
        """
        Run the complete trend analysis.
        """

        coverage = self.date_coverage()

        daily_sales = self.daily_sales()

        daily_quantity = self.daily_quantity()

        monthly_sales = (
            self.monthly_sales_with_change()
        )

        monthly_quantity = (
            self.monthly_quantity()
        )

        return {
            "date_coverage": coverage,
            "daily_sales": daily_sales,
            "daily_quantity": daily_quantity,
            "monthly_sales": monthly_sales,
            "monthly_quantity": monthly_quantity
        }


# -------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------

def analyze_trends(
    df: pd.DataFrame,
    semantic_mapping: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for trend analysis.
    """

    analyzer = TrendAnalyzer(
        df=df,
        semantic_mapping=semantic_mapping
    )

    return analyzer.analyze()