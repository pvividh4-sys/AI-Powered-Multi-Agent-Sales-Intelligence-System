
from ai_assistant import render_ai_assistant
import streamlit as st

import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

from textwrap import dedent

from pathlib import Path


from dotenv import load_dotenv

# Load API keys and other settings from .env
load_dotenv()


from ai_assistant import render_ai_assistant
# ============================================================

# BACKEND WORKFLOW IMPORT

# ============================================================

from workflow.graph import (

    run_workflow,

    resume_workflow_after_cleaning,

)


# ============================================================

# PAGE CONFIGURATION

# ============================================================

st.set_page_config(

    page_title="AI Sales Intelligence System",

    page_icon="🤖",

    layout="wide",

    initial_sidebar_state="expanded"

)

# ============================================================

# CONSTANTS

# ============================================================



AGENT_NAMES = [

    "Planner Agent",

    "Data Cleaning Agent",

    "EDA Agent",

    "Visualization Agent",

    "Forecasting Agent",

    "Insight Agent",

    "Recommendation Agent",

    "Report Agent",

]





# ============================================================

# SESSION STATE

# ============================================================



if "df" not in st.session_state:

    st.session_state.df = None



if "file_name" not in st.session_state:

    st.session_state.file_name = None



if "workflow_state" not in st.session_state:

    st.session_state.workflow_state = None



if "workflow_serialized" not in st.session_state:

    st.session_state.workflow_serialized = None



if "current_page" not in st.session_state:

    st.session_state.current_page = "Dashboard"



if "dark_mode" not in st.session_state:

    st.session_state.dark_mode = False



if "analysis_running" not in st.session_state:

    st.session_state.analysis_running = False



if "workflow_error" not in st.session_state:

    st.session_state.workflow_error = None





# ============================================================

# HELPER: HTML RENDERING

# ============================================================



def render_html(html):

    """

    Safely render HTML without displaying raw HTML source.

    """

    html = dedent(html).strip()



    try:

        st.html(html)

    except AttributeError:

        st.markdown(html, unsafe_allow_html=True)





# ============================================================

# CSS

# ============================================================



def load_css(dark=False):



    if dark:

        background = "#0b1220"

        surface = "#111827"

        card = "#172033"

        text = "#f8fafc"

        muted = "#a7b0c0"

        border = "#273449"

        purple = "#7c3aed"

    else:

        background = "#f5f7fb"

        surface = "#ffffff"

        card = "#ffffff"

        text = "#172033"

        muted = "#64748b"

        border = "#e2e8f0"

        purple = "#6d3df5"



    css = f"""

    <style>



    /* -------------------------------------------------------

       GLOBAL

    ------------------------------------------------------- */



    .stApp {{

        background: {background};

        color: {text};

    }}



    [data-testid="stAppViewContainer"] {{

        background: {background};

    }}



    [data-testid="stHeader"] {{

        background: transparent;

    }}



    .block-container {{

        padding-top: 2rem;

        padding-bottom: 2rem;

        max-width: 1500px;

    }}





    /* -------------------------------------------------------

       SIDEBAR

    ------------------------------------------------------- */



    section[data-testid="stSidebar"] {{

        background: #071225;

    }}



    section[data-testid="stSidebar"] > div {{

        background: #071225;

    }}



    .sidebar-brand {{

        font-size: 20px;

        font-weight: 750;

        color: #ffffff;

        margin-bottom: 30px;

    }}



    .sidebar-section {{

        color: #9b6cff;

        font-size: 11px;

        font-weight: 800;

        letter-spacing: 0.5px;

        margin-top: 20px;

        margin-bottom: 12px;

        text-transform: uppercase;

    }}



    .agent-row {{

        display: flex;

        align-items: center;

        gap: 10px;

        padding: 8px 0;

        color: #ffffff;

    }}



    .agent-dot {{

        width: 9px;

        height: 9px;

        border-radius: 50%;

        background: #64748b;

        flex-shrink: 0;

    }}



    .agent-dot.completed {{

        background: #22c55e;

    }}



    .agent-dot.running {{

        background: #8b5cf6;

    }}



    .agent-dot.failed {{

        background: #ef4444;

    }}



    .agent-dot.skipped {{

        background: #f59e0b;

    }}



    .agent-name {{

        font-size: 12px;

        font-weight: 700;

        line-height: 1.1;

    }}



    .agent-status {{

        color: #9ca9bd;

        font-size: 10px;

        margin-top: 3px;

    }}



    .progress-card {{

        background: #111c31;

        border: 1px solid #26344d;

        border-radius: 12px;

        padding: 14px;

        margin-top: 20px;

    }}



    .progress-title {{

        color: white;

        font-size: 12px;

        font-weight: 750;

        margin-bottom: 10px;

    }}



    .progress-track {{

        width: 100%;

        height: 8px;

        border-radius: 20px;

        background: #283552;

        overflow: hidden;

    }}



    .progress-fill {{

        height: 100%;

        background: linear-gradient(90deg, #6d3df5, #985eff);

        border-radius: 20px;

    }}



    .progress-text {{

        color: #a7b0c0;

        font-size: 11px;

        margin-top: 8px;

    }}





    /* -------------------------------------------------------

       HEADER

    ------------------------------------------------------- */



    .brand-container {{

        display: flex;

        align-items: center;

        gap: 18px;

        margin-bottom: 6px;

    }}



    .brand-icon {{

        width: 58px;

        height: 58px;

        border-radius: 14px;

        background: linear-gradient(135deg, #6d3df5, #914fff);

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 28px;

    }}



    .brand-title {{

        font-size: 30px;

        font-weight: 800;

        color: {text};

        line-height: 1.2;

    }}



    .brand-subtitle {{

        color: {muted};

        font-size: 14px;

        margin-top: 5px;

    }}





    /* -------------------------------------------------------

       METRIC CARDS

    ------------------------------------------------------- */



    .metric-card {{

        background: {card};

        border: 1px solid {border};

        border-radius: 14px;

        padding: 18px;

        min-height: 150px;

        box-shadow: 0 2px 10px rgba(20, 30, 50, 0.04);

    }}



    .metric-icon {{

        font-size: 23px;

        margin-bottom: 10px;

    }}



    .metric-title {{

        color: {muted};

        font-size: 13px;

        font-weight: 650;

        margin-bottom: 6px;

    }}



    .metric-value {{

        color: {text};

        font-size: 27px;

        font-weight: 800;

        margin-bottom: 6px;

    }}



    .metric-description {{

        color: {muted};

        font-size: 11px;

    }}





    /* -------------------------------------------------------

       SECTION CARDS

    ------------------------------------------------------- */



    .section-card {{

        background: {surface};

        border: 1px solid {border};

        border-radius: 14px;

        padding: 18px;

        margin-bottom: 18px;

    }}



    .section-title {{

        color: {text};

        font-size: 16px;

        font-weight: 750;

        margin-bottom: 12px;

    }}





    /* -------------------------------------------------------

       EMPTY STATE

    ------------------------------------------------------- */



    .empty-card {{

        background: {surface};

        border: 1px solid {border};

        border-radius: 14px;

        min-height: 420px;

        display: flex;

        align-items: center;

        justify-content: center;

        text-align: center;

    }}



    .empty-icon {{

        font-size: 58px;

        margin-bottom: 20px;

    }}



    .empty-title {{

        color: {text};

        font-size: 26px;

        font-weight: 800;

        margin-bottom: 10px;

    }}



    .empty-text {{

        color: {muted};

        font-size: 14px;

    }}





    /* -------------------------------------------------------

       INFO CARDS

    ------------------------------------------------------- */



    .info-card {{

        background: {surface};

        border: 1px solid {border};

        border-radius: 14px;

        padding: 18px;

        min-height: 190px;

    }}



    .info-title {{

        color: {text};

        font-size: 15px;

        font-weight: 750;

        margin-bottom: 14px;

    }}



    .info-item {{

        color: {text};

        font-size: 13px;

        margin: 10px 0;

        line-height: 1.5;

    }}





    /* -------------------------------------------------------

       STATUS

    ------------------------------------------------------- */



    .status-success {{

        color: #22c55e;

        font-weight: 700;

    }}



    .status-warning {{

        color: #f59e0b;

        font-weight: 700;

    }}



    .status-error {{

        color: #ef4444;

        font-weight: 700;

    }}





    /* -------------------------------------------------------

       FOOTER

    ------------------------------------------------------- */



    .footer {{

        color: {muted};

        font-size: 11px;

        text-align: center;

        padding: 25px 0 10px 0;

        border-top: 1px solid {border};

        margin-top: 25px;

    }}



    </style>

    """



    st.markdown(css, unsafe_allow_html=True)





