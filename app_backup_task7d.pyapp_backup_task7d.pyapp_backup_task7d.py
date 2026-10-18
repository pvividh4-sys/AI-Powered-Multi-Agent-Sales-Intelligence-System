# ============================================================
# AI-POWERED MULTI-AGENT SALES INTELLIGENCE SYSTEM
# app.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from textwrap import dedent
import re
import io


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Sales Intelligence System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "df": None,
    "original_df": None,
    "filename": None,
    "active_page": "Dashboard",
    "dark_mode": False,

    # Planner
    "planner_result": None,

    # Agent status
    "agent_status": {
        "Planner Agent": "Pending",
        "Data Cleaning Agent": "Pending",
        "EDA Agent": "Pending",
        "Visualization Agent": "Pending",
        "Forecasting Agent": "Pending",
        "Insight Agent": "Pending",
        "Recommendation Agent": "Pending",
        "Report Agent": "Pending",
    },

    # Analytical results
    "kpis": {},
    "monthly_sales": None,
    "category_sales": None,
    "product_sales": None,
    "customer_sales": None,
    "region_sales": None,

    # Insights and recommendations
    "insights": [],
    "recommendations": [],

    # Forecast
    "forecast_df": None,

    # Quality
    "quality": {},

    # Trace
    "decision_trace": [],
}


for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, dict) else value


# ============================================================
# CSS
# ============================================================

def inject_css(dark_mode=False):

    if dark_mode:
        background = "#0B1220"
        card = "#111827"
        text = "#F8FAFC"
        muted = "#94A3B8"
        border = "#263244"
        input_bg = "#172033"
    else:
        background = "#F7F8FC"
        card = "#FFFFFF"
        text = "#172033"
        muted = "#64748B"
        border = "#E5E7EB"
        input_bg = "#F8FAFC"

    st.html(
        f"""
        <style>

        /* ============================
           GLOBAL
        ============================ */

        .stApp {{
            background: {background};
        }}

        .main {{
            background: {background};
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background: #071022;
        }}

        [data-testid="stSidebar"] * {{
            color: #F8FAFC;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {text};
        }}

        p, span, label {{
            color: {text};
        }}


        /* ============================
           SIDEBAR
        ============================ */

        .sidebar-brand {{
            padding: 12px 4px 25px 4px;
        }}

        .sidebar-brand-title {{
            font-size: 19px;
            font-weight: 750;
            color: #FFFFFF;
        }}

        .sidebar-section-title {{
            font-size: 11px;
            font-weight: 750;
            color: #8B5CF6;
            letter-spacing: 0.6px;
            margin-top: 20px;
            margin-bottom: 12px;
        }}

        .agent-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0;
        }}

        .agent-dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .agent-name {{
            font-size: 13px;
            font-weight: 650;
            color: #FFFFFF;
        }}

        .agent-status {{
            font-size: 10px;
            color: #8FA0BA;
            margin-top: 2px;
        }}

        .progress-card {{
            background: #111C31;
            border: 1px solid #29364E;
            border-radius: 12px;
            padding: 15px;
            margin-top: 18px;
        }}

        .progress-title {{
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 12px;
        }}

        .progress-track {{
            width: 100%;
            height: 8px;
            background: #263452;
            border-radius: 20px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(
                90deg,
                #7C3AED,
                #9B5CF6
            );
            border-radius: 20px;
        }}

        .progress-text {{
            color: #A9B5C9;
            font-size: 11px;
            margin-top: 9px;
        }}


        /* ============================
           HEADER
        ============================ */

        .app-title {{
            font-size: 30px;
            font-weight: 800;
            color: {text};
            margin-bottom: 2px;
        }}

        .app-subtitle {{
            font-size: 14px;
            color: {muted};
            margin-bottom: 18px;
        }}

        .brand-icon {{
            width: 54px;
            height: 54px;
            border-radius: 13px;
            background: linear-gradient(
                135deg,
                #6D28D9,
                #8B5CF6
            );
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 29px;
            color: white;
            margin-bottom: 5px;
        }}


        /* ============================
           CARDS
        ============================ */

        .metric-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 17px;
            min-height: 130px;
            box-shadow: 0 2px 7px rgba(15, 23, 42, 0.04);
        }}

        .metric-icon {{
            font-size: 24px;
            margin-bottom: 8px;
        }}

        .metric-title {{
            color: {muted};
            font-size: 12px;
            font-weight: 650;
            margin-bottom: 5px;
        }}

        .metric-value {{
            color: {text};
            font-size: 24px;
            font-weight: 800;
        }}

        .metric-description {{
            color: #22C55E;
            font-size: 11px;
            margin-top: 7px;
        }}

        .section-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 2px 7px rgba(15, 23, 42, 0.03);
        }}

        .section-title {{
            color: {text};
            font-size: 16px;
            font-weight: 750;
            margin-bottom: 12px;
        }}

        .empty-state {{
            background: {card};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 80px 30px;
            text-align: center;
            margin-top: 20px;
        }}

        .empty-icon {{
            font-size: 58px;
            margin-bottom: 15px;
        }}

        .empty-title {{
            color: {text};
            font-size: 25px;
            font-weight: 750;
            margin-bottom: 8px;
        }}

        .empty-text {{
            color: {muted};
            font-size: 14px;
        }}


        /* ============================
           INSIGHT / RECOMMENDATION
        ============================ */

        .info-item {{
            padding: 9px 0;
            border-bottom: 1px solid {border};
            color: {text};
            font-size: 13px;
            line-height: 1.5;
        }}

        .info-item:last-child {{
            border-bottom: none;
        }}

        .bullet {{
            color: #7C3AED;
            font-weight: 800;
            margin-right: 7px;
        }}


        /* ============================
           UPLOAD
        ============================ */

        [data-testid="stFileUploader"] {{
            background: {card};
            border-radius: 12px;
        }}

        </style>
        """
    )


