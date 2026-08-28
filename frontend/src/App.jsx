import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

const WORKFLOW_STAGES = [
  {
    number: "01",
    title: "Analyze Merchant",
    description: "Identify valuable products",
  },
  {
    number: "02",
    title: "Find Upsell",
    description: "Use merchant evidence",
  },
  {
    number: "03",
    title: "Policy Validation",
    description: "Enforce 10% boundary",
  },
  {
    number: "04",
    title: "Payment Link",
    description: "Execute in Test Mode",
  },
  {
    number: "05",
    title: "Audit Trail",
    description: "Record the outcome",
  },
];

function App() {
  const [loading, setLoading] = useState(false);
  const [failureLoading, setFailureLoading] = useState(false);
  const [result, setResult] = useState(null);

  const [auditEvents, setAuditEvents] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);

  const [activeStage, setActiveStage] = useState(null);

  // =========================================================
  // FETCH AUDIT
  // =========================================================

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

  useEffect(() => {
    fetchAudit();
  }, []);

  // =========================================================
  // EXECUTE GROWTH WORKFLOW
  // =========================================================

  const executeGrowth = async () => {
    setLoading(true);
    setFailureLoading(false);
    setResult(null);

    setActiveStage(1);

    try {
      const response = await fetch(`${API_URL}/growth/execute`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mode: "test",
        }),
      });

      const data = await response.json();

      console.log("GROWTH EXECUTE RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data.reason ||
            data.detail ||
            `Backend returned HTTP ${response.status}`
        );
      }

      // -------------------------------------------------------
      // Stage 1: Analyze Merchant
      // -------------------------------------------------------

      setActiveStage(1);

      await delay(300);

      // -------------------------------------------------------
      // Stage 2: Find Upsell
      // -------------------------------------------------------

      setActiveStage(2);

      await delay(300);

      // -------------------------------------------------------
      // Stage 3: Policy Validation
      // -------------------------------------------------------

      setActiveStage(3);

      await delay(300);

      // -------------------------------------------------------
      // Stage 4: Payment Link
      // -------------------------------------------------------

      setActiveStage(4);

      await delay(300);

      // -------------------------------------------------------
      // Stage 5: Audit Trail
      // -------------------------------------------------------

      if (data.success === true) {
        setActiveStage(5);
      } else {
        /*
         * The backend explicitly reported a controlled failure.
         *
         * We keep the workflow at the payment stage rather than
         * pretending that a successful payment link was created.
         */
        setActiveStage(4);
      }

      setResult(data);

      await fetchAudit();
    } catch (error) {
      console.error("Growth execution failed:", error);

      setActiveStage(null);

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

  // =========================================================
  // CONTROLLED FAILURE SIMULATION
  // =========================================================

  const executeFailureSimulation = async () => {
    setFailureLoading(true);
    setLoading(false);
    setResult(null);

    setActiveStage(1);

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

      console.log("FAILURE SIMULATION RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data.reason ||
            data.detail ||
            `Backend returned HTTP ${response.status}`
        );
      }

      // Failure is deliberately injected at payment stage.
      setActiveStage(4);

      setResult(data);

      await fetchAudit();

      // Allow the UI to show the stopped state.
      await delay(500);

      setActiveStage(null);
    } catch (error) {
      console.error(
        "Failure simulation failed:",
        error
      );

      setActiveStage(null);

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

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="sticky top-0 z-20 border-b bg-white/95 backdrop-blur">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

          <div className="flex items-center gap-4">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-sm font-bold text-white">
              R
            </div>

            <div>

              <p className="text-[11px] font-bold tracking-[0.2em] text-slate-400">
                RAZORPAY BUILDATHON 2026
              </p>

              <h1 className="text-lg font-bold">
                Autonomous Growth Agent
              </h1>

            </div>

          </div>

          <div className="flex items-center gap-3">

            <div className="hidden rounded-full border bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600 sm:block">
              AI Growth & Agentic Commerce
            </div>

            <div className="flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-bold text-amber-700">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              TEST MODE
            </div>

          </div>

        </div>

      </header>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="mx-auto max-w-7xl px-6 py-10">

        {/* ===================================================
            HERO
        =================================================== */}

        <section className="grid gap-8 lg:grid-cols-[1.5fr_1fr] lg:items-center">

          <div>

            <div className="mb-4 inline-flex items-center gap-2 rounded-full border bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm">

              <span className="h-2 w-2 rounded-full bg-emerald-500" />

              Autonomous revenue optimization

            </div>

            <h2 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl">

              Turn merchant data

              <span className="block text-slate-500">
                into revenue.
              </span>

            </h2>

            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600">

              The growth agent analyzes merchant behavior,
              identifies an evidence-backed upsell,
              validates a deterministic safety policy,
              and executes a Razorpay Test Mode payment action.

            </p>

          </div>


          {/* Hero status */}

          <div className="rounded-2xl border bg-white p-6 shadow-sm">

            <div className="flex items-center justify-between">

              <div>

                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Agent Status
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {loading || failureLoading
                    ? "Executing"
                    : "Ready"}
                </p>

              </div>

              <div
                className={`flex h-12 w-12 items-center justify-center rounded-full ${
                  loading || failureLoading
                    ? "bg-amber-100 text-amber-700"
                    : "bg-emerald-100 text-emerald-700"
                }`}
              >
                {loading || failureLoading ? "…" : "✓"}
              </div>

            </div>

            <div className="mt-6 border-t pt-5">

              <div className="flex items-center justify-between text-sm">

                <span className="text-slate-500">
                  Financial authority
                </span>

                <span className="font-bold">
                  Bounded
                </span>

              </div>

              <div className="mt-3 flex items-center justify-between text-sm">

                <span className="text-slate-500">
                  Maximum upsell
                </span>

                <span className="font-bold">
                  10%
                </span>

              </div>

              <div className="mt-3 flex items-center justify-between text-sm">

                <span className="text-slate-500">
                  Environment
                </span>

                <span className="font-bold">
                  Razorpay Test Mode
                </span>

              </div>

            </div>

          </div>

        </section>


        {/* ===================================================
            KPI CARDS
        =================================================== */}

        <section className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            label="Merchant"
            value={
              result?.opportunity?.merchant_name ||
              "Demo Merchant"
            }
            icon="◆"
          />

          <MetricCard
            label="Base Product"
            value={formatRupees(
              result?.opportunity?.base_amount,
              "₹50,000"
            )}
            icon="₹"
          />

          <MetricCard
            label="Allowed Upsell"
            value={formatRupees(
              result?.opportunity?.upsell_amount,
              "₹5,000"
            )}
            icon="+"
          />

          <MetricCard
            label="Customer Value"
            value={formatRupees(
              result?.opportunity?.final_amount ||
                result?.amount,
              "₹55,000"
            )}
            icon="↗"
          />

        </section>


        {/* ===================================================
            WORKFLOW
        =================================================== */}

        <section className="mt-12">

          <SectionHeader
            title="Autonomous Growth Workflow"
            subtitle="Evidence → Policy → Execution → Verification → Audit"
          />

          <div className="mt-6 grid gap-3 md:grid-cols-5">

            {WORKFLOW_STAGES.map((stage, index) => (

              <WorkflowStep
                key={stage.number}
                {...stage}
                active={
                  activeStage !== null &&
                  activeStage === index + 1
                }
                completed={
                  activeStage !== null &&
                  activeStage > index + 1
                }
              />

            ))}

          </div>

        </section>


        {/* ===================================================
            MERCHANT EVIDENCE
        =================================================== */}

        <section className="mt-12">

          <SectionHeader
            title="Merchant Evidence"
            subtitle="Why the agent selected this revenue opportunity"
          />

          <div className="mt-6 grid gap-5 lg:grid-cols-2">

            <EvidenceCard
              label="Highest-Value Product"
              title={
                result?.opportunity?.base_product_name ||
                "Premium Annual Plan"
              }
              amount={formatRupees(
                result?.opportunity?.base_amount,
                "₹50,000"
              )}
              metric={
                result?.opportunity?.base_product_evidence ||
                result?.opportunity?.historical_purchases ||
                "100 historical purchases"
              }
              description={
                result?.opportunity?.base_product_reason ||
                "The agent identifies the merchant's highest-value product as the base offer."
              }
            />

            <EvidenceCard
              label="Evidence-Backed Upsell"
              title={
                result?.opportunity?.upsell_product_name ||
                "Premium Support"
              }
              amount={formatRupees(
                result?.opportunity?.upsell_amount,
                "₹5,000"
              )}
              metric={
                result?.opportunity?.upsell_evidence ||
                result?.opportunity?.conversion_rate ||
                "25% historical conversion"
              }
              description={
                result?.opportunity?.upsell_reason ||
                result?.opportunity?.evidence ||
                "Historical merchant behavior provides evidence for the support upsell."
              }
            />

          </div>

        </section>


        {/* ===================================================
            RECOMMENDATION
        =================================================== */}

        <section className="mt-12">

          <SectionHeader
            title="AI Recommendation"
            subtitle="The agent proposes the revenue action before execution"
          />

          <div className="mt-6 grid gap-5 lg:grid-cols-[1.6fr_1fr]">

            <div className="rounded-2xl border bg-white p-6 shadow-sm">

              <div className="flex flex-wrap items-start justify-between gap-4">

                <div>

                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Recommended offer
                  </p>

                  <h3 className="mt-2 text-2xl font-bold">

                    {result?.opportunity?.base_product_name ||
                      "Premium Annual Plan"}

                    <span className="mx-2 text-slate-300">
                      +
                    </span>

                    {result?.opportunity?.upsell_product_name ||
                      "Premium Support"}

                  </h3>

                </div>

                <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700">
                  Evidence-backed
                </span>

              </div>


              <div className="mt-7 space-y-4">

                <Reason
                  title="Product selection"
                  text={
                    result?.opportunity?.base_product_reason ||
                    result?.opportunity?.reason ||
                    "Highest-value product selected from merchant data."
                  }
                />

                <Reason
                  title="Upsell selection"
                  text={
                    result?.opportunity?.upsell_reason ||
                    result?.opportunity?.evidence ||
                    "Premium Support is supported by historical conversion evidence."
                  }
                />

                <Reason
                  title="Financial boundary"
                  text={
                    result?.opportunity?.policy_reason ||
                    "Upsell amount remains within the deterministic 10% autonomy limit."
                  }
                />

              </div>

            </div>


            {/* Amount breakdown */}

            <div className="rounded-2xl border bg-white p-6 shadow-sm">

              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Transaction calculation
              </p>

              <div className="mt-6 space-y-5">

                <AmountRow
                  label="Base product"
                  value={formatRupees(
                    result?.opportunity?.base_amount,
                    "₹50,000"
                  )}
                />

                <AmountRow
                  label="Autonomous upsell"
                  value={`+ ${formatRupees(
                    result?.opportunity?.upsell_amount,
                    "₹5,000"
                  )}`}
                />

                <div className="border-t" />

                <AmountRow
                  label="Final customer amount"
                  value={formatRupees(
                    result?.opportunity?.final_amount ||
                      result?.amount,
                    "₹55,000"
                  )}
                  highlight
                />

              </div>

            </div>

          </div>


          {/* Policy */}

          <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-5">

            <div className="flex items-start gap-4">

              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-700">
                🛡
              </div>

              <div>

                <p className="font-bold text-amber-900">
                  Deterministic Safety Boundary
                </p>

                <p className="mt-1 text-sm leading-6 text-amber-800">

                  The AI can recommend the opportunity,
                  but it cannot override the policy engine.
                  The payment action proceeds only when the
                  upsell is within the configured 10% boundary.

                </p>

              </div>

            </div>

          </div>

        </section>


        {/* ===================================================
            EXECUTION
        =================================================== */}

        <section className="mt-12">

          <SectionHeader
            title="Execute Growth Action"
            subtitle="The agent can execute only inside the configured financial boundary"
          />

          <div className="mt-6 rounded-2xl border bg-white p-6 shadow-sm">

            <div className="grid gap-4 md:grid-cols-2">

              <button
                onClick={executeGrowth}
                disabled={loading || failureLoading}
                className="group rounded-xl bg-slate-900 px-6 py-4 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >

                <span className="flex items-center justify-center gap-2">

                  {loading ? (
                    <>
                      <span className="animate-spin">
                        ◌
                      </span>

                      Executing Growth Workflow...
                    </>
                  ) : (
                    <>
                      🚀
                      Create Payment Link
                    </>
                  )}

                </span>

              </button>


              <button
                onClick={executeFailureSimulation}
                disabled={loading || failureLoading}
                className="group rounded-xl border border-red-200 bg-red-50 px-6 py-4 text-sm font-bold text-red-700 transition hover:border-red-300 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
              >

                <span className="flex items-center justify-center gap-2">

                  {failureLoading ? (
                    <>
                      <span className="animate-spin">
                        ◌
                      </span>

                      Simulating Failure...
                    </>
                  ) : (
                    <>
                      ⚠
                      Simulate Razorpay Failure
                    </>
                  )}

                </span>

              </button>

            </div>

            <div className="mt-5 flex items-center justify-center gap-2 text-xs text-slate-400">

              <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />

              Test Mode only • No live customer payment is created

            </div>

          </div>

        </section>


        {/* ===================================================
            RESULT
        =================================================== */}

        {result && (

          <section className="mt-8">

            {result.success ? (
              <SuccessResult result={result} />
            ) : (
              <FailureResult result={result} />
            )}

          </section>

        )}


        {/* ===================================================
            AUDIT TRAIL
        =================================================== */}

        <section className="mt-14">

          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">

            <SectionHeader
              title="Audit Trail"
              subtitle="Every important money-action boundary is recorded"
            />

            <button
              onClick={fetchAudit}
              disabled={auditLoading}
              className="self-start rounded-lg border bg-white px-4 py-2 text-sm font-semibold shadow-sm transition hover:bg-slate-50 disabled:opacity-50 sm:self-auto"
            >

              {auditLoading
                ? "Refreshing..."
                : "↻ Refresh Audit"}

            </button>

          </div>


          <div className="mt-6">

            {auditEvents.length === 0 ? (

              <EmptyAudit />

            ) : (

              <div className="rounded-2xl border bg-white p-5 shadow-sm">

                <div className="space-y-0">

                  {auditEvents.map((event, index) => (

                    <AuditEvent
                      key={`${event.timestamp}-${index}`}
                      event={event}
                      last={
                        index === auditEvents.length - 1
                      }
                    />

                  ))}

                </div>

              </div>

            )}

          </div>

        </section>


        {/* ===================================================
            WHY THIS FITS
        =================================================== */}

        <section className="mt-14">

          <SectionHeader
            title="Why This Is Agentic Commerce"
            subtitle="Autonomy is useful only when financial authority is bounded and observable."
          />

          <div className="mt-6 grid gap-5 md:grid-cols-3">

            <FeatureCard
              icon="↗"
              title="Revenue Growth"
              text="The agent analyzes merchant evidence and identifies a concrete opportunity to increase transaction value."
            />

            <FeatureCard
              icon="◈"
              title="Bounded Autonomy"
              text="The AI proposes the action, while deterministic policy controls what financial actions are actually permitted."
            />

            <FeatureCard
              icon="✓"
              title="Verifiable Execution"
              text="Payment outcomes are verified and recorded. Failures stop safely instead of being represented as successful actions."
            />

          </div>

        </section>

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer className="mt-16 border-t bg-white">

        <div className="mx-auto max-w-7xl px-6 py-7">

          <div className="flex flex-col items-center justify-between gap-3 text-center sm:flex-row sm:text-left">

            <div>

              <p className="text-sm font-bold">
                Razorpay AI Growth Agent
              </p>

              <p className="mt-1 text-xs text-slate-400">
                Evidence → Policy → Execution → Verification → Audit
              </p>

            </div>

            <div className="rounded-full border bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-500">
              TEST MODE
            </div>

          </div>

        </div>

      </footer>

    </div>
  );
}