load_css(st.session_state.dark_mode)





# ============================================================

# WORKFLOW HELPERS

# ============================================================



def normalize_status(status):

    """

    Convert backend status values to UI-friendly labels.

    """

    if status is None:

        return "Pending"



    value = str(status).strip().lower()



    mapping = {

        "completed": "Completed",

        "complete": "Completed",

        "validated": "Validated",

        "running": "In Progress",

        "in_progress": "In Progress",

        "pending": "Pending",

        "failed": "Failed",

        "skipped": "Skipped",

        "initialised": "Pending",

        "initialized": "Pending",

    }



    return mapping.get(value, str(status).replace("_", " ").title())





def get_state_value(state, name, default=None):

    """

    Safely retrieve a WorkflowState attribute.

    """

    if state is None:

        return default



    try:

        return getattr(state, name)

    except Exception:

        return default





def get_agent_statuses(state):

    """

    Read actual agent statuses from WorkflowState.

    """

    statuses = {}



    if state is None:

        return {agent: "Pending" for agent in AGENT_NAMES}



    state_statuses = get_state_value(state, "agent_statuses", None)



    for agent in AGENT_NAMES:



        status = None



        if isinstance(state_statuses, dict):

            status = state_statuses.get(agent)



        if status is None:



            attribute_map = {

                "Planner Agent": "planner_status",

                "Data Cleaning Agent": "cleaning_status",

                "EDA Agent": "eda_status",

                "Visualization Agent": "visualization_status",

                "Forecasting Agent": "forecasting_status",

                "Insight Agent": "insight_status",

                "Recommendation Agent": "recommendation_status",

                "Report Agent": "report_status",

            }



            attr = attribute_map.get(agent)



            if attr:

                status = get_state_value(state, attr, None)



        statuses[agent] = normalize_status(status)



    return statuses





def workflow_completed(state):

    """

    Determine whether the complete workflow passed.

    """

    if state is None:

        return False



    status = str(

        get_state_value(state, "workflow_status", "")

    ).lower()



    errors = get_state_value(state, "errors", [])



    return status == "completed" and not errors





def get_progress(statuses):

    """

    Calculate workflow progress from actual agent statuses.

    """

    completed_values = {

        "Completed",

        "Validated",

        "Skipped",

    }



    completed = sum(

        1

        for status in statuses.values()

        if status in completed_values

    )



    total = len(statuses)



    if total == 0:

        return 0



    return int((completed / total) * 100)





def run_analysis(df):

    """

    Execute the real eight-agent backend workflow.

    """

    try:

        state = run_workflow(df)



        st.session_state.workflow_state = state

        st.session_state.workflow_error = None



        try:

            st.session_state.workflow_serialized = state.to_dict()

        except Exception:

            st.session_state.workflow_serialized = None



        return state



    except Exception as exc:



        st.session_state.workflow_state = None

        st.session_state.workflow_serialized = None

        st.session_state.workflow_error = str(exc)



        raise





def safe_dict(value):

    """

    Return a dictionary when possible.

    """

    if isinstance(value, dict):

        return value



    if value is None:

        return {}



    try:

        return dict(value)

    except Exception:

        return {}





def first_value(data, *keys, default=None):

    """

    Return the first available value from a dictionary.

    """

    if not isinstance(data, dict):

        return default



    for key in keys:

        if key in data and data[key] is not None:

            return data[key]



    return default





def format_number(value, decimals=2):

    """

    Format numeric values safely.

    """

    try:

        number = float(value)



        if decimals == 0:

            return f"{number:,.0f}"



        return f"{number:,.{decimals}f}"



    except Exception:

        return "N/A"





def format_currency(value, decimals=2):

    """

    Format values using Indian Rupee display.

    """

    try:

        number = float(value)

        return f"₹{number:,.{decimals}f}"

    except Exception:

        return "N/A"





def get_eda_result():

    state = st.session_state.workflow_state



    if state is None:

        return {}



    return safe_dict(

        get_state_value(state, "eda_result", {})

    )





def get_forecasting_result():

    state = st.session_state.workflow_state



    if state is None:

        return {}



    return safe_dict(

        get_state_value(state, "forecasting_result", {})

    )





def get_insight_result():

    state = st.session_state.workflow_state



    if state is None:

        return {}



    return safe_dict(

        get_state_value(state, "insight_result", {})

    )





