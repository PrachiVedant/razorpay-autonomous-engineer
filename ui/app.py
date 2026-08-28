import json
import os
import sys
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv


# =========================================================
# PROJECT SETUP
# =========================================================

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

load_dotenv(
    os.path.join(ROOT_DIR, ".env")
)


# =========================================================
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(
    page_title="Razorpay AI Growth Agent",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# LOAD WORKFLOW SAFELY
# =========================================================

WORKFLOW_IMPORT_ERROR = None
run_growth_workflow = None

try:
    from agents.growth_workflow import run_growth_workflow
except Exception as e:
    WORKFLOW_IMPORT_ERROR = e


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main application */
    .stApp {
        background-color: #f7f8fc;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #111827 !important;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px;
    }

    /* Cards */
    .custom-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 10px;
    }

    .card-label {
        font-size: 12px;
        font-weight: 700;
        color: #667085;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }

    .card-description {
        font-size: 14px;
        color: #667085;
    }

    /* Workflow step */
    .workflow-step {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        min-height: 75px;
    }

    .workflow-number {
        font-size: 12px;
        font-weight: 700;
        color: #667085;
    }

    .workflow-name {
        font-size: 14px;
        font-weight: 600;
        color: #111827;
        margin-top: 5px;
    }

    /* Audit */
    .audit-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .footer {
        text-align: center;
        color: #667085;
        font-size: 13px;
        margin-top: 30px;
        padding-bottom: 20px;
    }

    /* Small text */
    .muted {
        color: #667085;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MERCHANT DATA
# =========================================================

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


# =========================================================
# AUDIT FILE
# =========================================================

AUDIT_FILE = os.path.join(
    ROOT_DIR,
    "audit_log.jsonl",
)


# =========================================================
# AUDIT HELPERS
# =========================================================

def read_audit(limit=12):
    """
    Read the latest audit events.

    Invalid JSON lines are ignored so that a corrupted
    audit entry does not crash the entire Streamlit app.
    """

    if not os.path.exists(AUDIT_FILE):
        return []

    events = []

    try:
        with open(
            AUDIT_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                try:
                    event = json.loads(line)

                    if isinstance(event, dict):
                        events.append(event)

                except json.JSONDecodeError:
                    continue

    except Exception:
        return []

    return events[-limit:][::-1]


def format_time(value):
    """
    Convert ISO timestamp to HH:MM:SS.
    """

    if not value:
        return ""

    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        ).strftime("%H:%M:%S")

    except Exception:
        return str(value)


# =========================================================
# HEADER
# =========================================================

st.caption(
    "RAZORPAY BUILDATHON 2026 • AI GROWTH & AGENTIC COMMERCE"
)

st.title("💳 Autonomous Growth Agent")

st.write(
    """
    An AI agent that increases merchant revenue by identifying a
    high-value product, applying an evidence-backed bounded upsell,
    validating deterministic policy rules, creating a Razorpay
    Test Mode payment link, and recording every money action
    in an audit trail.
    """
)


# =========================================================
# WORKFLOW IMPORT STATUS
# =========================================================

if WORKFLOW_IMPORT_ERROR is not None:

    st.error(
        "The Streamlit interface loaded, but the growth workflow "
        "could not be imported."
    )

    with st.expander("Show workflow import error"):

        st.code(
            repr(WORKFLOW_IMPORT_ERROR),
            language="text",
        )

    st.warning(
        "The UI below is still available. Fix the import error "
        "above before executing a growth action."
    )


# =========================================================
# KPI ROW
# =========================================================

st.subheader("System Status")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Environment",
        "Test Mode",
    )

with k2:
    st.metric(
        "Autonomy Limit",
        "10%",
    )

with k3:
    st.metric(
        "Merchant",
        "Demo Merchant",
    )

with k4:
    st.metric(
        "Currency",
        "INR",
    )


st.divider()


# =========================================================
# WORKFLOW PIPELINE
# =========================================================

st.subheader("Growth Workflow")

steps = [
    ("01", "Analyze Merchant"),
    ("02", "Find Upsell"),
    ("03", "Policy Validation"),
    ("04", "Create Payment Link"),
    ("05", "Audit Trail"),
]

flow = st.columns(5)

for col, (number, name) in zip(flow, steps):

    with col:

        st.markdown(
            f"""
            <div class="workflow-step">
                <div class="workflow-number">
                    STEP {number}
                </div>
                <div class="workflow-name">
                    {name}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.progress(
    1.0,
    text="Growth workflow ready",
)

st.divider()


# =========================================================
# MERCHANT OPPORTUNITY
# =========================================================

st.subheader("Merchant Opportunity")

product_col, upsell_col = st.columns(2)

with product_col:

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-label">
                HIGH-VALUE PRODUCT
            </div>

            <div class="card-title">
                Premium Annual Plan
            </div>

            <div class="card-description">
                Selected because it is the merchant's highest-value
                product with 100 historical purchases.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.metric(
        "Product Price",
        "₹50,000",
    )

    st.caption(
        "100 historical purchases"
    )


with upsell_col:

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-label">
                EVIDENCE-BACKED UPSELL
            </div>

            <div class="card-title">
                Premium Support
            </div>

            <div class="card-description">
                Historical merchant evidence shows a 25% conversion
                rate for this upsell.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.metric(
        "Upsell Price",
        "₹5,000",
    )

    st.caption(
        "25% historical conversion rate"
    )


st.divider()


# =========================================================
# AI RECOMMENDATION
# =========================================================

st.subheader("AI Recommendation")

left, right = st.columns([2, 1])

with left:

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-label">
                AGENT DECISION
            </div>

            <div class="card-title">
                Premium Annual Plan + Premium Support
            </div>

            <div class="card-description">

                The agent recommends adding Premium Support to the
                Premium Annual Plan because the upsell is supported
                by historical merchant evidence.

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "Evidence-backed recommendation"
    )

    st.markdown(
        """
        **Why this decision was made**

        - Highest-value product selected.
        - Historical purchases provide evidence.
        - Premium Support has a 25% conversion rate.
        - Upsell is exactly 10% of the base product.
        - Deterministic policy validation is required before execution.
        """
    )


with right:

    st.metric(
        "Base Amount",
        "₹50,000",
    )

    st.metric(
        "Upsell",
        "+₹5,000",
    )

    st.metric(
        "Customer Pays",
        "₹55,000",
    )


st.info(
    "Policy Boundary: ₹5,000 upsell = exactly 10% of the ₹50,000 base product."
)


st.divider()


# =========================================================
# EXECUTE GROWTH ACTION
# =========================================================

st.subheader("Execute Growth Action")

col1, col2 = st.columns(2)

with col1:

    create_payment = st.button(
        "🚀 Create Payment Link",
        type="primary",
        use_container_width=True,
        disabled=WORKFLOW_IMPORT_ERROR is not None,
    )


with col2:

    simulate_failure = st.button(
        "⚠️ Simulate Razorpay Failure",
        use_container_width=True,
        disabled=WORKFLOW_IMPORT_ERROR is not None,
    )


# =========================================================
# SUCCESS FLOW
# =========================================================

if create_payment:

    merchant_id = (
        "merchant-demo-"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
    )

    with st.spinner(
        "Running autonomous growth workflow..."
    ):

        try:

            result = run_growth_workflow(
                MERCHANT_SNAPSHOT,
                merchant_id=merchant_id,
                mode="test",
            )

        except Exception as e:

            result = {
                "success": False,
                "stage": "workflow_execution",
                "reason": str(e),
            }

    st.divider()

    if result.get("success"):

        st.success(
            "✅ Payment Link created successfully."
        )

        a, b = st.columns(2)

        with a:

            st.metric(
                "Customer Amount",
                f"₹{result.get('amount', 0):,}",
            )

            st.write(
                "**Payment Link ID**"
            )

            payment_link_id = result.get(
                "payment_link_id"
            )

            if payment_link_id:

                st.code(
                    payment_link_id
                )

            else:

                st.warning(
                    "No Payment Link ID returned."
                )

        with b:

            st.write(
                "**Razorpay Short URL**"
            )

            short_url = result.get(
                "short_url"
            )

            if short_url:

                st.markdown(
                    f"[🔗 Open Razorpay Payment Link]({short_url})"
                )

            else:

                st.warning(
                    "No short URL returned."
                )

        st.success(
            "The merchant can immediately share this payment link with the customer."
        )

    else:

        st.error(
            "❌ Workflow failed."
        )

        st.write(
            result.get(
                "reason",
                "Unknown workflow error.",
            )
        )

        st.write(
            "**Workflow Stage:**",
            result.get(
                "stage",
                "unknown",
            ),
        )


# =========================================================
# CONTROLLED FAILURE DEMONSTRATION
# =========================================================

if simulate_failure:

    try:

        import agents.growth_workflow as workflow

        original_create_payment_link = (
            workflow.create_payment_link
        )

        def fake_failure(**kwargs):

            raise RuntimeError(
                "Controlled Razorpay Test Mode API failure "
                "for graceful demonstration."
            )

        workflow.create_payment_link = fake_failure

        try:

            with st.spinner(
                "Executing controlled failure..."
            ):

                result = run_growth_workflow(
                    MERCHANT_SNAPSHOT,
                    merchant_id="failure-demo",
                    mode="test",
                )

        finally:

            workflow.create_payment_link = (
                original_create_payment_link
            )

    except Exception as e:

        result = {
            "success": False,
            "stage": "payment_link_creation",
            "reason": str(e),
        }

    st.divider()

    st.error(
        "⚠️ Razorpay failure handled safely."
    )

    left, right = st.columns(2)

    with left:

        st.metric(
            "Workflow Stage",
            result.get(
                "stage",
                "unknown",
            ),
        )

    with right:

        st.metric(
            "Status",
            "Stopped Safely",
        )

    st.warning(
        result.get(
            "reason",
            "Controlled payment failure.",
        )
    )

    st.write(
        "### Agent Response"
    )

    st.markdown(
        """
        - Payment link creation failed.
        - Workflow stopped immediately.
        - No Payment Link ID was fabricated.
        - No short URL was fabricated.
        - No second payment attempt was made.
        - Failure was recorded in the audit trail.
        """
    )


st.divider()


# =========================================================
# AUDIT TRAIL
# =========================================================

header, refresh_col = st.columns(
    [5, 1]
)

with header:

    st.subheader(
        "📋 Audit Trail"
    )

with refresh_col:

    refresh = st.button(
        "🔄 Refresh",
        use_container_width=True,
    )

if refresh:

    st.rerun()


events = read_audit(
    limit=12
)


if not events:

    st.info(
        "No audit events yet. Execute a growth action to generate the audit trail."
    )

else:

    for event in events:

        status = str(
            event.get(
                "status",
                "INFO",
            )
        ).upper()

        if status == "PASS":

            icon = "✅"

        elif status == "FAIL":

            icon = "❌"

        else:

            icon = "ℹ️"

        event_name = event.get(
            "event",
            "Unknown Event",
        )

        timestamp = format_time(
            event.get(
                "timestamp",
                "",
            )
        )

        with st.container():

            st.markdown(
                f"""
                <div class="audit-card">

                    <strong>
                        {icon} {event_name}
                    </strong>

                    <div class="muted">
                        {timestamp}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if status == "PASS":

                st.success(
                    "PASS"
                )

            elif status == "FAIL":

                st.error(
                    "FAIL"
                )

            else:

                st.info(
                    "INFO"
                )

            details = event.get(
                "details",
                {},
            )

            if isinstance(details, dict):

                for key, value in details.items():

                    key_lower = str(
                        key
                    ).lower()

                    if key_lower in {
                        "secret",
                        "password",
                        "token",
                        "key_secret",
                        "key_id",
                        "api_key",
                    }:

                        continue

                    st.write(
                        f"**{str(key).replace('_', ' ').title()}** : {value}"
                    )


st.divider()


# =========================================================
# WHY THIS FITS RAZORPAY BUILDATHON
# =========================================================

st.subheader(
    "Why this fits AI Growth & Agentic Commerce"
)

f1, f2, f3 = st.columns(3)


with f1:

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-title">
                📈 Revenue Growth
            </div>

            <div class="card-description">
                The agent identifies a high-value product and
                increases potential order value through an
                evidence-backed upsell.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with f2:

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-title">
                🛡️ Bounded Money Actions
            </div>

            <div class="card-description">
                The agent cannot arbitrarily change prices.
                A deterministic policy boundary validates the
                upsell before the payment action.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with f3:

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-title">
                📋 Explainable Audit Trail
            </div>

            <div class="card-description">
                Decisions, policy validation, payment attempts,
                successful actions, and controlled failures are
                recorded without exposing secrets.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ARCHITECTURE SUMMARY
# =========================================================

st.subheader(
    "Agent Execution Model"
)

st.markdown(
    """
    **Evidence → Decision → Policy → Execution → Audit**

    The agent does not directly perform an unrestricted money action.

    1. **Evidence** — Analyze merchant products and historical upsell data.
    2. **Decision** — Select the highest-value product and evidence-backed upsell.
    3. **Policy** — Verify the upsell is within the 10% autonomous boundary.
    4. **Execution** — Create the Razorpay Test Mode Payment Link.
    5. **Audit** — Record the action and its result, including failures.
    """
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        Razorpay AI Growth Agent • Test Mode
        <br>
        Evidence → Policy → Execution → Audit
    </div>
    """,
    unsafe_allow_html=True,
)