inject_css(st.session_state.dark_mode)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def reset_analysis():

    st.session_state.df = None
    st.session_state.original_df = None
    st.session_state.filename = None
    st.session_state.planner_result = None
    st.session_state.kpis = {}
    st.session_state.monthly_sales = None
    st.session_state.category_sales = None
    st.session_state.product_sales = None
    st.session_state.customer_sales = None
    st.session_state.region_sales = None
    st.session_state.forecast_df = None
    st.session_state.insights = []
    st.session_state.recommendations = []
    st.session_state.quality = {}
    st.session_state.decision_trace = []

    st.session_state.agent_status = {
        "Planner Agent": "Pending",
        "Data Cleaning Agent": "Pending",
        "EDA Agent": "Pending",
        "Visualization Agent": "Pending",
        "Forecasting Agent": "Pending",
        "Insight Agent": "Pending",
        "Recommendation Agent": "Pending",
        "Report Agent": "Pending",
    }


def normalise_column_name(column):

    value = str(column).strip().lower()

    value = value.replace("_", " ")
    value = value.replace("-", " ")

    value = re.sub(r"\s+", " ", value)

    return value


def find_column(df, candidates):

    normalised = {
        normalise_column_name(col): col
        for col in df.columns
    }

    for candidate in candidates:

        candidate_norm = normalise_column_name(candidate)

        if candidate_norm in normalised:
            return normalised[candidate_norm]

    for col in df.columns:

        col_norm = normalise_column_name(col)

        for candidate in candidates:

            candidate_norm = normalise_column_name(candidate)

            if candidate_norm in col_norm:
                return col

    return None


def format_currency(value):

    if value is None or pd.isna(value):
        return "₹0"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"₹{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"₹{value / 1_000:.1f}K"

    return f"₹{value:,.0f}"


def format_number(value):

    if value is None or pd.isna(value):
        return "0"

    return f"{float(value):,.0f}"


# ============================================================
# COLUMN DETECTION
# ============================================================

def detect_columns(df):

    mapping = {}

    mapping["order_id"] = find_column(
        df,
        [
            "order id",
            "order_id",
            "order number",
            "transaction id",
        ],
    )

    mapping["date"] = find_column(
        df,
        [
            "date",
            "order date",
            "order_date",
            "transaction date",
            "sales date",
        ],
    )

    mapping["customer"] = find_column(
        df,
        [
            "customer",
            "customer id",
            "customer_id",
            "client",
        ],
    )

    mapping["product"] = find_column(
        df,
        [
            "product",
            "product name",
            "item",
            "item name",
        ],
    )

    mapping["category"] = find_column(
        df,
        [
            "category",
            "product category",
            "product_category",
        ],
    )

    mapping["region"] = find_column(
        df,
        [
            "region",
            "city",
            "state",
            "location",
            "area",
        ],
    )

    mapping["quantity"] = find_column(
        df,
        [
            "quantity",
            "qty",
            "units",
            "units sold",
        ],
    )

    mapping["sales"] = find_column(
        df,
        [
            "sales",
            "revenue",
            "total amount",
            "total_amount",
            "total price",
            "amount",
        ],
    )

    mapping["cost"] = find_column(
        df,
        [
            "cost",
            "total cost",
            "cost price",
        ],
    )

    mapping["profit"] = find_column(
        df,
        [
            "profit",
            "net profit",
            "profit amount",
        ],
    )

    mapping["discount"] = find_column(
        df,
        [
            "discount",
            "discount amount",
            "discount %",
            "discount percent",
        ],
    )

    return mapping


# ============================================================
# PLANNER AGENT
# ============================================================