def get_recommendation_result():

    state = st.session_state.workflow_state



    if state is None:

        return {}



    return safe_dict(

        get_state_value(state, "recommendation_result", {})

    )





def get_report_result():

    state = st.session_state.workflow_state



    if state is None:

        return {}



    return safe_dict(

        get_state_value(state, "report_result", {})

    )





def get_visualization_result():

    state = st.session_state.workflow_state



    if state is None:

        return {}



    return safe_dict(

        get_state_value(state, "visualization_result", {})

    )





def get_cleaning_result():

    state = st.session_state.workflow_state



    if state is None:

        return {}



    return safe_dict(

        get_state_value(state, "cleaning_result", {})

    )

def get_cleaning_decisions():
    """Return cleaning decisions as a list of dictionaries."""

    state = st.session_state.workflow_state

    if state is None:
        return []

    decisions = get_state_value(
        state,
        "cleaning_decision",
        []
    )

    if not decisions:
        return []

    if isinstance(decisions, dict):
        decisions = [decisions]

    if not isinstance(decisions, (list, tuple)):
        return []

    normalized_decisions = []

    fields = [
        "issue_id",
        "issue_type",
        "column",
        "affected_rows",
        "evidence",
        "detected_by",
        "llm_reasoning",
        "recommended_action",
        "alternative_actions",
        "confidence",
        "risk_level",
        "requires_approval",
        "user_decision",
        "execution_result",
        "validation_result",
    ]

    for decision in decisions:
        if isinstance(decision, dict):
            decision_dict = decision.copy()

        elif hasattr(decision, "to_dict"):
            decision_dict = decision.to_dict()

        else:
            decision_dict = {
                field: getattr(decision, field)
                for field in fields
                if hasattr(decision, field)
            }

        if decision_dict:
            normalized_decisions.append(decision_dict)

    return normalized_decisions






# ============================================================

# SIDEBAR

# ============================================================



