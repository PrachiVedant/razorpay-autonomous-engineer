import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [loading, setLoading] = useState(false);
  const [failureLoading, setFailureLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [auditEvents, setAuditEvents] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);

  // -------------------------------------------------------
  // Fetch real audit trail from FastAPI
  // -------------------------------------------------------

  const fetchAudit = async () => {
    setAuditLoading(true);

    try {
      const response = await fetch(`${API_URL}/audit`);

      if (!response.ok) {
        throw new Error("Failed to fetch audit trail");
      }

      const data = await response.json();

      setAuditEvents(data.events || []);
    } catch (error) {
      console.error("Audit fetch failed:", error);
    } finally {
      setAuditLoading(false);
    }
  };

  // -------------------------------------------------------
  // Load audit trail when dashboard opens
  // -------------------------------------------------------

  useEffect(() => {
    fetchAudit();
  }, []);

  // -------------------------------------------------------
  // Execute real growth workflow
  // -------------------------------------------------------

  const executeGrowth = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/growth/execute`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mode: "test",
          }),
        }
      );

      const data = await response.json();

      setResult(data);

      await fetchAudit();
    } catch (error) {
      console.error("Growth execution failed:", error);

      setResult({
        success: false,
        stage: "frontend",
        reason: error.message,
      });

      await fetchAudit();
    } finally {
      setLoading(false);
    }
  };

  // -------------------------------------------------------
  // Execute controlled Razorpay failure
  // -------------------------------------------------------

  const executeFailureSimulation = async () => {
    setFailureLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/growth/simulate-failure`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mode: "test",
          }),
        }
      );

      const data = await response.json();

      setResult(data);

      await fetchAudit();
    } catch (error) {
      console.error(
        "Failure simulation failed:",
        error
      );

      setResult({
        success: false,
        stage: "frontend",
        reason: error.message,
      });

      await fetchAudit();
    } finally {
      setFailureLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">

      {/* ===================================================
          HEADER
      =================================================== */}

      <header className="border-b bg-white">

        <div className="mx-auto max-w-7xl px-6 py-5">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-xs font-bold tracking-widest text-slate-500">
                RAZORPAY BUILDATHON 2026
              </p>

              <h1 className="mt-1 text-2xl font-bold tracking-tight">
                Autonomous Growth Agent
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                AI Growth & Agentic Commerce
              </p>

            </div>

            <div className="rounded-full border bg-slate-50 px-4 py-2 text-sm font-semibold">
              Test Mode
            </div>

          </div>

        </div>

      </header>


      {/* ===================================================
          MAIN
      =================================================== */}

      <main className="mx-auto max-w-7xl px-6 py-8">

        {/* -------------------------------------------------
            INTRO
        ------------------------------------------------- */}

        <div className="max-w-3xl">

          <h2 className="text-3xl font-bold tracking-tight">
            Turn merchant data into revenue.
          </h2>

          <p className="mt-3 text-base leading-7 text-slate-600">
            The autonomous agent identifies a high-value
            product, finds an evidence-backed upsell,
            validates a deterministic policy boundary,
            creates a Razorpay Test Mode payment link,
            and records every money action.
          </p>

        </div>


        {/* =================================================
            KPI CARDS
        ================================================= */}

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            label="Environment"
            value="Test Mode"
          />

          <MetricCard
            label="Autonomy Limit"
            value="10%"
          />

          <MetricCard
            label="Merchant"
            value="Demo Merchant"
          />

          <MetricCard
            label="Currency"
            value="INR"
          />

        </div>


        {/* =================================================
            GROWTH WORKFLOW
        ================================================= */}

        <section className="mt-10">

          <SectionHeader
            title="Growth Workflow"
            subtitle="Evidence → Policy → Execution → Audit"
          />

          <div className="mt-5 grid gap-3 md:grid-cols-5">

            <WorkflowStep
              number="01"
              title="Analyze Merchant"
              description="Find valuable products"
            />

            <WorkflowStep
              number="02"
              title="Find Upsell"
              description="Use merchant evidence"
            />

            <WorkflowStep
              number="03"
              title="Policy Validation"
              description="Enforce 10% limit"
            />

            <WorkflowStep
              number="04"
              title="Payment Link"
              description="Execute in Test Mode"
            />

            <WorkflowStep
              number="05"
              title="Audit Trail"
              description="Record every action"
            />

          </div>

        </section>


        {/* =================================================
            MERCHANT OPPORTUNITY
        ================================================= */}

        <section className="mt-10">

          <SectionHeader
            title="Merchant Opportunity"
            subtitle="The opportunity selected by the growth agent"
          />

          <div className="mt-5 grid gap-5 lg:grid-cols-2">

            {/* High value product */}

            <div className="rounded-2xl border bg-white p-6 shadow-sm">

              <p className="text-xs font-bold tracking-wider text-slate-400">
                HIGH-VALUE PRODUCT
              </p>

              <h3 className="mt-3 text-2xl font-bold">
                Premium Annual Plan
              </h3>

              <div className="mt-6 flex items-end justify-between">

                <div>

                  <p className="text-sm text-slate-500">
                    Product price
                  </p>

                  <p className="mt-1 text-3xl font-bold">
                    ₹50,000
                  </p>

                </div>

                <div className="text-right">

                  <p className="text-sm text-slate-500">
                    Historical purchases
                  </p>

                  <p className="mt-1 text-xl font-bold">
                    100
                  </p>

                </div>

              </div>

            </div>


            {/* Upsell */}

            <div className="rounded-2xl border bg-white p-6 shadow-sm">

              <p className="text-xs font-bold tracking-wider text-slate-400">
                EVIDENCE-BACKED UPSELL
              </p>

              <h3 className="mt-3 text-2xl font-bold">
                Premium Support
              </h3>

              <div className="mt-6 flex items-end justify-between">

                <div>

                  <p className="text-sm text-slate-500">
                    Upsell price
                  </p>

                  <p className="mt-1 text-3xl font-bold">
                    ₹5,000
                  </p>

                </div>

                <div className="text-right">

                  <p className="text-sm text-slate-500">
                    Historical conversion
                  </p>

                  <p className="mt-1 text-xl font-bold">
                    25%
                  </p>

                </div>

              </div>

            </div>

          </div>

        </section>


        {/* =================================================
            AI RECOMMENDATION
        ================================================= */}

        <section className="mt-10">

          <SectionHeader
            title="AI Recommendation"
            subtitle="The agent's proposed revenue action"
          />

          <div className="mt-5 grid gap-5 lg:grid-cols-[2fr_1fr]">

            <div className="rounded-2xl border bg-white p-6 shadow-sm">

              <div className="flex items-start justify-between gap-4">

                <div>

                  <p className="text-sm font-semibold text-slate-500">
                    Recommended offer
                  </p>

                  <h3 className="mt-2 text-2xl font-bold">
                    Premium Annual Plan
                    <span className="mx-2 text-slate-300">
                      +
                    </span>
                    Premium Support
                  </h3>

                </div>

                <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                  Evidence-backed
                </span>

              </div>

              <div className="mt-6 space-y-3">

                <Reason text="Highest-value merchant product selected." />

                <Reason text="Upsell supported by historical merchant evidence." />

                <Reason text="Upsell amount is within the autonomous policy boundary." />

              </div>

            </div>


            {/* Amount breakdown */}

            <div className="rounded-2xl border bg-white p-6 shadow-sm">

              <AmountRow
                label="Base Amount"
                value="₹50,000"
              />

              <AmountRow
                label="Upsell"
                value="+₹5,000"
              />

              <div className="my-4 border-t" />

              <AmountRow
                label="Customer Pays"
                value="₹55,000"
                highlight
              />

            </div>

          </div>


          <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4">

            <p className="text-sm font-semibold text-amber-900">
              Deterministic Safety Boundary
            </p>

            <p className="mt-1 text-sm leading-6 text-amber-800">
              The policy engine validates that the upsell
              is exactly 10% of the base product before
              any financial action is executed.
            </p>

          </div>

        </section>


        {/* =================================================
            EXECUTION
        ================================================= */}

        <section className="mt-10">

          <SectionHeader
            title="Execute Growth Action"
            subtitle="Financial actions are executed only after policy validation"
          />

          <div className="mt-5 rounded-2xl border bg-white p-6 shadow-sm">

            <div className="grid gap-4 md:grid-cols-2">

              <button
                onClick={executeGrowth}
                disabled={loading || failureLoading}
                className="rounded-xl bg-slate-900 px-6 py-4 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {loading
                  ? "Creating Payment Link..."
                  : "🚀 Create Payment Link"}

              </button>


              <button
                onClick={executeFailureSimulation}
                disabled={loading || failureLoading}
                className="rounded-xl border border-red-200 bg-red-50 px-6 py-4 text-sm font-bold text-red-700 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {failureLoading
                  ? "Simulating Failure..."
                  : "⚠️ Simulate Razorpay Failure"}

              </button>

            </div>

            <p className="mt-4 text-center text-xs text-slate-400">
              Test Mode only • No live customer payment is created
            </p>

          </div>

        </section>


        {/* =================================================
            RESULT
        ================================================= */}

        {result && (

          <section className="mt-8">

            {result.success ? (

              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">

                <div className="flex items-start gap-4">

                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 text-lg text-emerald-700">
                    ✓
                  </div>

                  <div className="flex-1">

                    <h3 className="text-lg font-bold text-emerald-900">
                      Payment Link Created Successfully
                    </h3>

                    <p className="mt-1 text-sm text-emerald-800">
                      The autonomous growth action completed
                      successfully in Razorpay Test Mode.
                    </p>


                    <div className="mt-5 grid gap-4 md:grid-cols-3">

                      <ResultCard
                        label="Customer Amount"
                        value={`₹${Number(
                          result.amount || 0
                        ).toLocaleString("en-IN")}`}
                      />

                      <ResultCard
                        label="Payment Link ID"
                        value={
                          result.payment_link_id ||
                          "Not available"
                        }
                        small
                      />

                      <div className="rounded-xl border border-emerald-200 bg-white p-4">

                        <p className="text-xs font-semibold text-slate-500">
                          Payment URL
                        </p>

                        {result.short_url ? (

                          <a
                            href={result.short_url}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-2 inline-block text-sm font-bold text-emerald-700 underline"
                          >
                            Open Razorpay Link →
                          </a>

                        ) : (

                          <p className="mt-2 text-sm text-slate-500">
                            Not available
                          </p>

                        )}

                      </div>

                    </div>

                  </div>

                </div>

              </div>

            ) : (

              <div className="rounded-2xl border border-red-200 bg-red-50 p-6">

                <div className="flex items-start gap-4">

                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100 text-lg font-bold text-red-700">
                    !
                  </div>

                  <div>

                    <h3 className="text-lg font-bold text-red-900">
                      Razorpay Failure Handled Safely
                    </h3>

                    <p className="mt-1 text-sm text-red-800">
                      The workflow stopped without claiming
                      that a payment link was created.
                    </p>

                    <div className="mt-5 grid gap-4 md:grid-cols-2">

                      <ResultCard
                        label="Workflow Stage"
                        value={
                          result.stage ||
                          "Unknown"
                        }
                        danger
                      />

                      <ResultCard
                        label="Status"
                        value="Stopped Safely"
                        danger
                      />

                    </div>

                    <div className="mt-4 rounded-xl border border-red-200 bg-white p-4">

                      <p className="text-xs font-semibold text-slate-500">
                        Failure Reason
                      </p>

                      <p className="mt-2 text-sm font-medium text-red-700">
                        {result.reason ||
                          "Unknown failure"}
                      </p>

                    </div>

                    <div className="mt-5 space-y-2 text-sm text-red-800">

                      <p>✓ Payment link creation failed.</p>

                      <p>✓ Workflow stopped immediately.</p>

                      <p>✓ No Payment Link ID was fabricated.</p>

                      <p>✓ No short URL was fabricated.</p>

                      <p>✓ Failure was recorded in the audit trail.</p>

                    </div>

                  </div>

                </div>

              </div>

            )}

          </section>

        )}


        {/* =================================================
            AUDIT TRAIL
        ================================================= */}

        <section className="mt-12">

          <div className="flex items-center justify-between">

            <SectionHeader
              title="Audit Trail"
              subtitle="Live events recorded by the autonomous workflow"
            />

            <button
              onClick={fetchAudit}
              disabled={auditLoading}
              className="rounded-lg border bg-white px-4 py-2 text-sm font-semibold shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
            >
              {auditLoading
                ? "Refreshing..."
                : "🔄 Refresh"}
            </button>

          </div>


          <div className="mt-5 space-y-3">

            {auditEvents.length === 0 ? (

              <div className="rounded-2xl border bg-white p-8 text-center">

                <p className="font-semibold text-slate-600">
                  No audit events yet.
                </p>

                <p className="mt-1 text-sm text-slate-400">
                  Execute a growth action to generate
                  audit events.
                </p>

              </div>

            ) : (

              auditEvents.map((event, index) => (

                <AuditEvent
                  key={`${event.timestamp}-${index}`}
                  event={event}
                />

              ))

            )}

          </div>

        </section>


        {/* =================================================
            WHY THIS FITS
        ================================================= */}

        <section className="mt-12">

          <SectionHeader
            title="Why This Fits AI Growth & Agentic Commerce"
            subtitle="The agent is autonomous, but its financial authority is bounded."
          />

          <div className="mt-5 grid gap-5 md:grid-cols-3">

            <FeatureCard
              icon="📈"
              title="Revenue Growth"
              text="Identifies the highest-value product and increases order value using evidence-backed upselling."
            />

            <FeatureCard
              icon="🛡️"
              title="Bounded Money Actions"
              text="Every payment action passes deterministic policy validation before execution."
            />

            <FeatureCard
              icon="📋"
              title="Explainable Audit Trail"
              text="Every decision, payment request, success, and failure is recorded without exposing secrets."
            />

          </div>

        </section>

      </main>


      {/* ===================================================
          FOOTER
      =================================================== */}

      <footer className="border-t bg-white">

        <div className="mx-auto max-w-7xl px-6 py-6 text-center text-xs text-slate-400">

          Razorpay AI Growth Agent • Test Mode •
          Evidence → Policy → Execution → Audit

        </div>

      </footer>

    </div>
  );
}


