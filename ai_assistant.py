
import json
import os

import pandas as pd
import streamlit as st
from groq import Groq


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )
    return Groq(api_key=api_key)


def _get_model():
    return os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b",
    )


def _column_schema(df):
    return [
        {
            "name": str(col),
            "dtype": str(df[col].dtype),
            "examples": [
                str(value)
                for value in df[col].dropna().head(3).tolist()
            ],
        }
        for col in df.columns
    ]


def _make_plan(question, df, history):
    """Ask Groq to translate the question into a constrained query plan."""
    client = _get_client()

    messages = [
        {
            "role": "system",
            "content": """
You translate questions about a CSV dataset into JSON query plans.

Return JSON only, using this schema:
{
  "aggregation": "sum|mean|count|nunique|minimum|maximum|rows",
  "metric_column": null,
  "date_column": null,
  "date_start": null,
  "date_end": null,
  "group_by": [],
  "filters": [
    {"column": "exact column name", "operator": "eq|contains|gt|gte|lt|lte", "value": "value"}
  ],
  "sort_by_metric": false,
  "limit": 10,
  "answer_type": "numeric|grouped|overview"
}

Rules:
- Use only the exact column names supplied by the user message.
- Never invent columns or data.
- For questions about a month, set date_start and date_end to the
  inclusive calendar dates, e.g. 2023-03-01 and 2023-03-31.
- Choose the date column that most plausibly represents the event date.
- For "sales", "revenue" or "total sales", choose the relevant monetary
  measure, not an ID or quantity column.
- For "how many orders", prefer a count of a genuine order identifier
  or rows only when each row represents one order.
- Use group_by for questions such as sales by region or product.
- Use filters for named categories, products, regions, or other criteria.
- Do not use a date range unless the question asks for one.
- If a requested field cannot be identified, use null and do not guess.
- limit must be between 1 and 20.
""",
        }
    ]

    # Keep recent conversational context for follow-up questions.
    for item in history[-6:]:
        if item.get("role") in {"user", "assistant"}:
            messages.append({
                "role": item["role"],
                "content": item["content"][:1500],
            })

    messages.append({
        "role": "user",
        "content": (
            f"Question: {question}\n\n"
            f"Dataset columns and examples:\n"
            f"{json.dumps(_column_schema(df), ensure_ascii=False)}"
        ),
    })

    response = client.chat.completions.create(
        model=_get_model(),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=700,
    )

    return json.loads(response.choices[0].message.content)