with st.sidebar:



    render_html(

        """

        <div class="sidebar-brand">

            🤖 Sales Intelligence

        </div>

        """

    )



    render_html(

        """

        <div class="sidebar-section">

            1. Upload Sales Data

        </div>

        """

    )



    uploaded_file = st.file_uploader(

        "Upload CSV",

        type=["csv"],

        label_visibility="collapsed"

    )



    if uploaded_file is not None:



        file_changed = (

            st.session_state.file_name != uploaded_file.name

        )



        try:



            df_uploaded = pd.read_csv(uploaded_file)



            st.session_state.df = df_uploaded

            st.session_state.file_name = uploaded_file.name



            if file_changed:



                # Clear old workflow results when a new file is uploaded.

                st.session_state.workflow_state = None

                st.session_state.workflow_serialized = None

                st.session_state.workflow_error = None
                
                # Reset AI Assistant conversation for the new dataset.
                st.session_state.ai_assistant_messages = []
                st.session_state.ai_assistant_open = False

            st.success("CSV loaded")



        except Exception as exc:



            st.session_state.df = None

            st.session_state.file_name = None

            st.session_state.workflow_state = None

            st.session_state.workflow_error = str(exc)



            st.error(f"Unable to read CSV: {exc}")



    if st.session_state.file_name:



        st.caption(

            f"📄 {st.session_state.file_name}"

        )





    # --------------------------------------------------------

    # RUN ANALYSIS

    # --------------------------------------------------------



    render_html(

        """

        <div class="sidebar-section">

            2. Analysis

        </div>

        """

    )



    if st.session_state.df is not None:



        run_button = st.button(

            "▶ Run Complete Analysis",

            use_container_width=True,

            type="primary"

        )



        if run_button:



            st.session_state.analysis_running = True



            with st.spinner(

                "Running all eight AI agents..."

            ):



                try:



                    run_analysis(

                        st.session_state.df.copy()

                    )



                    st.session_state.analysis_running = False



                    st.success(

                        "Complete workflow executed successfully."

                    )



                    st.rerun()



                except Exception as exc:



                    st.session_state.analysis_running = False



                    st.error(

                        f"Workflow failed: {exc}"

                    )





    # --------------------------------------------------------

    # SYSTEM STATUS

    # --------------------------------------------------------



    render_html(

        """

        <div class="sidebar-section">

            3. System Status

        </div>

        """

    )



    statuses = get_agent_statuses(

        st.session_state.workflow_state

    )



    completed = sum(

        1

        for status in statuses.values()

        if status in {

            "Completed",

            "Validated",

            "Skipped"

        }

    )



    total_agents = len(AGENT_NAMES)



    progress = get_progress(statuses)



    for agent, status in statuses.items():



        if status in {"Completed", "Validated"}:

            dot_class = "completed"



        elif status == "In Progress":

            dot_class = "running"



        elif status == "Failed":

            dot_class = "failed"



        elif status == "Skipped":

            dot_class = "skipped"



        else:

            dot_class = ""



        render_html(

            f"""

            <div class="agent-row">



                <div class="agent-dot {dot_class}">

                </div>



                <div>



                    <div class="agent-name">

                        {agent}

                    </div>



                    <div class="agent-status">

                        {status}

                    </div>



                </div>



            </div>

            """

        )





    render_html(

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

        """

    )





    # --------------------------------------------------------

    # WORKFLOW STATUS

    # --------------------------------------------------------



    if st.session_state.workflow_state is not None:



        workflow_status = str(

            get_state_value(

                st.session_state.workflow_state,

                "workflow_status",

                "unknown"

            )

        ).upper()



        if workflow_status == "COMPLETED":



            st.success(

                "✓ Workflow completed"

            )



        elif workflow_status == "FAILED":



            st.error(

                "✕ Workflow failed"

            )





# ============================================================

# HEADER

# ============================================================



render_html(

    """

    <div class="brand-container">



        <div class="brand-icon">

            🤖

        </div>



        <div>



            <div class="brand-title">

                AI-Powered Multi-Agent Sales Intelligence System

            </div>



            <div class="brand-subtitle">

                Retail & E-commerce Sales Analytics and Business Decision Support

            </div>



        </div>



    </div>

    """

)





# ============================================================

# DARK MODE

# ============================================================



dark_mode = st.toggle(

    "Dark Mode",

    value=st.session_state.dark_mode

)



if dark_mode != st.session_state.dark_mode:



    st.session_state.dark_mode = dark_mode



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

    "Report"

]



selected_page = st.radio(

    "Navigation",

    pages,

    index=pages.index(

        st.session_state.current_page

    ),

    horizontal=True,

    label_visibility="collapsed"

)



st.session_state.current_page = selected_page



st.divider()





# ============================================================

# NO DATA STATE

# ============================================================



if st.session_state.df is None:



    render_html(

        """

        <div class="empty-card">



            <div>



                <div class="empty-icon">

                    📊

                </div>



                <div class="empty-title">

                    Upload your sales dataset

                </div>



                <div class="empty-text">

                    Upload a retail or e-commerce CSV file

                    to begin the multi-agent analysis.

                </div>



            </div>



        </div>

        """

    )



    render_html(

        """

        <div class="footer">

            AI-Powered Multi-Agent Sales Intelligence System

            | Built with Streamlit

        </div>

        """

    )



    st.stop()





# ============================================================

# DATA

# ============================================================



df = st.session_state.df.copy()



state = st.session_state.workflow_state

# ============================================================
# AI ASSISTANT
# ============================================================

cleaned_df = get_state_value(state, "cleaned_df", None)

if isinstance(cleaned_df, pd.DataFrame):
    assistant_df = cleaned_df.copy()
else:
    assistant_df = df.copy()

render_ai_assistant(
    assistant_df,
    dataset_name=st.session_state.file_name or "uploaded dataset",
)





# ============================================================

# WORKFLOW NOT RUN STATE

# ============================================================



if state is None:



    render_html(

        """

        <div class="empty-card">



            <div>



                <div class="empty-icon">

                    ⚙️

                </div>



                <div class="empty-title">

                    Dataset Ready

                </div>



                <div class="empty-text">

                    Your dataset has been uploaded successfully.

                    <br>

                    Click <b>Run Complete Analysis</b> in the sidebar

                    to execute all eight agents.

                </div>



            </div>



        </div>

        """

    )



    render_html(

        """

        <div class="footer">

            AI-Powered Multi-Agent Sales Intelligence System

            | Built with Streamlit

        </div>

        """

    )



    st.stop()





# ============================================================

# WORKFLOW ERROR

# ============================================================



if st.session_state.workflow_error:



    st.error(

        st.session_state.workflow_error

    )





# ============================================================
# HUMAN-IN-THE-LOOP CLEANING APPROVAL PANEL
# ============================================================

cleaning_status_now = str(
    get_state_value(state, "cleaning_status", "")
).lower()
workflow_status_now = str(
    get_state_value(state, "workflow_status", "")
).lower()

if (
    cleaning_status_now == "awaiting_approval"
    or workflow_status_now == "awaiting_approval"
):
    st.header("Data Cleaning Approval")
    st.warning(
        "The workflow is paused. Review each proposed cleaning action. "
        "Every decision defaults to SKIP; choose APPROVE only when you "
        "want that action to be executed."
    )

    cleaning_decisions = get_cleaning_decisions()
    approvals = {}

    if not cleaning_decisions:
        st.info(
            "The cleaning agent has paused for approval, but no individual "
            "decisions were returned. You can continue without approving "
            "any cleaning action."
        )

    for index, decision in enumerate(cleaning_decisions):
        issue_id = str(decision.get("issue_id") or f"ISSUE_{index + 1}")
        issue_type = decision.get("issue_type", "Cleaning issue")
        column = decision.get("column", "Not specified")
        risk = decision.get("risk_level", "Not specified")
        affected_rows = decision.get("affected_rows", "Not specified")
        recommended_action = decision.get("recommended_action", "No recommendation provided")

        with st.expander(
            f"{issue_id} — {issue_type} | Column: {column}",
            expanded=True,
        ):
            left, right = st.columns(2)
            with left:
                st.write("**Risk level:**", str(risk))
                st.write("**Affected rows:**", str(affected_rows))
                st.write("**Recommended action:**", str(recommended_action))
            with right:
                st.write("**Confidence:**", str(decision.get("confidence", "Not specified")))
                st.write("**Approval required:**", str(decision.get("requires_approval", "Not specified")))
                st.write("**Detected by:**", str(decision.get("detected_by", "Not specified")))

            reasoning = decision.get("llm_reasoning")
            if reasoning:
                st.write("**Reasoning:**")
                st.write(str(reasoning))

            evidence = decision.get("evidence")
            if evidence:
                st.write("**Evidence:**")
                if isinstance(evidence, (dict, list, tuple)):
                    st.json(evidence)
                else:
                    st.write(str(evidence))

            alternatives = decision.get("alternative_actions")
            if alternatives:
                st.write("**Alternative actions:**")
                st.write(alternatives)

            selected_decision = st.selectbox(
                "Decision for this issue",
                options=["SKIP", "APPROVE"],
                index=0,
                key=f"cleaning_approval_{issue_id}_{index}",
                help="SKIP leaves this proposed action unapplied. APPROVE authorises the cleaning agent to execute it.",
            )
            approvals[issue_id] = selected_decision

    st.caption(
        "No cleaning action will run until you press the button below. "
        "Skipped actions remain unapplied."
    )

    
    if st.button(
        "Confirm Decisions and Continue Workflow",
        type="primary",
        key="confirm_cleaning_approvals",
        use_container_width=True,
    ):
        st.write("Confirm button clicked.")
        st.write(f"Cleaning decisions submitted: {len(approvals)}")

        try:
            with st.spinner(
                "Applying approved cleaning decisions and continuing analysis..."
            ):
                resumed_state = resume_workflow_after_cleaning(
                    state,
                    approvals,
                )

            st.session_state.workflow_state = resumed_state
            st.session_state.workflow_error = None

            try:
                st.session_state.workflow_serialized = (
                    resumed_state.to_dict()
                )
            except Exception:
                st.session_state.workflow_serialized = None

            resumed_status = str(
                get_state_value(
                    resumed_state,
                    "workflow_status",
                    "unknown",
                )
            ).lower()

            cleaning_status = str(
                get_state_value(
                    resumed_state,
                    "cleaning_status",
                    "unknown",
                )
            ).lower()

            st.write(f"Workflow status: `{resumed_status}`")
            st.write(f"Cleaning status: `{cleaning_status}`")

            if resumed_status == "failed" or cleaning_status == "failed":
                errors = get_state_value(
                    resumed_state,
                    "errors",
                    [],
                )
                st.error("The workflow returned a failure.")
                st.write("Error details:")
                st.write(errors)

                # Keep the current page visible for debugging.
                st.stop()

            if (
                resumed_status == "completed"
                or cleaning_status in {"validated", "completed"}
            ):
                st.success(
                    "Cleaning decisions processed. "
                    "The workflow reports successful completion."
                )
            else:
                st.warning(
                    "The workflow returned without completing. "
                    "Check the status values above."
                )

            # Rerun only after displaying the returned state.
            st.rerun()

        except Exception as exc:
            st.error(
                f"Could not resume the workflow: "
                f"{type(exc).__name__}: {exc}"
            )
            st.exception(exc)


# ============================================================

# GET BACKEND RESULTS

# ============================================================



eda_result = get_eda_result()



forecasting_result = get_forecasting_result()



insight_result = get_insight_result()



recommendation_result = get_recommendation_result()



report_result = get_report_result()



visualization_result = get_visualization_result()



cleaning_result = get_cleaning_result()





# ============================================================

# CLEANED DATA

# ============================================================



cleaned_df = get_state_value(

    state,

    "cleaned_df",

    None

)



if isinstance(cleaned_df, pd.DataFrame):



    analysis_df = cleaned_df.copy()



else:



    analysis_df = df.copy()





# ============================================================

# EDA RESULTS

# ============================================================



kpis = safe_dict(

    first_value(

        eda_result,

        "kpis",

        "kpi_results",

        default={}

    )

)



trends = safe_dict(

    first_value(

        eda_result,

        "trends",

        "trend_results",

        default={}

    )

)



rankings = safe_dict(

    first_value(

        eda_result,

        "rankings",

        "ranking_results",

        default={}

    )

)





# ============================================================

# KPI VALUES

# ============================================================



total_sales = first_value(

    kpis,

    "total_sales",

    "total_revenue",

    default=0

)



total_quantity = first_value(

    kpis,

    "total_quantity",

    default=0

)



total_orders = first_value(

    kpis,

    "total_orders",

    default=len(analysis_df)

)



total_customers = first_value(

    kpis,

    "total_customers",

    default=analysis_df.shape[0]

)



average_order_value = first_value(

    kpis,

    "average_order_value",

    default=0

)



average_quantity = first_value(

    kpis,

    "average_quantity_per_order",

    default=0

)



average_selling_price = first_value(

    kpis,

    "average_selling_price",

    default=0

)





# ============================================================

# DASHBOARD

# ============================================================



if selected_page == "Dashboard":



    st.header("Dashboard")



    st.caption(

        f"Validated analysis results for "

        f"**{st.session_state.file_name}**"

    )





    # --------------------------------------------------------

    # WORKFLOW STATUS

    # --------------------------------------------------------



    if workflow_completed(state):



        st.success(

            "✓ Complete eight-agent workflow successfully completed."

        )



    else:



        st.warning(

            "The workflow has not completed successfully."

        )





    # --------------------------------------------------------

    # KPI CARDS

    # --------------------------------------------------------



    cols = st.columns(5)



    metrics = [

        (

            "💰",

            "Total Revenue",

            format_currency(total_sales, 0),

            "Validated EDA KPI"

        ),

        (

            "🛒",

            "Total Orders",

            format_number(total_orders, 0),

            "Records analysed"

        ),

        (

            "📦",

            "Total Quantity",

            format_number(total_quantity, 0),

            "Units detected"

        ),

        (

            "🛍️",

            "Average Order Value",

            format_currency(average_order_value, 2),

            "Validated EDA KPI"

        ),

        (

            "👥",

            "Total Customers",

            format_number(total_customers, 0),

            "Validated customer analysis"

        )

    ]



    for col, metric in zip(cols, metrics):



        icon, title, value, description = metric



        with col:



            render_html(

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

                """

            )





    st.write("")





    # --------------------------------------------------------

    # SALES TREND + PRODUCT PERFORMANCE

    # --------------------------------------------------------



    left, right = st.columns(2)





    with left:



        render_html(

            """

            <div class="section-card">



                <div class="section-title">

                    Monthly Sales Trend

                </div>



            </div>

            """

        )



        monthly_df = pd.DataFrame(

            first_value(

                trends,

                "monthly",

                "monthly_sales",

                default=[]

            )

        )



        if not monthly_df.empty:



            date_candidates = [

                "month",

                "Month",

                "period",

                "Period"

            ]



            sales_candidates = [

                "sales",

                "Sales",

                "revenue",

                "Revenue",

                "total_sales",

                "total_amount"

            ]



            x_col = next(

                (

                    c for c in date_candidates

                    if c in monthly_df.columns

                ),

                monthly_df.columns[0]

            )



            y_col = next(

                (

                    c for c in sales_candidates

                    if c in monthly_df.columns

                ),

                monthly_df.columns[-1]

            )



            fig = px.line(

                monthly_df,

                x=x_col,

                y=y_col,

                markers=True

            )



            fig.update_layout(

                height=350,

                margin=dict(

                    l=20,

                    r=20,

                    t=20,

                    b=20

                )

            )



            st.plotly_chart(

                fig,

                use_container_width=True

            )



        else:



            st.info(

                "Monthly trend data is unavailable."

            )





    with right:



        render_html(

            """

            <div class="section-card">



                <div class="section-title">

                    Sales by Product Category

                </div>



            </div>

            """

        )



        product_sales = pd.DataFrame(

            first_value(

                rankings,

                "product_sales",

                "top_product_categories_by_sales",

                "products_by_sales",

                default=[]

            )

        )



        if not product_sales.empty:



            st.dataframe(

                product_sales,

                use_container_width=True,

                hide_index=True

            )



        else:



            st.info(

                "Product ranking data is unavailable."

            )





    # --------------------------------------------------------

    # TOP REGIONS + TOP CUSTOMERS

    # --------------------------------------------------------



    left, right = st.columns(2)





    with left:



        render_html(

            """

            <div class="section-card">



                <div class="section-title">

                    Regional Sales Performance

                </div>



            </div>

            """

        )



        regional_sales = pd.DataFrame(

            first_value(

                rankings,

                "regional_sales",

                "region_sales",

                "top_regions_by_sales",

                default=[]

            )

        )



        if not regional_sales.empty:



            st.dataframe(

                regional_sales,

                use_container_width=True,

                hide_index=True

            )



        else:



            st.info(

                "Regional ranking data is unavailable."

            )





    with right:



        render_html(

            """

            <div class="section-card">



                <div class="section-title">

                    Top Customers by Sales

                </div>



            </div>

            """

        )



        customer_sales = pd.DataFrame(

            first_value(

                rankings,

                "customer_sales",

                "top_customers_by_sales",

                "customers_by_sales",

                default=[]

            )

        )



        if not customer_sales.empty:



            st.dataframe(

                customer_sales,

                use_container_width=True,

                hide_index=True

            )



        else:



            st.info(

                "Customer ranking data is unavailable."

            )





    # --------------------------------------------------------

    # DATA QUALITY + INSIGHTS + RECOMMENDATIONS

    # --------------------------------------------------------



    st.write("")



    c1, c2, c3 = st.columns(3)





    # DATA QUALITY



    with c1:



        cleaning_validation = get_state_value(

            state,

            "cleaning_validation",

            {}

        )



        cleaning_validation = safe_dict(

            cleaning_validation

        )



        missing_values = int(

            analysis_df.isna().sum().sum()

        )



        duplicate_rows = int(

            analysis_df.duplicated().sum()

        )



        cleaning_status = str(

            first_value(

                cleaning_validation,

                "overall_status",

                default="UNKNOWN"

            )

        )



        render_html(

            f"""

            <div class="info-card">



                <div class="info-title">

                    🛡️ Data Quality Summary

                </div>



                <div class="info-item">

                    Missing Values:

                    <b>{missing_values:,}</b>

                </div>



                <div class="info-item">

                    Duplicate Rows:

                    <b>{duplicate_rows:,}</b>

                </div>



                <div class="info-item">

                    Rows:

                    <b>{len(analysis_df):,}</b>

                </div>



                <div class="info-item">

                    Columns:

                    <b>{len(analysis_df.columns):,}</b>

                </div>



                <div class="info-item">

                    Cleaning Validation:

                    <b>{cleaning_status}</b>

                </div>



            </div>

            """

        )





    # INSIGHTS



    with c2:



        insights = insight_result.get(

            "insights",

            []

        )



        if not isinstance(insights, list):

            insights = []



        insight_items = []



        for item in insights[:4]:



            if isinstance(item, dict):



                text = first_value(

                    item,

                    "insight",

                    "statement",

                    "description",

                    "title",

                    default=str(item)

                )



            else:



                text = str(item)



            insight_items.append(

                f'<div class="info-item">• {text}</div>'

            )



        if not insight_items:



            insight_items.append(

                '<div class="info-item">No validated insights available.</div>'

            )



        render_html(

            """

            <div class="info-card">



                <div class="info-title">

                    💡 Key Insights

                </div>

            """

            +

            "".join(insight_items)

            +

            """

            </div>

            """

        )





    # RECOMMENDATIONS



    with c3:



        recommendations = recommendation_result.get(

            "recommendations",

            []

        )



        if not isinstance(recommendations, list):

            recommendations = []



        recommendation_items = []



        for item in recommendations[:4]:



            if isinstance(item, dict):



                text = first_value(

                    item,

                    "recommendation",

                    "title",

                    "description",

                    default=str(item)

                )



            else:



                text = str(item)



            recommendation_items.append(

                f'<div class="info-item">• {text}</div>'

            )



        if not recommendation_items:



            recommendation_items.append(

                '<div class="info-item">No validated recommendations available.</div>'

            )



        render_html(

            """

            <div class="info-card">



                <div class="info-title">

                    🎯 Top Recommendations

                </div>

            """

            +

            "".join(recommendation_items)

            +

            """

            </div>

            """

        )