// =========================================================
// COMPONENTS
// =========================================================

function MetricCard({ label, value, icon }) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
            {label}
          </p>

          <p className="mt-2 text-xl font-bold">
            {value}
          </p>

        </div>

        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-slate-600">
          {icon}
        </div>

      </div>

    </div>
  );
}


// =========================================================
// WORKFLOW STEP
// =========================================================

function WorkflowStep({
  number,
  title,
  description,
  active,
  completed,
}) {
  return (
    <div
      className={`rounded-xl border p-4 shadow-sm transition ${
        active
          ? "border-amber-300 bg-amber-50"
          : completed
          ? "border-emerald-200 bg-emerald-50"
          : "bg-white"
      }`}
    >

      <div className="flex items-start gap-3">

        <span
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
            active
              ? "bg-amber-500 text-white"
              : completed
              ? "bg-emerald-600 text-white"
              : "bg-slate-900 text-white"
          }`}
        >
          {completed ? "✓" : number}
        </span>

        <div>

          <p className="text-sm font-bold">
            {title}
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            {description}
          </p>

        </div>

      </div>

    </div>
  );
}


// =========================================================
// SECTION HEADER
// =========================================================

function SectionHeader({ title, subtitle }) {
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


// =========================================================
// EVIDENCE CARD
// =========================================================

function EvidenceCard({
  label,
  title,
  amount,
  metric,
  description,
}) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
        {label}
      </p>

      <div className="mt-4 flex items-end justify-between gap-4">

        <div>

          <h3 className="text-2xl font-bold">
            {title}
          </h3>

          <p className="mt-2 text-3xl font-bold">
            {amount}
          </p>

        </div>

        <span className="rounded-lg bg-slate-50 px-3 py-2 text-right text-xs font-semibold text-slate-600">
          {metric}
        </span>

      </div>

      <p className="mt-5 border-t pt-4 text-sm leading-6 text-slate-500">
        {description}
      </p>

    </div>
  );
}


// =========================================================
// REASON
// =========================================================

function Reason({ title, text }) {
  return (
    <div className="flex items-start gap-3">

      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">
        ✓
      </span>

      <div>

        <p className="text-sm font-semibold">
          {title}
        </p>

        <p className="mt-1 text-sm leading-6 text-slate-500">
          {text}
        </p>

      </div>

    </div>
  );
}


// =========================================================
// AMOUNT ROW
// =========================================================

function AmountRow({
  label,
  value,
  highlight = false,
}) {
  return (
    <div className="flex items-center justify-between gap-4">

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


// =========================================================
// SUCCESS RESULT
// =========================================================

function SuccessResult({ result }) {
  const opportunity = result.opportunity || {};

  const amount =
    result.amount ??
    opportunity.final_amount ??
    0;

  return (
    <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">

      <div className="flex items-start gap-4">

        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-lg font-bold text-emerald-700">
          ✓
        </div>

        <div className="min-w-0 flex-1">

          <div className="flex flex-wrap items-start justify-between gap-3">

            <div>

              <h3 className="text-lg font-bold text-emerald-900">
                Payment Link Created Successfully
              </h3>

              <p className="mt-1 text-sm text-emerald-800">
                The autonomous growth action completed successfully in Razorpay Test Mode.
              </p>

            </div>

            <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-emerald-700">
              VERIFIED
            </span>

          </div>


          {/* Opportunity summary */}

          <div className="mt-5 rounded-xl border border-emerald-200 bg-white p-4">

            <p className="text-xs font-semibold text-slate-500">
              Executed Opportunity
            </p>

            <p className="mt-2 text-sm font-bold text-slate-900">

              {opportunity.base_product_name ||
                "Base Product"}

              <span className="mx-2 text-slate-300">
                +
              </span>

              {opportunity.upsell_product_name ||
                "Upsell"}

            </p>

          </div>


          <div className="mt-6 grid gap-4 md:grid-cols-3">

            <ResultCard
              label="Customer Amount"
              value={`₹${Number(
                amount
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
  );
}


// =========================================================
// FAILURE RESULT
// =========================================================

function FailureResult({ result }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-6">

      <div className="flex items-start gap-4">

        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-red-100 text-lg font-bold text-red-700">
          !
        </div>

        <div className="min-w-0 flex-1">

          <div className="flex flex-wrap items-start justify-between gap-3">

            <div>

              <h3 className="text-lg font-bold text-red-900">
                Razorpay Failure Handled Safely
              </h3>

              <p className="mt-1 text-sm text-red-800">
                The workflow stopped without claiming that a payment link was created.
              </p>

            </div>

            <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-red-700">
              STOPPED SAFELY
            </span>

          </div>


          <div className="mt-6 grid gap-4 md:grid-cols-2">

            <ResultCard
              label="Workflow Stage"
              value={formatEventName(
                result.stage || "Unknown"
              )}
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

            <p className="mt-2 break-words text-sm font-medium text-red-700">
              {result.reason ||
                result.error ||
                result.detail ||
                "Unknown failure"}
            </p>

          </div>


          <div className="mt-5 grid gap-2 text-sm text-red-800 sm:grid-cols-2">

            <SafetyCheck text="Payment link creation failed." />

            <SafetyCheck text="Workflow stopped immediately." />

            <SafetyCheck text="No Payment Link ID was fabricated." />

            <SafetyCheck text="No short URL was fabricated." />

            <SafetyCheck text="Failure was recorded in the audit trail." />

          </div>

        </div>

      </div>

    </div>
  );
}