def _calculate_answer(df, plan):
    """Execute the query plan locally; never let the LLM calculate totals."""
    data = df.copy()

    aggregation = str(plan.get("aggregation", "rows")).lower()
    metric = plan.get("metric_column")
    date_column = plan.get("date_column")
    start = plan.get("date_start")
    end = plan.get("date_end")
    filters = plan.get("filters") or []
    group_by = plan.get("group_by") or []

    if start or end:
        if not date_column or date_column not in data.columns:
            raise ValueError(
                "I could not identify a valid date column for that question."
            )

        dates = pd.to_datetime(
            data[date_column],
            errors="coerce",
            dayfirst=True,
        )

        if start:
            data = data.loc[
                dates >= pd.Timestamp(start)
            ].copy()
            dates = dates.loc[data.index]

        if end:
            data = data.loc[
                dates < pd.Timestamp(end) + pd.Timedelta(days=1)
            ].copy()

    for condition in filters:
        if not isinstance(condition, dict):
            continue

        column = condition.get("column")
        operator = condition.get("operator")
        value = condition.get("value")

        if column not in data.columns:
            raise ValueError(
                f"The requested filter column '{column}' is unavailable."
            )

        series = data[column]

        if operator == "eq":
            mask = series.astype(str).str.casefold() == str(value).casefold()
        elif operator == "contains":
            mask = series.astype(str).str.contains(
                str(value), case=False, na=False, regex=False
            )
        elif operator in {"gt", "gte", "lt", "lte"}:
            numeric = pd.to_numeric(series, errors="coerce")
            try:
                target = float(value)
            except (TypeError, ValueError):
                raise ValueError(
                    f"The filter value for '{column}' is not numeric."
                )

            if operator == "gt":
                mask = numeric > target
            elif operator == "gte":
                mask = numeric >= target
            elif operator == "lt":
                mask = numeric < target
            else:
                mask = numeric <= target
        else:
            continue

        data = data.loc[mask].copy()

    if aggregation == "rows":
        result = {"matching_rows": int(len(data))}

    elif aggregation == "count":
        if metric and metric in data.columns:
            result = {"count": int(data[metric].count())}
        else:
            result = {"count": int(len(data))}

    elif aggregation == "nunique":
        if not metric or metric not in data.columns:
            raise ValueError("A valid column is required for unique counts.")
        result = {"unique_values": int(data[metric].nunique())}

    elif aggregation in {"sum", "mean", "minimum", "maximum"}:
        if not metric or metric not in data.columns:
            raise ValueError(
                "I could not identify the numeric column needed "
                "to answer that question."
            )

        numeric = pd.to_numeric(data[metric], errors="coerce").dropna()

        if numeric.empty:
            raise ValueError(
                f"Column '{metric}' contains no usable numeric values."
            )

        if aggregation == "sum":
            value = float(numeric.sum())
        elif aggregation == "mean":
            value = float(numeric.mean())
        elif aggregation == "minimum":
            value = float(numeric.min())
        else:
            value = float(numeric.max())

        result = {
            "metric": metric,
            "aggregation": aggregation,
            "value": value,
        }

    else:
        raise ValueError("I could not interpret that calculation.")

    if group_by:
        valid_groups = [
            column for column in group_by
            if column in data.columns
        ]

        if not valid_groups:
            raise ValueError(
                "The requested grouping columns were not found."
            )

        if aggregation in {"sum", "mean", "minimum", "maximum"}:
            if not metric or metric not in data.columns:
                raise ValueError("A valid numeric measure is required.")

            data[metric] = pd.to_numeric(data[metric], errors="coerce")
            grouped = (
                data.groupby(valid_groups, dropna=False)[metric]
                .agg(aggregation)
                .reset_index()
            )
            grouped = grouped.rename(columns={metric: aggregation})

            if plan.get("sort_by_metric"):
                grouped = grouped.sort_values(
                    aggregation, ascending=False
                )

        else:
            grouped = (
                data.groupby(valid_groups, dropna=False)
                .size()
                .reset_index(name="count")
            )

            if plan.get("sort_by_metric"):
                grouped = grouped.sort_values(
                    "count", ascending=False
                )

        limit = max(1, min(int(plan.get("limit", 10)), 20))
        result = {
            "groups": grouped.head(limit).to_dict(orient="records"),
            "group_columns": valid_groups,
            "matching_rows": int(len(data)),
        }

    return {
        "result": result,
        "rows_matched": int(len(data)),
        "columns_used": {
            "metric": metric,
            "date": date_column,
            "group_by": group_by,
        },
    }


def _explain_result(question, calculated, df):
    """Use Groq to explain the computed result without changing its values."""
    client = _get_client()

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a business intelligence assistant. Explain "
                    "the supplied calculated result clearly and concisely. "
                    "Use only the supplied result and dataset schema. "
                    "Do not invent values, trends, causes or recommendations. "
                    "Preserve all numeric values accurately. If no rows match, "
                    "say so. Mention the calculation's metric and period when "
                    "available. Do not claim the result is a forecast unless "
                    "the result explicitly says it is."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "calculated_result": calculated,
                        "dataset_columns": list(map(str, df.columns)),
                    },
                    default=str,
                    ensure_ascii=False,
                ),
            },
        ],
        temperature=0.1,
        max_tokens=350,
    )

    return response.choices[0].message.content.strip()