# ============================================================

# DETAILED ANALYSIS

# ============================================================



elif selected_page == "Detailed Analysis":



    st.header("Detailed Analysis")



    st.write(

        "Validated analytical results generated by the EDA Agent."

    )





    # --------------------------------------------------------

    # DATASET OVERVIEW

    # --------------------------------------------------------



    st.subheader("Dataset Overview")



    overview = pd.DataFrame(

        {

            "Metric": [

                "Rows",

                "Columns",

                "Missing Values",

                "Duplicate Rows"

            ],

            "Value": [

                len(analysis_df),

                len(analysis_df.columns),

                int(

                    analysis_df.isna().sum().sum()

                ),

                int(

                    analysis_df.duplicated().sum()

                )

            ]

        }

    )



    st.dataframe(

        overview,

        use_container_width=True,

        hide_index=True

    )





    # --------------------------------------------------------

    # KPI DETAILS

    # --------------------------------------------------------



    st.subheader("KPI Results")



    if kpis:



        kpi_table = pd.DataFrame(

            {

                "KPI": list(kpis.keys()),

                "Value": list(kpis.values())

            }

        )



        st.dataframe(

            kpi_table,

            use_container_width=True,

            hide_index=True

        )



    else:



        st.info(

            "Validated KPI results are unavailable."

        )





    # --------------------------------------------------------

    # COLUMN INFORMATION

    # --------------------------------------------------------



    st.subheader("Column Information")



    column_info = pd.DataFrame(

        {

            "Column": analysis_df.columns,

            "Data Type": [

                str(dtype)

                for dtype in analysis_df.dtypes

            ],

            "Missing Values": [

                int(

                    analysis_df[col].isna().sum()

                )

                for col in analysis_df.columns

            ],

            "Unique Values": [

                int(

                    analysis_df[col].nunique()

                )

                for col in analysis_df.columns

            ]

        }

    )



    st.dataframe(

        column_info,

        use_container_width=True,

        hide_index=True

    )





    # --------------------------------------------------------

    # DATASET PREVIEW

    # --------------------------------------------------------



    st.subheader("Dataset Preview")



    st.dataframe(

        analysis_df.head(20),

        use_container_width=True

    )





    # --------------------------------------------------------

    # TRENDS

    # --------------------------------------------------------



    st.subheader("Trend Analysis")



    monthly_df = pd.DataFrame(

        first_value(

            trends,

            "monthly",

            "monthly_sales",

            default=[]

        )

    )



    if not monthly_df.empty:



        st.dataframe(

            monthly_df,

            use_container_width=True,

            hide_index=True

        )



    else:



        st.info(

            "Monthly trend results are unavailable."

        )