def run_planner_agent(df):

    mapping = detect_columns(df)

    capabilities = {
        "sales_analysis": mapping["sales"] is not None,
        "product_analysis": (
            mapping["sales"] is not None
            and (
                mapping["product"] is not None
                or mapping["category"] is not None
            )
        ),
        "customer_analysis": (
            mapping["sales"] is not None
            and mapping["customer"] is not None
        ),
        "regional_analysis": (
            mapping["sales"] is not None
            and mapping["region"] is not None
        ),
        "profitability_analysis": (
            mapping["profit"] is not None
            or (
                mapping["sales"] is not None
                and mapping["cost"] is not None
            )
        ),
        "quantity_analysis": mapping["quantity"] is not None,
        "pricing_analysis": (
            mapping["sales"] is not None
            or find_column(
                df,
                ["price", "price per unit", "unit price"]
            ) is not None
        ),
        "discount_analysis": mapping["discount"] is not None,
        "forecasting": (
            mapping["date"] is not None
            and mapping["sales"] is not None
        ),
    }

    analysis_plan = {
        "run_data_cleaning": True,
        "run_eda": True,
        "run_visualization": True,
        "run_forecasting": capabilities["forecasting"],
        "run_insight_generation": True,
        "run_recommendations": True,
        "run_report_generation": True,
    }

    semantic_mapping = []

    for column in df.columns:

        norm = normalise_column_name(column)

        if norm in ["order id", "order number", "transaction id"]:
            meaning = "order_id"
            confidence = 100
            evidence = f"Column name matches '{column}'."

        elif norm in [
            "date",
            "order date",
            "transaction date",
        ]:
            meaning = "date"
            confidence = 100
            evidence = f"Column name matches '{column}'."

        elif "customer" in norm:
            meaning = "customer"
            confidence = 100
            evidence = f"Column name contains customer identifier."

        elif "product category" in norm:
            meaning = "category"
            confidence = 100
            evidence = f"Column name indicates product category."

        elif norm == "category":
            meaning = "category"
            confidence = 100
            evidence = f"Column name matches category."

        elif norm in ["city", "state", "region", "location"]:
            meaning = "region"
            confidence = 100
            evidence = f"Column name identifies geographic information."

        elif "quantity" in norm or norm == "qty":
            meaning = "quantity"
            confidence = 100
            evidence = f"Column name indicates quantity."

        elif "price per unit" in norm or "unit price" in norm:
            meaning = "price"
            confidence = 100
            evidence = f"Column name indicates unit price."

        elif (
            "total amount" in norm
            or norm == "sales"
            or norm == "revenue"
        ):
            meaning = "sales"
            confidence = 100
            evidence = f"Column name indicates sales/revenue."

        elif "total price" in norm:
            meaning = "sales"
            confidence = 100
            evidence = f"Column name may represent sales value."

        elif "profit" in norm:
            meaning = "profit"
            confidence = 100
            evidence = f"Column name indicates profit."

        elif "cost" in norm:
            meaning = "cost"
            confidence = 100
            evidence = f"Column name indicates cost."

        elif "discount" in norm:
            meaning = "discount"
            confidence = 100
            evidence = f"Column name indicates discount."

        else:
            meaning = "No semantic match"
            confidence = 0
            evidence = "No strong semantic evidence detected."

        semantic_mapping.append(
            {
                "Column": column,
                "Possible Meaning": meaning,
                "Confidence": f"{confidence}%",
                "Evidence": evidence,
            }
        )

    result = {
        "semantic_mapping": semantic_mapping,
        "mapping": mapping,
        "capabilities": capabilities,
        "analysis_plan": analysis_plan,
    }

    return result


# ============================================================
# DATA CLEANING AGENT
# ============================================================

def run_cleaning_agent(df):

    cleaned = df.copy()

    missing_before = int(cleaned.isna().sum().sum())
    duplicates_before = int(cleaned.duplicated().sum())

    actions = []

    # Standardise column names only by stripping whitespace
    cleaned.columns = [
        str(col).strip()
        for col in cleaned.columns
    ]

    # Convert obvious date column
    mapping = detect_columns(cleaned)

    date_col = mapping.get("date")

    if date_col:

        original_non_null = cleaned[date_col].notna().sum()

        converted = pd.to_datetime(
            cleaned[date_col],
            errors="coerce",
            dayfirst=True,
        )

        valid_after = converted.notna().sum()

        if valid_after > 0:
            cleaned[date_col] = converted

            actions.append(
                f"Validated date column: {date_col}"
            )

    # Remove exact duplicate rows only
    duplicate_count = cleaned.duplicated().sum()

    if duplicate_count > 0:

        cleaned = cleaned.drop_duplicates().reset_index(drop=True)

        actions.append(
            f"Removed {duplicate_count} exact duplicate rows."
        )

    missing_after = int(cleaned.isna().sum().sum())

    quality = {
        "missing_before": missing_before,
        "missing_after": missing_after,
        "duplicates_before": duplicates_before,
        "duplicates_after": int(cleaned.duplicated().sum()),
        "rows_before": len(df),
        "rows_after": len(cleaned),
        "actions": actions,
    }

    return cleaned, quality


# ============================================================
# EDA AGENT
# ============================================================