// =========================================================
// SAFETY CHECK
// =========================================================

function SafetyCheck({ text }) {
  return (
    <div className="flex items-center gap-2">

      <span className="font-bold">
        ✓
      </span>

      <span>
        {text}
      </span>

    </div>
  );
}


// =========================================================
// RESULT CARD
// =========================================================

function ResultCard({
  label,
  value,
  small = false,
  danger = false,
}) {
  return (
    <div
      className={`rounded-xl border bg-white p-4 ${
        danger
          ? "border-red-200"
          : "border-emerald-200"
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


// =========================================================
// AUDIT EVENT
// =========================================================

function AuditEvent({ event, last }) {
  const status = event.status;

  const isPass = status === "PASS";
  const isFail = status === "FAIL";

  return (
    <div className="relative flex gap-4">

      {!last && (
        <div className="absolute left-[17px] top-10 h-full w-px bg-slate-200" />
      )}

      <div
        className={`relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
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


      <div className="min-w-0 flex-1 pb-6">

        <div className="flex flex-wrap items-start justify-between gap-3">

          <div>

            <p className="break-words font-semibold">
              {formatEventName(event.event)}
            </p>

            {event.timestamp && (

              <p className="mt-1 text-xs text-slate-400">
                {formatTimestamp(event.timestamp)}
              </p>

            )}

          </div>

          <span
            className={`rounded-full px-3 py-1 text-xs font-bold ${
              isPass
                ? "bg-emerald-50 text-emerald-700"
                : isFail
                ? "bg-red-50 text-red-700"
                : "bg-slate-100 text-slate-600"
            }`}
          >
            {status || "INFO"}
          </span>

        </div>


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
                  className="max-w-full break-words rounded-lg bg-slate-50 px-3 py-1.5 text-xs text-slate-600"
                >

                  <span className="font-semibold">
                    {formatKey(key)}:
                  </span>{" "}

                  {formatAuditValue(value)}

                </span>

              ))}

          </div>

        )}

      </div>

    </div>
  );
}


