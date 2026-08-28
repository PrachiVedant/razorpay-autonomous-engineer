# Razorpay Autonomous Growth Agent

An autonomous merchant-growth system that identifies evidence-backed upsell opportunities, applies deterministic financial constraints, and executes a verified Razorpay Payment Link in Test Mode.

> **AI decides what growth opportunity to pursue. Deterministic controls decide what financial action is allowed.**

---

## 1. Problem

Merchants have valuable transaction, payment, and product data, but often lack an automated mechanism that can convert this data into actionable revenue opportunities.

Traditional analytics systems can identify:

* High-value products
* Payment conversion patterns
* Failed payment patterns
* Historical upsell behavior
* Potential revenue opportunities

However, identifying an opportunity is fundamentally different from safely executing a financial action.

An autonomous commerce system must therefore solve two problems simultaneously:

1. Identify a commercially meaningful opportunity from merchant evidence.
2. Execute that opportunity without allowing AI-generated decisions to exceed predefined financial boundaries.

The core challenge is maintaining **autonomy while preserving financial safety, determinism, and observability**.

---

## 2. Solution

The **Razorpay Autonomous Growth Agent** addresses this by separating intelligence from financial authority.

The system:

1. Builds a structured merchant snapshot from merchant data.
2. Evaluates historical product and upsell evidence.
3. Selects the strongest growth opportunity.
4. Calculates the proposed transaction value.
5. Passes the proposal through a deterministic policy engine.
6. Executes the approved action through Razorpay Test Mode.
7. Verifies the returned Payment Link against the expected transaction.
8. Records the complete money-action lifecycle in an audit trail.

The Growth Agent does **not** have unrestricted authority over financial execution.

Instead:

```text
AI proposes
    ↓
Policy validates
    ↓
Razorpay executes
    ↓
Outcome is verified
    ↓
Audit records what happened
```

This separation enables autonomous decision-making without giving the AI unrestricted financial authority.

---

# 3. System Design

The architecture separates merchant intelligence, autonomous growth reasoning, financial authorization, payment execution, verification, and auditability.

### System Architecture

<img width="1811" height="428" alt="image" src="https://github.com/user-attachments/assets/c67cfd9e-6049-49ca-9488-102a4e88b241" />



The system establishes clear boundaries between:

* Merchant data and analytics
* Growth opportunity discovery
* Deterministic financial policy
* Razorpay payment execution
* Outcome verification
* Auditability

The Growth Agent proposes an opportunity, while deterministic controls independently determine whether the proposed financial action is permitted.

---

## 4. Architectural Components

### 4.1 Merchant Data Layer

The merchant data layer provides the Growth Agent with a controlled interface to merchant information.

The agent does not directly manipulate the underlying merchant data files.

The merchant snapshot combines:

```text
Revenue Metrics
      +
Payment Metrics
      +
Payment Method Metrics
      +
Product Information
      +
Historical Upsell Evidence
```

The primary interface is:

```python
get_merchant_snapshot()
```

The resulting structured snapshot is passed to the Growth Agent as evidence for opportunity discovery.

---

### 4.2 Growth Agent

The Growth Agent is responsible for **opportunity identification**, not financial authorization.

Its responsibilities include:

* Validating product information
* Evaluating historical upsell evidence
* Generating candidate opportunities
* Calculating expected incremental revenue
* Measuring evidence strength
* Calculating confidence
* Ranking candidate opportunities
* Selecting the strongest opportunity

For example, the merchant evidence can identify:

```text
Base Product:
Premium Annual Plan

Base Amount:
₹50,000

Upsell:
Premium Support

Upsell Amount:
₹5,000

Historical Conversion:
25%

Expected Incremental Revenue:
₹1,250
```

The resulting proposal is:

```text
Premium Annual Plan
        +
Premium Support
        =
₹55,000
```

This remains a **proposal** until it passes the deterministic financial policy.

---

## 5. Deterministic Financial Policy

The proposed opportunity is passed through a deterministic policy layer before any Razorpay action occurs.

The policy engine enforces the configured financial boundary.

For this implementation:

```text
Maximum Autonomous Upsell = 10%
```

For the example above:

```text
Base Amount       = ₹50,000
Maximum Upsell    = ₹5,000
Actual Upsell     = ₹5,000
Upsell Percentage = 10%

Policy Result     = ALLOWED
```

The policy is deterministic and independent of the Growth Agent's reasoning.