def render_ai_assistant(df, dataset_name="uploaded dataset"):
    """Render the expandable AI Assistant chat in Streamlit."""
    if "ai_assistant_open" not in st.session_state:
        st.session_state.ai_assistant_open = False

    if "ai_assistant_messages" not in st.session_state:
        st.session_state.ai_assistant_messages = []


    st.markdown(
    """
    <style>
    /* Floating AI Assistant button */
    div[class*="st-key-ai_assistant_toggle"] {
        position: fixed !important;
        right: 26px !important;
        bottom: 26px !important;
        z-index: 999999 !important;
        width: 230px !important;
        max-width: calc(100vw - 36px) !important;
        background: transparent !important;
        padding: 0 !important;
    }

    div[class*="st-key-ai_assistant_toggle"] button {
        width: 100% !important;
        min-height: 62px !important;
        border-radius: 36px !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
        background: linear-gradient(
            135deg,
            #52c7b5 0%,
            #00a3bd 100%
        ) !important;
        color: #ffffff !important;
        font-size: 17px !important;
        font-weight: 750 !important;
        box-shadow:
            0 5px 0 rgba(0, 90, 110, 0.55),
            0 12px 28px rgba(0, 140, 165, 0.35) !important;
        transition: transform 0.2s ease,
                    box-shadow 0.2s ease !important;
    }

    div[class*="st-key-ai_assistant_toggle"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow:
            0 7px 0 rgba(0, 90, 110, 0.45),
            0 16px 32px rgba(0, 140, 165, 0.4) !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
    }

    /* AI Assistant panel: make its text black */
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] label,
    div[data-testid="stVerticalBlockBorderWrapper"] small {
        color: #000000 !important;
    }

    /* Dataset name and introductory example text */
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] p {
        color: #000000 !important;
        opacity: 1 !important;
    }

    /* Keep the chat input and its placeholder readable */
    div[data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #374151 !important;
        -webkit-text-fill-color: #374151 !important;
        opacity: 1 !important;
    }

    @media (max-width: 600px) {
        div[class*="st-key-ai_assistant_toggle"] {
            right: 12px !important;
            bottom: 12px !important;
            width: 190px !important;
        }

        div[class*="st-key-ai_assistant_toggle"] button {
            min-height: 54px !important;
            font-size: 15px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    
    # Render exactly one floating assistant button.
    with st.container(key="ai_assistant_toggle"):
        if st.button(
            "✦  AI Assistant",
            key="ai_assistant_toggle_button",
            help="Ask questions about your uploaded dataset",
            use_container_width=True,
        ):
            st.session_state.ai_assistant_open = (
                not st.session_state.ai_assistant_open
            )

    if not st.session_state.ai_assistant_open:
        return

    with st.container(border=True):
        header_col, close_col = st.columns([5, 1])

        with header_col:
            st.subheader("✦ AI Assistant")
            st.caption(f"Ask questions about **{dataset_name}**")

        with close_col:
            if st.button("✕", key="ai_assistant_close"):
                st.session_state.ai_assistant_open = False
                st.rerun()

        if df is None or df.empty:
            st.info("Upload a CSV dataset before asking questions.")
            return

        st.caption(
            "Examples: monthly sales, top products, regional performance, "
            "average order value or number of orders."
        )

        for index, message in enumerate(
            st.session_state.ai_assistant_messages
        ):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("evidence"):
                    st.caption(message["evidence"])

        question = st.chat_input(
            "Ask a question about your dataset...",
            key="ai_assistant_chat_input",
        )

        if question:
            st.session_state.ai_assistant_messages.append({
                "role": "user",
                "content": question,
            })

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Checking your dataset..."):
                    try:
                        plan = _make_plan(
                            question,
                            df,
                            st.session_state.ai_assistant_messages[:-1],
                        )
                        calculated = _calculate_answer(df, plan)
                        answer = _explain_result(
                            question, calculated, df
                        )
                        evidence = (
                            f"Calculated from {calculated['rows_matched']:,} "
                            f"matching row(s)."
                        )

                        st.markdown(answer)
                        st.caption(evidence)

                        st.session_state.ai_assistant_messages.append({
                            "role": "assistant",
                            "content": answer,
                            "evidence": evidence,
                        })

                    except Exception as exc:
                        st.error(
                            "I couldn't answer that question reliably. "
                            "Check the API configuration and column names, "
                            "or try asking in a different way."
                        )
                        st.caption(f"Details: {type(exc).__name__}: {exc}")
                        st.session_state.ai_assistant_messages.append({
                            "role": "assistant",
                            "content": (
                                "I couldn't answer that question reliably. "
                                "Please try rephrasing it."
                            ),
                        })