# ============================================================

# FORECAST

# ============================================================



elif selected_page == "Forecast":



    st.header("Forecast")



    eligibility = safe_dict(

        first_value(

            forecasting_result,

            "eligibility",

            "forecast_eligibility",

            default={}

        )

    )



    eligible = first_value(

        forecasting_result,

        "eligible",

        "is_eligible",

        default=None

    )



    if eligible is None:

        eligible = first_value(

            eligibility,

            "eligible",

            "is_forecast_eligible",

            default=False

        )



    eligible = bool(eligible)





    # --------------------------------------------------------

    # FORECAST STATUS

    # --------------------------------------------------------



    if eligible:



        st.success(

            "✓ Forecasting is eligible for this dataset."

        )



    else:



        st.warning(

            "Forecasting is not eligible for this dataset."

        )





    # --------------------------------------------------------

    # FORECAST METRICS

    # --------------------------------------------------------



    fc1, fc2, fc3, fc4 = st.columns(4)



    best_model = first_value(

        forecasting_result,

        "best_model",

        default="N/A"

    )



    best_mae = first_value(

        forecasting_result,

        "best_mae",

        default=None

    )



    horizon = first_value(

        forecasting_result,

        "horizon",

        "forecast_horizon",

        default=None

    )



    date_column = first_value(

        forecasting_result,

        "date_column",

        default="N/A"

    )



    sales_column = first_value(

        forecasting_result,

        "sales_column",

        default="N/A"

    )





    with fc1:



        st.metric(

            "Eligibility",

            "Eligible" if eligible else "Not Eligible"

        )





    with fc2:



        st.metric(

            "Best Model",

            str(best_model)

        )





    with fc3:



        st.metric(

            "Best MAE",

            format_number(

                best_mae,

                2

            )

        )





    with fc4:



        st.metric(

            "Forecast Horizon",

            str(

                horizon

                if horizon is not None

                else "N/A"

            )

        )





    st.write("")



    st.caption(

        f"Date column: **{date_column}** | "

        f"Sales column: **{sales_column}**"

    )





    # --------------------------------------------------------

    # FORECAST DATA

    # --------------------------------------------------------



    forecast_data = first_value(

        forecasting_result,

        "forecast",

        "forecast_values",

        "predictions",

        default=[]

    )



    if isinstance(

        forecast_data,

        pd.DataFrame

    ):



        forecast_df = forecast_data.copy()



    elif isinstance(

        forecast_data,

        list

    ):



        forecast_df = pd.DataFrame(

            forecast_data

        )



    elif isinstance(

        forecast_data,

        dict

    ):



        forecast_df = pd.DataFrame(

            forecast_data

        )



    else:



        forecast_df = pd.DataFrame()





    if not forecast_df.empty:



        st.subheader("Forecast Results")



        st.dataframe(

            forecast_df,

            use_container_width=True,

            hide_index=True

        )





        # Try to automatically identify date/value columns.



        date_candidates = [

            "date",

            "Date",

            "forecast_date",

            "Forecast Date"

        ]



        value_candidates = [

            "forecast",

            "Forecast",

            "prediction",

            "Prediction",

            "predicted_sales",

            "Predicted Sales",

            "value",

            "Value"

        ]



        fc_date_col = next(

            (

                col

                for col in date_candidates

                if col in forecast_df.columns

            ),

            None

        )



        fc_value_col = next(

            (

                col

                for col in value_candidates

                if col in forecast_df.columns

            ),

            None

        )





        if (

            fc_date_col is not None

            and fc_value_col is not None

        ):



            fig = px.line(

                forecast_df,

                x=fc_date_col,

                y=fc_value_col,

                markers=True

            )



            fig.update_layout(

                title="Forecasted Sales",

                height=450

            )



            st.plotly_chart(

                fig,

                use_container_width=True

            )



    else:



        st.info(

            "Forecast values are not directly available "

            "in the workflow result."

        )





