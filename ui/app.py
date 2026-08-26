import json
import sys
from pathlib import Path


# ============================================================
# Project root
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import streamlit as st

from agents.growth_workflow import run_growth_workflow


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Razorpay AI Growth Agent",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Demo data
# ============================================================

MERCHANT_SNAPSHOT = {
    "products": [
        {
            "name": "Premium Annual Plan",
            "price": 50000,
            "sales": 100,
        },
        {
            "name": "Basic Plan",
            "price": 10000,
            "sales": 200,
        },
    ],
    "upsell_evidence": [
        {
            "base_product": "Premium Annual Plan",
            "upsell_product": "Premium Support",
            "upsell_price": 5000,
            "conversion_rate": 0.25,
        }
    ],
}


AUDIT_LOG_PATH = Path("audit_log.jsonl")


# ============================================================
# Custom CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Header */

    .hero {
        padding: 10px 0 20px 0;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 750;
        letter-spacing: -1.5px;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 12px;
    }

    .mode-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background: #eef6ff;
        color: #2563eb;
        font-size: 13px;
        font-weight: 600;
    }

    /* Section titles */

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    /* Cards */

    .card {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 22px;
        background: white;
        min-height: 145px;
    }

    .card-label {
        color: #6b7280;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .card-value {
        font-size: 28px;
        font-weight: 750;
        margin-top: 8px;
    }

    .card-description {
        color: #6b7280;
        font-size: 14px;
        margin-top: 5px;
    }

    /* Recommendation */

    .recommendation {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 24px;
        background: #fafafa;
    }

    .recommendation-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .recommendation-text {
        color: #6b7280;
        font-size: 15px;
        line-height: 1.6;
    }

    /* Pipeline */

    .pipeline {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 15px 0 25px 0;
        flex-wrap: wrap;
    }

    .pipeline-step {
        padding: 10px 15px;
        border-radius: 9px;
        background: #f3f4f6;
        font-size: 13px;
        font-weight: 600;
    }

    .pipeline-arrow {
        color: #9ca3af;
        font-weight: 700;
    }

    /* Success */

    .success-panel {
        border: 1px solid #bbf7d0;
        background: #f0fdf4;
        border-radius: 14px;
        padding: 25px;
    }

    .success-title {
        font-size: 24px;
        font-weight: 750;
        margin-bottom: 12px;
    }

    /* Failure */

    .failure-panel {
        border: 1px solid #fecaca;
        background: #fef2f2;
        border-radius: 14px;
        padding: 25px;
    }

    .failure-title {
        font-size: 24px;
        font-weight: 750;
        margin-bottom: 12px;
    }

    /* Audit */

    .audit-event {
        padding: 12px 15px;
        border: 1px solid #e5e7eb;
        border-radius: 9px;
        margin-bottom: 8px;
        background: #ffffff;
    }

    .audit-event-name {
        font-weight: 650;
        font-size: 14px;
    }

    .audit-time {
        color: #9ca3af;
        font-size: 12px;
    }

    /* Buttons */

    div.stButton > button {
        border-radius: 9px;
        font-weight: 650;
        min-height: 48px;
    }

    /* Hide Streamlit footer */

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            Razorpay AI Growth Agent
        </div>

        <div class="hero-subtitle">
            Autonomous revenue growth with bounded upsells
            and controlled payment execution.
        </div>

        <span class="mode-badge">
            ● RAZORPAY TEST MODE
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Merchant overview
# ============================================================