// =========================================================
// COMPONENTS
// =========================================================

function MetricCard({ label, value }) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-xl font-bold">
        {value}
      </p>

    </div>
  );
}


function WorkflowStep({
  number,
  title,
  description,
}) {
  return (
    <div className="rounded-xl border bg-white p-4 shadow-sm">

      <div className="flex items-center gap-3">

        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">
          {number}
        </span>

        <div>

          <p className="text-sm font-bold">
            {title}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {description}
          </p>

        </div>

      </div>

    </div>
  );
}


function SectionHeader({
  title,
  subtitle,
}) {
  return (
    <div>

      <h2 className="text-xl font-bold tracking-tight">
        {title}
      </h2>

      <p className="mt-1 text-sm text-slate-500">
        {subtitle}
      </p>

    </div>
  );
}


function Reason({ text }) {
  return (
    <div className="flex items-start gap-3">

      <span className="mt-0.5 text-emerald-600">
        ✓
      </span>

      <p className="text-sm text-slate-600">
        {text}
      </p>

    </div>
  );
}


function AmountRow({
  label,
  value,
  highlight = false,
}) {
  return (
    <div className="flex items-center justify-between">

      <span className="text-sm text-slate-500">
        {label}
      </span>

      <span
        className={
          highlight
            ? "text-xl font-bold"
            : "font-semibold"
        }
      >
        {value}
      </span>

    </div>
  );
}