# ============================================================

# INSIGHTS

# ============================================================



elif selected_page == "Insights":



    st.header("Insights")



    st.write(

        "Evidence-grounded insights generated by the Insight Agent."

    )





    insights = insight_result.get(

        "insights",

        []

    )



    if not isinstance(insights, list):

        insights = []





    if not insights:



        st.info(

            "No validated insights are available."

        )



    else:



        for index, item in enumerate(

            insights,

            start=1

        ):



            if isinstance(item, dict):



                title = first_value(

                    item,

                    "title",

                    default=f"Insight {index}"

                )



                text = first_value(

                    item,

                    "insight",

                    "statement",

                    "description",

                    default=""

                )



                confidence = first_value(

                    item,

                    "confidence",

                    default=None

                )



                evidence = first_value(

                    item,

                    "evidence",

                    "evidence_source",

                    "source",

                    default=None

                )



            else:



                title = f"Insight {index}"

                text = str(item)

                confidence = None

                evidence = None





            with st.expander(

                f"{index}. {title}",

                expanded=index <= 3

            ):



                if text:

                    st.write(text)



                if confidence is not None:



                    st.caption(

                        f"Confidence: "

                        f"{format_number(confidence, 2)}"

                    )



                if evidence is not None:



                    st.caption(

                        f"Evidence: {evidence}"

                    )





    # --------------------------------------------------------

    # VALIDATION

    # --------------------------------------------------------



    insight_validation = get_state_value(

        state,

        "insight_validation",

        {}

    )



    insight_validation = safe_dict(

        insight_validation

    )



    if insight_validation:



        st.subheader(

            "Insight Validation"

        )



        validation_status = first_value(

            insight_validation,

            "overall_status",

            default="UNKNOWN"

        )



        if str(validation_status).upper() == "PASSED":



            st.success(

                "✓ Insight validation PASSED"

            )



        else:



            st.warning(

                f"Insight validation: {validation_status}"

            )





# ============================================================

# RECOMMENDATIONS

# ============================================================



elif selected_page == "Recommendations":



    st.header("Recommendations")



    st.write(

        "Evidence-based business recommendations generated "

        "by the Recommendation Agent."

    )





    recommendations = recommendation_result.get(

        "recommendations",

        []

    )



    if not isinstance(

        recommendations,

        list

    ):



        recommendations = []





    if not recommendations:



        st.info(

            "No validated recommendations are available."

        )



    else:



        for index, item in enumerate(

            recommendations,

            start=1

        ):



            if isinstance(item, dict):



                title = first_value(

                    item,

                    "title",

                    default=f"Recommendation {index}"

                )



                recommendation = first_value(

                    item,

                    "recommendation",

                    "description",

                    default=""

                )



                priority = first_value(

                    item,

                    "priority",

                    default="N/A"

                )



                confidence = first_value(

                    item,

                    "confidence",

                    default=None

                )



                implication = first_value(

                    item,

                    "business_implication",

                    default=None

                )



                evidence = first_value(

                    item,

                    "evidence",

                    default=None

                )



            else:



                title = f"Recommendation {index}"

                recommendation = str(item)

                priority = "N/A"

                confidence = None

                implication = None

                evidence = None





            with st.expander(

                f"{index}. {title}",

                expanded=index <= 3

            ):



                st.write(

                    recommendation

                )



                if implication:



                    st.markdown(

                        f"**Business Implication:** "

                        f"{implication}"

                    )



                if priority:



                    st.caption(

                        f"Priority: {priority}"

                    )



                if confidence is not None:



                    st.caption(

                        f"Confidence: "

                        f"{format_number(confidence, 2)}"

                    )



                if evidence:



                    st.caption(

                        f"Evidence: {evidence}"

                    )





    # --------------------------------------------------------

    # VALIDATION

    # --------------------------------------------------------



    recommendation_validation = get_state_value(

        state,

        "recommendation_validation",

        {}

    )



    recommendation_validation = safe_dict(

        recommendation_validation

    )



    if recommendation_validation:



        st.subheader(

            "Recommendation Validation"

        )



        validation_status = first_value(

            recommendation_validation,

            "overall_status",

            default="UNKNOWN"

        )



        if str(validation_status).upper() == "PASSED":



            st.success(

                "✓ Recommendation validation PASSED"

            )



        else:



            st.warning(

                f"Recommendation validation: "

                f"{validation_status}"

            )