This prevents an AI-generated recommendation from bypassing the financial constraint.

Conceptually:

```text
AI Recommendation
        │
        ▼
┌──────────────────────┐
│ Deterministic Policy │
│                      │
│ Upsell ≤ 10%         │
│ Test Mode only       │
└──────────┬───────────┘
           │
      ┌────┴────┐
      │         │
   Allowed   Rejected
      │         │
      ▼         ▼
  Execute     Stop
```

---

## 6. Razorpay Execution Layer

Once the policy approves the opportunity, the workflow creates a Razorpay Payment Link.

The execution layer is isolated from the Growth Agent.

The workflow constructs:

```text
Amount
Currency
Description
Reference ID
```

and submits the request to Razorpay Test Mode.

Razorpay execution is kept behind a dedicated integration boundary.

This ensures:

```text
Growth Intelligence ≠ Payment Execution
```

The Growth Agent determines **what should be attempted**.

The Razorpay integration determines **how the approved financial action is executed**.

---

## 7. Outcome Verification

A successful API response is not treated as sufficient evidence of a valid execution.

After Razorpay returns the Payment Link response, the system verifies the outcome against the expected transaction.

Verification includes:

* Payment Link existence
* Payment Link ID
* Short URL
* Expected amount
* Expected currency

Only after successful verification does the workflow report:

```text
success = true
```

The execution lifecycle therefore follows:

```text
Request
   ↓
Razorpay Response
   ↓
Verification
   ↓
Verified Outcome
   ↓
Success
```

rather than:

```text
Request
   ↓
Razorpay Response
   ↓
Assume Success
```

This distinction is critical for autonomous financial systems.

---

## 8. Failure Safety

Financial execution failures are treated as first-class outcomes.

If Razorpay execution fails:

```text
Payment Link Creation
        ↓
      FAILURE
        ↓
Workflow Stops
        ↓
No fabricated Payment Link
        ↓
No fabricated Short URL
        ↓
Failure recorded in Audit Trail
```

Similarly, if outcome verification fails, the system does not convert the response into a successful workflow result.

The workflow explicitly catches execution failures and returns a structured failure state.

This provides **graceful degradation instead of silent or misleading success**.

---

## 9. Audit Trail

Every important money-action boundary is recorded in an append-only JSONL audit log.

The audit trail records events such as:

```text
GROWTH_OPPORTUNITY_IDENTIFIED
        ↓
UPSELL_PROPOSED
        ↓
UPSELL_POLICY_VALIDATED
        ↓
PAYMENT_LINK_REQUESTED
        ↓
PAYMENT_LINK_OUTCOME_VERIFIED
        ↓
PAYMENT_LINK_CREATED
        ↓
GROWTH_WORKFLOW_COMPLETED
```

Failure states are also recorded:

```text
UPSELL_POLICY_REJECTED
        ↓
GROWTH_WORKFLOW_FAILED
```

or:

```text
PAYMENT_LINK_CREATION_FAILED
        ↓
GROWTH_WORKFLOW_FAILED
```

Sensitive fields are sanitized before audit information is exposed through the API.

This creates an observable chain from:

```text
Evidence
   →
Decision
   →
Policy
   →
Execution
   →
Verification
   →
Outcome
```

---

## 10. API Layer

The backend is implemented using **FastAPI**.

The primary execution endpoint is:

```http
POST /growth/execute
```

The request accepts:

```json
{
  "mode": "test"
}
```

The API intentionally restricts the execution environment to Test Mode.

A successful response follows a stable contract:

```json
{
  "success": true,
  "stage": "completed",
  "reason": null,
  "amount": 55000,
  "currency": "INR",
  "payment_link_id": "...",
  "short_url": "...",
  "opportunity": {}
}
```

The API normalizes workflow responses so that the frontend receives a consistent structure for both successful and unsuccessful executions.

---

## 11. Frontend

The frontend provides an operational view of the autonomous growth workflow.

It exposes:

* Merchant evidence
* Selected growth opportunity
* Transaction calculation
* Policy boundary
* Workflow state
* Payment Link result
* Outcome status
* Audit trail

The frontend communicates with the FastAPI backend rather than directly accessing merchant data or Razorpay credentials.

The communication flow is:

```text
React Frontend
      │
      │ HTTP
      ▼
FastAPI API
      │
      ▼
Growth Workflow
      │
      ├── Merchant Layer
      ├── Growth Agent
      ├── Policy Engine
      ├── Razorpay Integration
      ├── Outcome Verification
      └── Audit Layer
```