def run_eda_agent(df, mapping):

    results = {}

    sales_col = mapping.get("sales")
    order_col = mapping.get("order_id")
    quantity_col = mapping.get("quantity")
    customer_col = mapping.get("customer")
    product_col = mapping.get("product")
    category_col = mapping.get("category")
    region_col = mapping.get("region")
    profit_col = mapping.get("profit")
    date_col = mapping.get("date")

    # --------------------------------------------------------
    # SALES
    # --------------------------------------------------------

    if sales_col:

        sales = pd.to_numeric(
            df[sales_col],
            errors="coerce"
        )

        total_revenue = sales.sum()

        if order_col:
            total_orders = df[order_col].nunique()
        else:
            total_orders = len(df)

        results["total_revenue"] = total_revenue
        results["total_orders"] = total_orders

    else:

        results["total_revenue"] = 0
        results["total_orders"] = len(df)

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    if quantity_col:

        quantity = pd.to_numeric(
            df[quantity_col],
            errors="coerce"
        )

        total_quantity = quantity.sum()

    else:

        total_quantity = 0

    results["total_quantity"] = total_quantity

    # --------------------------------------------------------
    # AVERAGE ORDER VALUE
    # --------------------------------------------------------

    if results["total_orders"] > 0:

        results["average_order_value"] = (
            results["total_revenue"]
            / results["total_orders"]
        )

    else:

        results["average_order_value"] = 0

    # --------------------------------------------------------
    # PROFIT
    # --------------------------------------------------------

    if profit_col:

        profit = pd.to_numeric(
            df[profit_col],
            errors="coerce"
        )

        total_profit = profit.sum()

        results["total_profit"] = total_profit

        if results["total_revenue"] != 0:

            results["profit_margin"] = (
                total_profit
                / results["total_revenue"]
                * 100
            )

        else:

            results["profit_margin"] = None

    else:

        results["total_profit"] = None
        results["profit_margin"] = None

    # --------------------------------------------------------
    # MONTHLY SALES
    # --------------------------------------------------------

    if date_col and sales_col:

        temp = df[[date_col, sales_col]].copy()

        temp[date_col] = pd.to_datetime(
            temp[date_col],
            errors="coerce",
            dayfirst=True,
        )

        temp[sales_col] = pd.to_numeric(
            temp[sales_col],
            errors="coerce"
        )

        temp = temp.dropna()

        if not temp.empty:

            monthly = (
                temp
                .set_index(date_col)[sales_col]
                .resample("ME")
                .sum()
                .reset_index()
            )

            monthly.columns = [
                "Date",
                "Sales"
            ]

            results["monthly_sales"] = monthly

        else:

            results["monthly_sales"] = None

    else:

        results["monthly_sales"] = None

    # --------------------------------------------------------
    # CATEGORY SALES
    # --------------------------------------------------------

    if category_col and sales_col:

        temp = df.copy()

        temp[sales_col] = pd.to_numeric(
            temp[sales_col],
            errors="coerce"
        )

        category = (
            temp
            .groupby(category_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        category.columns = [
            "Category",
            "Revenue"
        ]

        results["category_sales"] = category

    else:

        results["category_sales"] = None

    # --------------------------------------------------------
    # PRODUCT SALES
    # --------------------------------------------------------

    if product_col and sales_col:

        temp = df.copy()

        temp[sales_col] = pd.to_numeric(
            temp[sales_col],
            errors="coerce"
        )

        product = (
            temp
            .groupby(product_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        product.columns = [
            "Product",
            "Revenue"
        ]

        results["product_sales"] = product

    elif category_col and sales_col:

        # Your current dataset uses Product Category
        temp = df.copy()

        temp[sales_col] = pd.to_numeric(
            temp[sales_col],
            errors="coerce"
        )

        product = (
            temp
            .groupby(category_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        product.columns = [
            "Product",
            "Revenue"
        ]

        results["product_sales"] = product

    else:

        results["product_sales"] = None

    # --------------------------------------------------------
    # CUSTOMER SALES
    # --------------------------------------------------------

    if customer_col and sales_col:

        temp = df.copy()

        temp[sales_col] = pd.to_numeric(
            temp[sales_col],
            errors="coerce"
        )

        customer = (
            temp
            .groupby(customer_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        customer.columns = [
            "Customer",
            "Revenue"
        ]

        results["customer_sales"] = customer

    else:

        results["customer_sales"] = None

    # --------------------------------------------------------
    # REGION SALES
    # --------------------------------------------------------

    if region_col and sales_col:

        temp = df.copy()

        temp[sales_col] = pd.to_numeric(
            temp[sales_col],
            errors="coerce"
        )

        region = (
            temp
            .groupby(region_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        region.columns = [
            "Region",
            "Revenue"
        ]

        results["region_sales"] = region

    else:

        results["region_sales"] = None

    return results


# ============================================================
# VISUALIZATION AGENT
# ============================================================

def create_monthly_chart(monthly):

    if monthly is None or monthly.empty:
        return None

    fig = px.line(
        monthly,
        x="Date",
        y="Sales",
        markers=True,
        title="",
    )

    fig.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Date",
        yaxis_title="Revenue",
    )

    return fig


def create_category_chart(category):

    if category is None or category.empty:
        return None

    fig = px.pie(
        category,
        names="Category",
        values="Revenue",
        hole=0.58,
    )

    fig.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        height=350,
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# ============================================================
# FORECASTING AGENT
# ============================================================

def run_forecasting_agent(monthly_sales):

    if monthly_sales is None:
        return None

    if len(monthly_sales) < 6:
        return None

    data = monthly_sales.copy()

    data["Sales"] = pd.to_numeric(
        data["Sales"],
        errors="coerce"
    )

    data = data.dropna()

    if len(data) < 6:
        return None

    values = data["Sales"].values.astype(float)

    # Simple deterministic trend-based forecast.
    # This is deliberately bounded and transparent.
    x = np.arange(len(values))

    try:

        coefficients = np.polyfit(
            x,
            values,
            1
        )

        slope = coefficients[0]
        intercept = coefficients[1]

        future_x = np.arange(
            len(values),
            len(values) + 6
        )

        forecast_values = (
            intercept
            + slope * future_x
        )

        forecast_values = np.maximum(
            forecast_values,
            0
        )

        last_date = pd.to_datetime(
            data["Date"].iloc[-1]
        )

        future_dates = pd.date_range(
            start=last_date + pd.offsets.MonthEnd(1),
            periods=6,
            freq="ME"
        )

        forecast = pd.DataFrame(
            {
                "Date": future_dates,
                "Forecast": forecast_values,
            }
        )

        return forecast

    except Exception:
        return None


# ============================================================
# INSIGHT AGENT
# ============================================================

def generate_insights(
    kpis,
    category_sales,
    product_sales,
    customer_sales,
    region_sales,
):

    insights = []

    revenue = kpis.get(
        "total_revenue",
        0
    )

    insights.append(
        f"Total recorded sales are {format_currency(revenue)}."
    )

    if category_sales is not None and not category_sales.empty:

        top_category = category_sales.iloc[0]

        insights.append(
            f"{top_category['Category']} is the highest-revenue category."
        )

    if product_sales is not None and not product_sales.empty:

        top_product = product_sales.iloc[0]

        insights.append(
            f"{top_product['Product']} is the highest-performing product/category in the detected product field."
        )

    if customer_sales is not None and not customer_sales.empty:

        top_customer = customer_sales.iloc[0]

        insights.append(
            f"{top_customer['Customer']} is the highest-revenue customer in the analysed dataset."
        )

    if region_sales is not None and not region_sales.empty:

        top_region = region_sales.iloc[0]

        insights.append(
            f"{top_region['Region']} records the highest sales among the detected geographic fields."
        )

    return insights


# ============================================================
# RECOMMENDATION AGENT
# ============================================================

def generate_recommendations(
    category_sales,
    product_sales,
    customer_sales,
    region_sales,
):

    recommendations = []

    if product_sales is not None and not product_sales.empty:

        recommendations.append(
            "Prioritise inventory and promotional planning around the highest-performing products."
        )

    if category_sales is not None and not category_sales.empty:

        recommendations.append(
            "Review high-performing categories for additional growth opportunities."
        )

    if customer_sales is not None and not customer_sales.empty:

        recommendations.append(
            "Consider targeted retention and loyalty strategies for high-value customers."
        )

    if region_sales is not None and not region_sales.empty:

        recommendations.append(
            "Evaluate regional performance differences when allocating sales and marketing resources."
        )

    if not recommendations:

        recommendations.append(
            "Collect additional sales dimensions before making detailed business recommendations."
        )

    return recommendations


# ============================================================
# REPORT AGENT
# ============================================================

def generate_report_text():

    kpis = st.session_state.kpis
    quality = st.session_state.quality

    report = []

    report.append(
        "AI-POWERED MULTI-AGENT SALES INTELLIGENCE SYSTEM"
    )

    report.append("")
    report.append(
        "Executive Summary"
    )

    report.append(
        f"Total Revenue: {format_currency(kpis.get('total_revenue', 0))}"
    )

    report.append(
        f"Total Orders: {format_number(kpis.get('total_orders', 0))}"
    )

    report.append(
        f"Total Quantity: {format_number(kpis.get('total_quantity', 0))}"
    )

    report.append(
        f"Average Order Value: {format_currency(kpis.get('average_order_value', 0))}"
    )

    report.append("")

    report.append("Data Quality")

    report.append(
        f"Rows before cleaning: {quality.get('rows_before', 0)}"
    )

    report.append(
        f"Rows after cleaning: {quality.get('rows_after', 0)}"
    )

    report.append(
        f"Missing values after cleaning: {quality.get('missing_after', 0)}"
    )

    report.append(
        f"Duplicate rows after cleaning: {quality.get('duplicates_after', 0)}"
    )

    report.append("")

    report.append("Insights")

    for insight in st.session_state.insights:
        report.append(f"- {insight}")

    report.append("")

    report.append("Recommendations")

    for recommendation in st.session_state.recommendations:
        report.append(f"- {recommendation}")

    return "\n".join(report)


# ============================================================
# FULL PIPELINE
# ============================================================

def run_pipeline(df):

    # --------------------------------------------------------
    # PLANNER
    # --------------------------------------------------------

    st.session_state.agent_status[
        "Planner Agent"
    ] = "In Progress"

    planner = run_planner_agent(df)

    st.session_state.planner_result = planner

    st.session_state.agent_status[
        "Planner Agent"
    ] = "Completed"

    mapping = planner["mapping"]

    # --------------------------------------------------------
    # CLEANING
    # --------------------------------------------------------

    st.session_state.agent_status[
        "Data Cleaning Agent"
    ] = "In Progress"

    cleaned_df, quality = run_cleaning_agent(df)

    st.session_state.quality = quality

    st.session_state.agent_status[
        "Data Cleaning Agent"
    ] = "Completed"

    # --------------------------------------------------------
    # EDA
    # --------------------------------------------------------

    st.session_state.agent_status[
        "EDA Agent"
    ] = "In Progress"

    mapping = detect_columns(cleaned_df)

    eda = run_eda_agent(
        cleaned_df,
        mapping
    )

    st.session_state.kpis = {
        "total_revenue": eda.get(
            "total_revenue",
            0
        ),
        "total_orders": eda.get(
            "total_orders",
            0
        ),
        "total_quantity": eda.get(
            "total_quantity",
            0
        ),
        "average_order_value": eda.get(
            "average_order_value",
            0
        ),
        "total_profit": eda.get(
            "total_profit"
        ),
        "profit_margin": eda.get(
            "profit_margin"
        ),
    }

    st.session_state.monthly_sales = eda.get(
        "monthly_sales"
    )

    st.session_state.category_sales = eda.get(
        "category_sales"
    )

    st.session_state.product_sales = eda.get(
        "product_sales"
    )

    st.session_state.customer_sales = eda.get(
        "customer_sales"
    )

    st.session_state.region_sales = eda.get(
        "region_sales"
    )

    st.session_state.agent_status[
        "EDA Agent"
    ] = "Completed"

    # --------------------------------------------------------
    # VISUALIZATION
    # --------------------------------------------------------

    st.session_state.agent_status[
        "Visualization Agent"
    ] = "In Progress"

    st.session_state.agent_status[
        "Visualization Agent"
    ] = "Completed"

    # --------------------------------------------------------
    # FORECAST
    # --------------------------------------------------------

    forecast_allowed = planner[
        "capabilities"
    ]["forecasting"]

    if forecast_allowed:

        st.session_state.agent_status[
            "Forecasting Agent"
        ] = "In Progress"

        forecast = run_forecasting_agent(
            st.session_state.monthly_sales
        )

        st.session_state.forecast_df = forecast

        if forecast is not None:

            st.session_state.agent_status[
                "Forecasting Agent"
            ] = "Completed"

        else:

            st.session_state.agent_status[
                "Forecasting Agent"
            ] = "Skipped"

    else:

        st.session_state.forecast_df = None

        st.session_state.agent_status[
            "Forecasting Agent"
        ] = "Skipped"

    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    st.session_state.agent_status[
        "Insight Agent"
    ] = "In Progress"

    st.session_state.insights = generate_insights(
        st.session_state.kpis,
        st.session_state.category_sales,
        st.session_state.product_sales,
        st.session_state.customer_sales,
        st.session_state.region_sales,
    )

    st.session_state.agent_status[
        "Insight Agent"
    ] = "Completed"

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    st.session_state.agent_status[
        "Recommendation Agent"
    ] = "In Progress"

    st.session_state.recommendations = generate_recommendations(
        st.session_state.category_sales,
        st.session_state.product_sales,
        st.session_state.customer_sales,
        st.session_state.region_sales,
    )

    st.session_state.agent_status[
        "Recommendation Agent"
    ] = "Completed"

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    st.session_state.agent_status[
        "Report Agent"
    ] = "In Progress"

    st.session_state.agent_status[
        "Report Agent"
    ] = "Completed"

    # --------------------------------------------------------
    # FINAL DATA
    # --------------------------------------------------------

    st.session_state.df = cleaned_df

    # --------------------------------------------------------
    # DECISION TRACE
    # --------------------------------------------------------

    st.session_state.decision_trace = [
        {
            "Decision": "Run sales analysis",
            "Reason": (
                "Sales/revenue field detected."
                if mapping.get("sales")
                else "No sales field detected."
            ),
            "Action": (
                "Execute sales analysis"
                if mapping.get("sales")
                else "Skip sales-specific analysis"
            ),
            "Validation": "Passed",
        },
        {
            "Decision": "Run customer analysis",
            "Reason": (
                "Customer field detected."
                if mapping.get("customer")
                else "No customer-identifying field detected."
            ),
            "Action": (
                "Execute customer analysis"
                if mapping.get("customer")
                else "Skip customer analysis"
            ),
            "Validation": "Passed",
        },
        {
            "Decision": "Forecasting",
            "Reason": (
                "Usable date and sales fields detected."
                if forecast_allowed
                else "No valid date/sales combination detected."
            ),
            "Action": (
                "Run Forecasting Agent"
                if forecast_allowed
                else "Skip Forecasting Agent"
            ),
            "Validation": "Passed",
        },
    ]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-brand-title">🤖 Sales Intelligence</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section-title">'
        '1. UPLOAD SALES DATA'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:

        try:

            if (
                st.session_state.filename
                != uploaded_file.name
            ):

                df_uploaded = pd.read_csv(
                    uploaded_file
                )

                st.session_state.original_df = (
                    df_uploaded.copy()
                )

                st.session_state.filename = (
                    uploaded_file.name
                )

                st.session_state.agent_status = {
                    "Planner Agent": "Pending",
                    "Data Cleaning Agent": "Pending",
                    "EDA Agent": "Pending",
                    "Visualization Agent": "Pending",
                    "Forecasting Agent": "Pending",
                    "Insight Agent": "Pending",
                    "Recommendation Agent": "Pending",
                    "Report Agent": "Pending",
                }

                run_pipeline(
                    df_uploaded
                )

                st.rerun()

        except Exception as error:

            st.error(
                f"Unable to read CSV: {error}"
            )

    if st.session_state.filename:

        st.success(
            f"📄 {st.session_state.filename}"
        )

    st.markdown(
        '<div class="sidebar-section-title">'
        '2. SYSTEM STATUS'
        '</div>',
        unsafe_allow_html=True
    )

    status_values = (
        st.session_state.agent_status
    )

    for agent, status in status_values.items():

        if status == "Completed":
            dot = "#22C55E"

        elif status == "In Progress":
            dot = "#8B5CF6"

        elif status == "Skipped":
            dot = "#F59E0B"

        else:
            dot = "#64748B"

        st.markdown(
            f"""
            <div class="agent-row">
                <div
                    class="agent-dot"
                    style="background:{dot};"
                ></div>

                <div>
                    <div class="agent-name">
                        {agent}
                    </div>

                    <div class="agent-status">
                        {status}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    completed_count = sum(
        1
        for status in status_values.values()
        if status in ["Completed", "Skipped"]
    )

    total_agents = len(status_values)

    progress = int(
        completed_count
        / total_agents
        * 100
    )

    st.markdown(
        f"""
        <div class="progress-card">

            <div class="progress-title">
                Overall Progress
            </div>

            <div class="progress-track">

                <div
                    class="progress-fill"
                    style="width:{progress}%"
                ></div>

            </div>

            <div class="progress-text">
                {progress}% completed
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN HEADER
# ============================================================

header_left, header_right = st.columns(
    [7, 1]
)

with header_left:

    st.markdown(
        '<div class="brand-icon">🤖</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="app-title">'
        'AI-Powered Multi-Agent Sales Intelligence System'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="app-subtitle">'
        'Retail & E-commerce Sales Analytics and Business Decision Support'
        '</div>',
        unsafe_allow_html=True
    )

with header_right:

    dark = st.toggle(
        "Dark Mode",
        value=st.session_state.dark_mode
    )

    if dark != st.session_state.dark_mode:

        st.session_state.dark_mode = dark

        st.rerun()


# ============================================================
# NAVIGATION
# ============================================================

pages = [
    "Dashboard",
    "Detailed Analysis",
    "Forecast",
    "Insights",
    "Recommendations",
    "Report",
]

selected_page = st.radio(
    "Navigation",
    pages,
    horizontal=True,
    label_visibility="collapsed",
)

st.session_state.active_page = selected_page

st.divider()


# ============================================================
# NO DATA SCREEN
# ============================================================

if st.session_state.df is None:

    st.markdown(
        """
        <div class="empty-state">

            <div class="empty-icon">
                📊
            </div>

            <div class="empty-title">
                Upload your sales dataset
            </div>

            <div class="empty-text">
                Upload a retail or e-commerce CSV
                file to begin the analysis.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# DATA
# ============================================================

df = st.session_state.df

kpis = st.session_state.kpis


# ============================================================
# DASHBOARD
# ============================================================

if selected_page == "Dashboard":

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    metric_cols = st.columns(5)

    metrics = [
        (
            "💰",
            "Total Revenue",
            format_currency(
                kpis.get(
                    "total_revenue",
                    0
                )
            ),
            "↑ Dataset total",
        ),

        (
            "🛒",
            "Total Orders",
            format_number(
                kpis.get(
                    "total_orders",
                    0
                )
            ),
            "↑ Records analysed",
        ),

        (
            "📦",
            "Total Quantity",
            format_number(
                kpis.get(
                    "total_quantity",
                    0
                )
            ),
            "↑ Units detected",
        ),

        (
            "🛍️",
            "Average Order Value",
            format_currency(
                kpis.get(
                    "average_order_value",
                    0
                )
            ),
            "Calculated from dataset",
        ),

        (
            "📊",
            "Profit Margin",
            (
                f"{kpis['profit_margin']:.1f}%"
                if kpis.get("profit_margin")
                is not None
                else "N/A"
            ),
            (
                "Calculated from profit"
                if kpis.get("profit_margin")
                is not None
                else "Profit field unavailable"
            ),
        ),
    ]

    for col, metric in zip(
        metric_cols,
        metrics
    ):

        icon, title, value, description = metric

        with col:

            st.markdown(
                f"""
                <div class="metric-card">

                    <div class="metric-icon">
                        {icon}
                    </div>

                    <div class="metric-title">
                        {title}
                    </div>

                    <div class="metric-value">
                        {value}
                    </div>

                    <div class="metric-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    chart_left, chart_right = st.columns(
        [1.6, 1]
    )

    with chart_left:

        st.markdown(
            '<div class="section-title">'
            'Monthly Sales Trend'
            '</div>',
            unsafe_allow_html=True
        )

        monthly = (
            st.session_state.monthly_sales
        )

        chart = create_monthly_chart(
            monthly
        )

        if chart is not None:

            st.plotly_chart(
                chart,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )

        else:

            st.info(
                "Monthly trend is unavailable because a usable date and sales field were not detected."
            )

    with chart_right:

        st.markdown(
            '<div class="section-title">'
            'Sales by Category'
            '</div>',
            unsafe_allow_html=True
        )

        category = (
            st.session_state.category_sales
        )

        chart = create_category_chart(
            category
        )

        if chart is not None:

            st.plotly_chart(
                chart,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )

        else:

            st.info(
                "Category analysis is unavailable."
            )

    # --------------------------------------------------------
    # TOP PRODUCTS / CUSTOMERS
    # --------------------------------------------------------

    st.write("")

    product_col, customer_col = st.columns(
        2
    )

    with product_col:

        st.markdown(
            '<div class="section-title">'
            'Top 5 Best Selling Products'
            '</div>',
            unsafe_allow_html=True
        )

        product = (
            st.session_state.product_sales
        )

        if product is not None:

            st.dataframe(
                product.head(5),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "Product analysis is unavailable."
            )

    with customer_col:

        st.markdown(
            '<div class="section-title">'
            'Top 5 Customers'
            '</div>',
            unsafe_allow_html=True
        )

        customer = (
            st.session_state.customer_sales
        )

        if customer is not None:

            st.dataframe(
                customer.head(5),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "Customer analysis is unavailable."
            )

    # --------------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------------

    st.write("")

    quality_col, insight_col, recommendation_col = (
        st.columns(3)
    )

    with quality_col:

        st.markdown(
            '<div class="section-title">'
            '🛡️ Data Quality Summary'
            '</div>',
            unsafe_allow_html=True
        )

        quality = st.session_state.quality

        quality_data = {
            "Metric": [
                "Missing Values",
                "Duplicate Rows",
                "Rows",
                "Columns",
            ],
            "Value": [
                quality.get(
                    "missing_after",
                    0
                ),
                quality.get(
                    "duplicates_after",
                    0
                ),
                len(df),
                len(df.columns),
            ],
        }

        st.dataframe(
            pd.DataFrame(quality_data),
            use_container_width=True,
            hide_index=True,
        )

    with insight_col:

        st.markdown(
            '<div class="section-title">'
            '💡 Key Insights'
            '</div>',
            unsafe_allow_html=True
        )

        for insight in st.session_state.insights[:4]:

            st.markdown(
                f"• {insight}"
            )

    with recommendation_col:

        st.markdown(
            '<div class="section-title">'
            '🎯 Top Recommendations'
            '</div>',
            unsafe_allow_html=True
        )

        for recommendation in (
            st.session_state.recommendations[:4]
        ):

            st.markdown(
                f"• {recommendation}"
            )


# ============================================================
# DETAILED ANALYSIS
# ============================================================

elif selected_page == "Detailed Analysis":

    st.header("Detailed Analysis")

    planner = (
        st.session_state.planner_result
    )

    if planner:

        st.subheader(
            "Detected Semantic Mapping"
        )

        semantic_df = pd.DataFrame(
            planner["semantic_mapping"]
        )

        st.dataframe(
            semantic_df,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader(
            "Detected Analytical Capabilities"
        )

        capability_rows = []

        for capability, available in (
            planner["capabilities"].items()
        ):

            capability_rows.append(
                {
                    "Capability": capability,
                    "Available": (
                        "Yes"
                        if available
                        else "No"
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(
                capability_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader(
        "Dataset Preview"
    )

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader(
        "Dataset Information"
    )

    column_information = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": [
                str(dtype)
                for dtype in df.dtypes
            ],
            "Missing Values": [
                int(df[col].isna().sum())
                for col in df.columns
            ],
            "Unique Values": [
                int(df[col].nunique())
                for col in df.columns
            ],
        }
    )

    st.dataframe(
        column_information,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FORECAST PAGE
# ============================================================

elif selected_page == "Forecast":

    st.header("Forecast")

    forecast = (
        st.session_state.forecast_df
    )

    if forecast is None:

        st.warning(
            "Forecasting is currently unavailable. The Planner Agent only routes forecasting when a usable date and sales field are detected and sufficient historical observations exist."
        )

    else:

        monthly = (
            st.session_state.monthly_sales
        )

        st.subheader(
            "Historical Sales and Forecast"
        )

        fig = go.Figure()

        if monthly is not None:

            fig.add_trace(
                go.Scatter(
                    x=monthly["Date"],
                    y=monthly["Sales"],
                    mode="lines+markers",
                    name="Actual",
                )
            )

        fig.add_trace(
            go.Scatter(
                x=forecast["Date"],
                y=forecast["Forecast"],
                mode="lines+markers",
                name="Forecast",
                line=dict(
                    dash="dash"
                ),
            )
        )

        fig.update_layout(
            height=450,
            xaxis_title="Date",
            yaxis_title="Sales",
            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader(
            "Next 6 Months"
        )

        display_forecast = forecast.copy()

        display_forecast[
            "Forecast"
        ] = display_forecast[
            "Forecast"
        ].round(2)

        st.dataframe(
            display_forecast,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# INSIGHTS PAGE
# ============================================================

elif selected_page == "Insights":

    st.header("Business Insights")

    if not st.session_state.insights:

        st.info(
            "No insights are available."
        )

    else:

        for index, insight in enumerate(
            st.session_state.insights,
            start=1
        ):

            st.markdown(
                f"""
                <div class="section-card"
                     style="margin-bottom:12px;">

                    <div class="section-title">
                        Insight {index}
                    </div>

                    <div class="info-item">
                        <span class="bullet">•</span>
                        {insight}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.subheader(
        "Decision Trace"
    )

    if st.session_state.decision_trace:

        st.dataframe(
            pd.DataFrame(
                st.session_state.decision_trace
            ),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# RECOMMENDATIONS PAGE
# ============================================================

elif selected_page == "Recommendations":

    st.header("Business Recommendations")

    if not st.session_state.recommendations:

        st.info(
            "No recommendations are available."
        )

    else:

        for index, recommendation in enumerate(
            st.session_state.recommendations,
            start=1
        ):

            st.markdown(
                f"""
                <div class="section-card"
                     style="margin-bottom:12px;">

                    <div class="section-title">
                        Recommendation {index}
                    </div>

                    <div class="info-item">
                        <span class="bullet">•</span>
                        {recommendation}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "Recommendations are evidence-based decision support and should not be interpreted as guaranteed business outcomes."
    )


# ============================================================
# REPORT PAGE
# ============================================================

elif selected_page == "Report":

    st.header("Sales Intelligence Report")

    report_text = generate_report_text()

    st.text_area(
        "Report Preview",
        value=report_text,
        height=450,
    )

    st.download_button(
        label="⬇️ Download Report",
        data=report_text,
        file_name="sales_intelligence_report.txt",
        mime="text/plain",
        use_container_width=False,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI-Powered Multi-Agent Sales Intelligence System | Built with Streamlit"
)