# ============================================================

# REPORT

# ============================================================



elif selected_page == "Report":



    st.header("Report")



    st.write(

        "Final consolidated report generated by the Report Agent."

    )



    # --------------------------------------------------------

    # REPORT STATUS

    # --------------------------------------------------------



    report_validation = get_state_value(

        state,

        "report_validation",

        {}

    )



    report_validation = safe_dict(

        report_validation

    )



    report_status = first_value(

        report_validation,

        "overall_status",

        default="UNKNOWN"

    )



    if str(report_status).upper() == "PASSED":



        st.success(

            "✓ Report validation PASSED"

        )



    else:



        st.warning(

            f"Report validation: {report_status}"

        )



    # --------------------------------------------------------

    # WORD REPORT DELIVERABLE

    # --------------------------------------------------------



    word_report_status = first_value(

        report_result,

        "word_report_status",

        default="not_generated"

    )



    word_report_path = first_value(

        report_result,

        "word_report_path",

        default=""

    )



    word_report_error = first_value(

        report_result,

        "word_report_error",

        default=""

    )



    st.subheader("Word Report")



    if (

        str(word_report_status).lower() == "generated"

        and word_report_path

    ):



        report_path = Path(str(word_report_path))



        if not report_path.is_absolute():

            report_path = Path.cwd() / report_path



        if report_path.is_file():



            file_size = report_path.stat().st_size



            st.success(

                "✓ Professional Word report generated successfully."

            )



            info_col1, info_col2 = st.columns(2)



            with info_col1:

                st.metric(

                    "Report Status",

                    "Generated"

                )



            with info_col2:

                st.metric(

                    "File Size",

                    f"{file_size / 1024:.1f} KB"

                )



            with open(report_path, "rb") as report_file:

                report_bytes = report_file.read()



            st.download_button(

                label="⬇ Download Word Report",

                data=report_bytes,

                file_name=report_path.name,

                mime=(

                    "application/vnd.openxmlformats-"

                    "officedocument.wordprocessingml.document"

                ),

                use_container_width=True,

                type="primary",

            )



            st.caption(

                f"Generated by Report Agent: {report_path}"

            )



        else:



            st.error(

                "The Report Agent reported that the Word report "

                "was generated, but the DOCX file could not be found."

            )



            st.caption(

                f"Expected file: {word_report_path}"

            )



    elif str(word_report_status).lower() == "failed":



        st.error(

            "The structured report was generated, but Word report "

            "generation failed."

        )



        if word_report_error:

            st.caption(

                f"Error: {word_report_error}"

            )



    else:



        st.info(

            "The Word report has not been generated yet. "

            "Run the complete analysis from the sidebar."

        )



    # --------------------------------------------------------

    # REPORT DATA

    # --------------------------------------------------------



    report = first_value(

        report_result,

        "report",

        default={}

    )



    report = safe_dict(report)



    if not report:



        st.info(

            "Report data is unavailable."

        )



    else:



        sections_for_count = first_value(

            report,

            "sections",

            default=[]

        )



        if not isinstance(

            sections_for_count,

            list

        ):

            sections_for_count = []



        total_sections = first_value(

            report_result,

            "total_sections",

            default=len(sections_for_count)

        )



        st.subheader("Report Summary")



        summary_col1, summary_col2 = st.columns(2)



        with summary_col1:

            st.metric(

                "Report Sections",

                str(total_sections)

            )



        with summary_col2:

            st.metric(

                "Structured Report",

                (

                    "Validated"

                    if str(report_status).upper() == "PASSED"

                    else "Not Validated"

                )

            )



        # ----------------------------------------------------

        # EXECUTIVE SUMMARY

        # ----------------------------------------------------



        executive_summary = first_value(

            report,

            "executive_summary",

            default=""

        )



        if executive_summary:



            st.subheader(

                "Executive Summary"

            )



            st.info(

                executive_summary

            )



        # ----------------------------------------------------

        # REPORT SECTIONS

        # ----------------------------------------------------



        sections = first_value(

            report,

            "sections",

            default=[]

        )



        if not isinstance(

            sections,

            list

        ):

            sections = []



        st.subheader(

            "Report Sections"

        )



        if sections:



            for index, section in enumerate(

                sections,

                start=1

            ):



                if isinstance(

                    section,

                    dict

                ):



                    title = first_value(

                        section,

                        "title",

                        default=f"Section {index}"

                    )



                    content = first_value(

                        section,

                        "content",

                        default=""

                    )



                    evidence_source = first_value(

                        section,

                        "evidence_source",

                        default="Validated workflow evidence"

                    )



                    status = first_value(

                        section,

                        "status",

                        default="VALIDATED"

                    )



                else:



                    title = f"Section {index}"

                    content = section

                    evidence_source = (

                        "Validated workflow evidence"

                    )

                    status = "VALIDATED"



                with st.expander(

                    f"{index}. {title}",

                    expanded=index == 1

                ):



                    if isinstance(

                        content,

                        (dict, list)

                    ):



                        st.json(

                            content

                        )



                    else:



                        st.write(

                            content

                        )



                    st.caption(

                        f"Evidence: {evidence_source}"

                    )



                    st.caption(

                        f"Status: {status}"

                    )



        # ----------------------------------------------------

        # LIMITATIONS

        # ----------------------------------------------------



        limitations = first_value(

            report,

            "limitations",

            default=[]

        )



        if not isinstance(

            limitations,

            list

        ):

            limitations = []



        if limitations:



            st.subheader(

                "Limitations"

            )



            for limitation in limitations:



                st.warning(

                    str(limitation)

                )





# ============================================================

# FOOTER

# ============================================================



render_html(

    """

    <div class="footer">

        AI-Powered Multi-Agent Sales Intelligence System

        | Built with Streamlit

    </div>

    """

)