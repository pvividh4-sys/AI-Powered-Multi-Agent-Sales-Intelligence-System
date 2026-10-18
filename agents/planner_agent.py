import pandas as pd
import re
from typing import Dict, Any


class PlannerAgent:
    """
    Planner Agent

    Responsibilities:
    - Inspect dataset schema
    - Detect semantic columns
    - Determine analytical capabilities
    - Create an analysis plan
    - Determine forecasting eligibility
    """

    AGENT_NAME = "Planner Agent"

    def __init__(self):
        pass

    def normalize_column(self, column_name: str) -> str:
        """
        Convert column name into a normalized form
        for semantic matching.
        """
        return re.sub(
            r"[^a-z0-9]+",
            "_",
            str(column_name).strip().lower()
        ).strip("_")

    def detect_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect important business columns from the dataset.
        """

        columns = list(df.columns)

        normalized = {
            col: self.normalize_column(col)
            for col in columns
        }

        mapping = {}

        keyword_groups = {
            "date": [
                "date",
                "order_date",
                "sales_date",
                "transaction_date",
                "invoice_date",
                "timestamp"
            ],

            "sales": [
                "sales",
                "sale",
                "revenue",
                "amount",
                "total_amount",
                "total_price",
                "sales_amount",
                "revenue_amount"
            ],

            "quantity": [
                "quantity",
                "qty",
                "units",
                "unit_sold",
                "units_sold"
            ],

            "product": [
                "product",
                "product_name",
                "item",
                "item_name",
                "product_category",
                "category"
            ],

            "customer": [
                "customer",
                "customer_id",
                "customer_name",
                "client",
                "client_id"
            ],

            "region": [
                "region",
                "state",
                "city",
                "location",
                "territory"
            ],

            "profit": [
                "profit",
                "profit_amount",
                "net_profit",
                "gross_profit"
            ],

            "cost": [
                "cost",
                "cost_price",
                "purchase_cost"
            ],

            "order_id": [
                "order_id",
                "orderid",
                "invoice_id",
                "transaction_id"
            ]
        }

        for semantic_type, keywords in keyword_groups.items():

            candidates = []

            for column, norm_column in normalized.items():

                for keyword in keywords:

                    if (
                        norm_column == keyword
                        or keyword in norm_column
                    ):
                        candidates.append(column)
                        break

            if candidates:
                mapping[semantic_type] = {
                    "column": candidates[0],
                    "candidates": candidates,
                    "confidence": self.calculate_confidence(
                        candidates[0],
                        semantic_type
                    ),
                    "evidence": "Keyword-based semantic match"
                }

        return mapping

    def calculate_confidence(
        self,
        column: str,
        semantic_type: str
    ) -> float:
        """
        Calculate basic semantic confidence.

        Exact semantic names receive higher confidence.
        """

        normalized = self.normalize_column(column)

        exact_names = {
            "date": [
                "date",
                "order_date",
                "sales_date"
            ],
            "sales": [
                "sales",
                "revenue",
                "total_amount",
                "total_price"
            ],
            "quantity": [
                "quantity",
                "qty",
                "units"
            ],
            "product": [
                "product",
                "product_name",
                "product_category"
            ],
            "customer": [
                "customer",
                "customer_id",
                "customer_name"
            ],
            "region": [
                "region",
                "state",
                "city"
            ],
            "profit": [
                "profit",
                "profit_amount"
            ],
            "cost": [
                "cost",
                "cost_price"
            ],
            "order_id": [
                "order_id",
                "transaction_id"
            ]
        }

        if normalized in exact_names.get(semantic_type, []):
            return 0.95

        return 0.75

    def determine_capabilities(
        self,
        mapping: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Determine which analytical tasks are possible.
        """

        capabilities = {
            "sales_analysis": False,
            "quantity_analysis": False,
            "product_analysis": False,
            "customer_analysis": False,
            "regional_analysis": False,
            "profitability_analysis": False,
            "forecasting": False
        }

        if "sales" in mapping:
            capabilities["sales_analysis"] = True

        if "quantity" in mapping:
            capabilities["quantity_analysis"] = True

        if "product" in mapping:
            capabilities["product_analysis"] = True

        if "customer" in mapping:
            capabilities["customer_analysis"] = True

        if "region" in mapping:
            capabilities["regional_analysis"] = True

        if "profit" in mapping:
            capabilities["profitability_analysis"] = True

        if "date" in mapping and "sales" in mapping:
            capabilities["forecasting"] = True

        return capabilities

    def create_analysis_plan(
        self,
        capabilities: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Create conditional analysis plan.
        """

        plan = {
            "run_sales_analysis": capabilities["sales_analysis"],
            "run_quantity_analysis": capabilities["quantity_analysis"],
            "run_product_analysis": capabilities["product_analysis"],
            "run_customer_analysis": capabilities["customer_analysis"],
            "run_regional_analysis": capabilities["regional_analysis"],
            "run_profitability_analysis": capabilities[
                "profitability_analysis"
            ],
            "run_forecasting": capabilities["forecasting"],
            "run_visualization": True,
            "run_insights": True,
            "run_recommendations": True,
            "run_report": True
        }

        return plan

    def check_forecasting_eligibility(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform basic forecasting eligibility checks.
        """

        result = {
            "eligible": False,
            "reason": "",
            "date_column": None,
            "sales_column": None,
            "observations": 0
        }

        if "date" not in mapping:
            result["reason"] = "Date field unavailable."
            return result

        if "sales" not in mapping:
            result["reason"] = "Sales/revenue field unavailable."
            return result

        date_column = mapping["date"]["column"]
        sales_column = mapping["sales"]["column"]

        result["date_column"] = date_column
        result["sales_column"] = sales_column

        dates = pd.to_datetime(
            df[date_column],
            errors="coerce"
        )

        sales = pd.to_numeric(
            df[sales_column],
            errors="coerce"
        )

        valid = pd.DataFrame({
            "date": dates,
            "sales": sales
        }).dropna()

        result["observations"] = len(valid)

        if len(valid) < 12:
            result["reason"] = (
                "Insufficient valid observations for reliable forecasting."
            )
            return result

        if valid["date"].nunique() < 6:
            result["reason"] = (
                "Insufficient unique time periods for forecasting."
            )
            return result

        result["eligible"] = True
        result["reason"] = "Basic forecasting eligibility satisfied."

        return result

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute Planner Agent.
        """

        if df is None or df.empty:
            return {
                "agent": self.AGENT_NAME,
                "status": "failed",
                "error": "Dataset is empty."
            }

        mapping = self.detect_columns(df)

        capabilities = self.determine_capabilities(mapping)

        analysis_plan = self.create_analysis_plan(
            capabilities
        )

        forecasting = self.check_forecasting_eligibility(
            df,
            mapping
        )

        result = {
            "agent": self.AGENT_NAME,
            "status": "completed",
            "schema": {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": {
                    col: str(df[col].dtype)
                    for col in df.columns
                }
            },
            "semantic_mapping": mapping,
            "capabilities": capabilities,
            "analysis_plan": analysis_plan,
            "forecasting_eligibility": forecasting
        }

        return result


def planner_agent(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function.
    """

    agent = PlannerAgent()

    return agent.run(df)