st.markdown(
    '<div class="section-title">Merchant Opportunity</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        """
        <div class="card">
            <div class="card-label">
                High-Value Product
            </div>

            <div class="card-value">
                ₹50,000
            </div>

            <div class="card-description">
                Premium Annual Plan
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown(
        """
        <div class="card">
            <div class="card-label">
                Recommended Upsell
            </div>

            <div class="card-value">
                ₹5,000
            </div>

            <div class="card-description">
                Premium Support
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        """
        <div class="card">
            <div class="card-label">
                Maximum Upsell
            </div>

            <div class="card-value">
                10%
            </div>

            <div class="card-description">
                Deterministic policy boundary
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.write("")


# ============================================================
# AI recommendation
# ============================================================

st.markdown(
    '<div class="section-title">AI Recommendation</div>',
    unsafe_allow_html=True,
)

recommendation_col, evidence_col = st.columns(
    [2.2, 1]
)


with recommendation_col:

    st.markdown(
        """
        <div class="recommendation">

            <div class="recommendation-title">
                Premium Annual Plan + Premium Support
            </div>

            <div class="recommendation-text">
                The growth agent identified the highest-value
                product and found historical evidence supporting
                Premium Support as an upsell.
                <br><br>
                The proposed ₹5,000 upsell is exactly 10% of the
                ₹50,000 base product, keeping the action within
                the configured autonomous boundary.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with evidence_col:

    st.metric(
        "Historical Conversion",
        "25%",
    )

    st.caption(
        "Evidence supporting the recommendation"
    )


st.write("")


# ============================================================
# Agent pipeline
# ============================================================

st.markdown(
    '<div class="section-title">Autonomous Execution</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pipeline">

        <div class="pipeline-step">
            🧠 Growth Agent
        </div>

        <div class="pipeline-arrow">→</div>

        <div class="pipeline-step">
            🛡️ Upsell Policy
        </div>

        <div class="pipeline-arrow">→</div>

        <div class="pipeline-step">
            💳 Razorpay Test Mode
        </div>

        <div class="pipeline-arrow">→</div>

        <div class="pipeline-step">
            📋 Audit Trail
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Execution buttons
# ============================================================

create_col, failure_col = st.columns(2)


with create_col:

    create_clicked = st.button(
        "🚀  CREATE PAYMENT LINK",
        use_container_width=True,
        type="primary",
    )


with failure_col:

    failure_clicked = st.button(
        "⚠  DEMO GRACEFUL FAILURE",
        use_container_width=True,
    )


# ============================================================
# Success flow
# ============================================================

if create_clicked:

    with st.spinner(
        "Agent evaluating opportunity and creating "
        "Razorpay Test Mode Payment Link..."
    ):

        result = run_growth_workflow(
            MERCHANT_SNAPSHOT,
            merchant_id="demo-merchant-ui",
            mode="test",
        )

    st.divider()

    if result["success"]:

        st.markdown(
            """
            <div class="success-panel">

                <div class="success-title">
                    ✓ Payment Link Created
                </div>

                <div>
                    The autonomous growth workflow completed
                    successfully.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        result_col1, result_col2 = st.columns(2)

        with result_col1:

            st.metric(
                "Final Amount",
                f"₹{result['amount']:,}",
            )

            st.caption(
                "Premium Annual Plan + Premium Support"
            )

        with result_col2:

            st.metric(
                "Payment Link ID",
                result["payment_link_id"],
            )

        st.markdown(
            "### Customer Payment Link"
        )

        st.link_button(
            "🔗  Open Razorpay Payment Link",
            result["short_url"],
            use_container_width=True,
        )

        st.code(
            result["short_url"],
            language=None,
        )

    else:

        st.error(
            "Growth workflow failed."
        )

        st.write(
            f"**Stage:** `{result['stage']}`"
        )

        st.write(
            f"**Reason:** {result['reason']}"
        )


# ============================================================
# Controlled failure flow
# ============================================================

if failure_clicked:

    st.divider()

    st.markdown(
        '<div class="section-title">Failure Handling</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "A controlled Razorpay Test Mode API failure is "
        "being simulated."
    )

    failure_snapshot = {
        "products": [
            {
                "name": "Premium Annual Plan",
                "price": 50000,
                "sales": 100,
            }
        ],
        "upsell_evidence": [
            {
                "base_product": "Premium Annual Plan",
                "upsell_product": "Premium Support",
                "upsell_price": 5000,
                "conversion_rate": 0.25,
            }
        ],
    }

    try:

        from unittest.mock import patch

        with patch(
            "agents.growth_workflow.create_payment_link"
        ) as mock_create:

            mock_create.side_effect = RuntimeError(
                "Controlled Razorpay Test Mode API failure "
                "for graceful-failure demonstration."
            )

            result = run_growth_workflow(
                failure_snapshot,
                merchant_id="demo-merchant-failure",
                mode="test",
            )

    except Exception as error:

        result = {
            "success": False,
            "stage": "payment_link_creation",
            "reason": str(error),
        }

    if not result["success"]:

        st.markdown(
            """
            <div class="failure-panel">

                <div class="failure-title">
                    ⚠ Razorpay Failure Handled Gracefully
                </div>

                <div>
                    The payment provider failed, and the
                    autonomous workflow stopped safely.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        failure_col1, failure_col2 = st.columns(2)

        with failure_col1:

            st.markdown(
                f"""
                **Failure Stage**

                `{result['stage']}`
                """
            )

        with failure_col2:

            st.markdown(
                f"""
                **Provider Response**

                {result['reason']}
                """
            )

        st.write("")

        st.markdown(
            """
            ### Safety Response

            | Check | Result |
            |---|---|
            | Failure detected | ✅ |
            | Failure recorded | ✅ |
            | Workflow stopped | ✅ |
            | Fake payment link | ❌ Not generated |
            | Fake `short_url` | ❌ Not returned |
            """
        )


# ============================================================
# Audit Trail
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">Audit Trail</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Structured events generated by the growth workflow."
)


def get_growth_audit_events():

    if not AUDIT_LOG_PATH.exists():
        return []

    events = []

    try:

        with AUDIT_LOG_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                try:

                    event = json.loads(line)

                except json.JSONDecodeError:

                    continue

                event_name = event.get(
                    "event",
                    "",
                )

                if (
                    event_name.startswith("GROWTH_")
                    or event_name.startswith("UPSELL_")
                    or event_name.startswith("PAYMENT_LINK_")
                ):

                    events.append(event)

    except OSError:

        return []

    return events


audit_events = get_growth_audit_events()


if not audit_events:

    st.info(
        "No growth workflow events recorded yet."
    )

else:

    for event in reversed(
        audit_events[-12:]
    ):

        event_name = event.get(
            "event",
            "UNKNOWN",
        )

        status = event.get(
            "status",
            "INFO",
        )

        timestamp = event.get(
            "timestamp",
            "",
        )

        if status == "PASS":

            icon = "✅"

        elif status == "FAIL":

            icon = "❌"

        else:

            icon = "ℹ️"

        st.markdown(
            f"""
            <div class="audit-event">

                <div class="audit-event-name">
                    {icon} {event_name}
                </div>

                <div class="audit-time">
                    {timestamp}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