// =========================================================
// EMPTY AUDIT
// =========================================================

function EmptyAudit() {
  return (
    <div className="rounded-2xl border bg-white p-10 text-center shadow-sm">

      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-500">
        📋
      </div>

      <p className="mt-4 font-semibold text-slate-600">
        No audit events yet
      </p>

      <p className="mt-1 text-sm text-slate-400">
        Execute a growth action to generate the workflow audit trail.
      </p>

    </div>
  );
}


// =========================================================
// FEATURE CARD
// =========================================================

function FeatureCard({
  icon,
  title,
  text,
}) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-lg font-bold text-slate-700">
        {icon}
      </div>

      <h3 className="mt-5 font-bold">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-slate-500">
        {text}
      </p>

    </div>
  );
}


// =========================================================
// HELPERS
// =========================================================

function delay(ms) {
  return new Promise((resolve) =>
    setTimeout(resolve, ms)
  );
}


function formatRupees(value, fallback = "₹0") {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return fallback;
  }

  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return fallback;
  }

  return `₹${numericValue.toLocaleString("en-IN")}`;
}


function formatAuditValue(value) {
  if (
    value !== null &&
    typeof value === "object"
  ) {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }

  return String(value);
}


function formatEventName(value) {
  if (!value) {
    return "Unknown Event";
  }

  return String(value)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}


function formatKey(value) {
  return String(value)
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
    String(key).toLowerCase()
  );
}


export default App;