function ResultCard({
  label,
  value,
  small = false,
  danger = false,
}) {
  return (
    <div
      className={`rounded-xl border p-4 ${
        danger
          ? "border-red-200 bg-white"
          : "border-emerald-200 bg-white"
      }`}
    >

      <p className="text-xs font-semibold text-slate-500">
        {label}
      </p>

      <p
        className={`mt-2 font-bold ${
          small
            ? "break-all text-xs"
            : danger
            ? "text-red-700"
            : "text-emerald-700"
        }`}
      >
        {value}
      </p>

    </div>
  );
}


function AuditEvent({ event }) {
  const status = event.status;

  const isPass = status === "PASS";
  const isFail = status === "FAIL";

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <div className="flex items-start justify-between gap-4">

        <div className="flex min-w-0 gap-3">

          <div
            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
              isPass
                ? "bg-emerald-100 text-emerald-700"
                : isFail
                ? "bg-red-100 text-red-700"
                : "bg-slate-100 text-slate-600"
            }`}
          >
            {isPass
              ? "✓"
              : isFail
              ? "!"
              : "i"}
          </div>


          <div className="min-w-0">

            <p className="break-words font-semibold">
              {formatEventName(event.event)}
            </p>

            {event.timestamp && (

              <p className="mt-1 text-xs text-slate-400">
                {formatTimestamp(event.timestamp)}
              </p>

            )}

            {event.details && (

              <div className="mt-3 flex flex-wrap gap-2">

                {Object.entries(event.details)
                  .filter(
                    ([key]) =>
                      !isSensitiveField(key)
                  )
                  .map(([key, value]) => (

                    <span
                      key={key}
                      className="rounded-lg bg-slate-50 px-3 py-1.5 text-xs text-slate-600"
                    >
                      <span className="font-semibold">
                        {formatKey(key)}:
                      </span>{" "}
                      {String(value)}
                    </span>

                  ))}

              </div>

            )}

          </div>

        </div>


        <span
          className={`shrink-0 rounded-full px-3 py-1 text-xs font-bold ${
            isPass
              ? "bg-emerald-50 text-emerald-700"
              : isFail
              ? "bg-red-50 text-red-700"
              : "bg-slate-100 text-slate-600"
          }`}
        >
          {status}
        </span>

      </div>

    </div>
  );
}


// =========================================================
// HELPERS
// =========================================================

function formatEventName(value) {
  if (!value) {
    return "Unknown Event";
  }

  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}


function formatKey(value) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}


function formatTimestamp(timestamp) {
  try {
    return new Date(timestamp).toLocaleString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }
    );
  } catch {
    return timestamp;
  }
}


function isSensitiveField(key) {
  const sensitiveFields = [
    "secret",
    "password",
    "token",
    "key_secret",
    "key_id",
    "api_key",
    "authorization",
  ];

  return sensitiveFields.includes(
    key.toLowerCase()
  );
}


function FeatureCard({
  icon,
  title,
  text,
}) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <div className="text-2xl">
        {icon}
      </div>

      <h3 className="mt-4 font-bold">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-slate-500">
        {text}
      </p>

    </div>
  );
}


export default App;