---

## 12. Technology Stack

| Layer                  | Technology         |
| ---------------------- | ------------------ |
| Frontend               | React              |
| Styling                | Tailwind CSS       |
| Backend                | FastAPI            |
| Validation             | Pydantic           |
| Agent Logic            | Python             |
| Payment Integration    | Razorpay Test Mode |
| Merchant Data          | JSON               |
| Audit Storage          | JSONL              |
| Environment Management | `.env`             |
| Package Management     | `uv`               |
| Testing                | Pytest             |

---

## 13. Project Structure

```text
razorpay-autonomous-engineer/
│
├── agents/
│   ├── growth_workflow.py
│   └── ...
│
├── api/
│   └── main.py
│
├── audit/
│   └── ...
│
├── merchant/
│   ├── data.py
│   ├── analytics.py
│   ├── growth_agent.py
│   └── tools.py
│
├── merchant_data/
│   ├── merchant.json
│   ├── orders.json
│   ├── payments.json
│   └── products.json
│
├── rzp_gate/
│   ├── upsell_policy.py
│   ├── outcome_verifier.py
│   └── ...
│
├── rzp_tools/
│   └── payment_link.py
│
├── frontend/
│   └── src/
│       └── App.jsx
│
├── tests/
│
├── audit_log.jsonl
├── config.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

The repository separates:

* Agent reasoning
* API orchestration
* Merchant data
* Policy enforcement
* Razorpay integration
* Outcome verification
* Auditability

into distinct modules.

---

---

## 14. Design Principles

### Bounded Autonomy

The AI can identify and recommend a revenue opportunity, but financial execution remains constrained by deterministic policy.

### Separation of Concerns

Merchant data, agent reasoning, policy enforcement, payment execution, verification, and auditability are isolated into separate components.

### Deterministic Financial Control

Financial boundaries are enforced through explicit programmatic rules rather than LLM judgment.

### Verified Execution

The system verifies the result of a financial API operation before declaring success.

### Failure Transparency

A failed financial operation remains a failed operation.

The system does not fabricate:

* Payment Link IDs
* Short URLs
* Transaction outcomes
* Successful execution states

### Auditability

Important decisions and financial boundaries are recorded so that the execution can be inspected after the fact.

---

## 15. Why This Is Agentic Commerce

This system goes beyond analytics because the agent does not stop at recommending an action.

It performs the complete decision-to-execution cycle:

```text
Observe
  ↓
Reason
  ↓
Propose
  ↓
Validate
  ↓
Act
  ↓
Verify
  ↓
Record
```

The critical distinction is that autonomy is **bounded**.

The system combines:

* AI-driven opportunity discovery
* Merchant-specific evidence
* Deterministic financial policy
* Payment infrastructure
* Outcome verification
* Auditable execution

This creates an architecture for autonomous commerce where the AI can pursue measurable business outcomes while remaining constrained by explicit financial controls.

---

## 16. Running the Project

### Backend

Install dependencies using `uv`:

```bash
uv sync
```

Configure the required environment variables in `.env`.

Start the FastAPI server:

```bash
uv run uvicorn api.main:app --reload --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

### Frontend

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend communicates with the FastAPI backend running on port `8000`.

---

## 17. Testing

Run the complete test suite:

```bash
uv run pytest -v
```

The test suite covers the merchant data layer, analytics, API behavior, and autonomous growth workflow.

---

## 18. Security Considerations

The system incorporates multiple security boundaries:

* Razorpay credentials are supplied through environment configuration.
* Only Test Mode execution is accepted by the API.
* Sensitive fields are redacted from audit responses.
* Sensitive execution errors are sanitized before being returned through the API.
* The Growth Agent does not directly access payment credentials.
* Financial authorization is separated from AI-generated recommendations.
* Payment outcomes are verified before successful completion is reported.
* Financial constraints are enforced deterministically.

---

## 19. Key Outcome

The Razorpay Autonomous Growth Agent demonstrates a practical architecture for **AI Growth + Agentic Commerce**.

```text
Merchant Evidence
       ↓
Autonomous Growth Decision
       ↓
Deterministic Financial Guardrail
       ↓
Razorpay Payment Execution
       ↓
Outcome Verification
       ↓
Auditable Result
```

The result is an autonomous growth system capable of taking a merchant-specific revenue opportunity from **evidence to verified financial execution**, while maintaining explicit boundaries around financial authority.
