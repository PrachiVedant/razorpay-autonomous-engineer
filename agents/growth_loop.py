from rzp_gate.action_registry import (
    get_action,
    record_action,
)

from audit.logger import log_event
from agents.growth_agent import identify_growth_opportunity
from agents.opportunity_validator import validate_opportunity
from rzp_gate.policy import validate_payment_plan
from rzp_gate.actions import RazorpayActions

from razorpay.errors import (
    BadRequestError,
    ServerError,
    GatewayError,
)

from merchant.data import get_orders


def run_growth_cycle():
    """
    End-to-end growth cycle:

        Opportunity (LLM)
          ↓
        Validation (deterministic, against ground-truth data)
          ↓
        Policy gate (allowed? needs human approval?)
          ↓
        Idempotency check
          ↓
        Execution (Razorpay test-mode API call)
          ↓
        Record successful action
          ↓
        Audit log at every step
    """

    log_event(
        "GROWTH_CYCLE_STARTED",
        agent="growth_loop",
    )

    # --------------------------------------------------
    # 1. LLM identifies an opportunity from real data
    # --------------------------------------------------

    opportunity = identify_growth_opportunity()

    log_event(
        "OPPORTUNITY_IDENTIFIED",
        agent="growth_agent",
        data=opportunity,
    )

    # --------------------------------------------------
    # 2. Deterministic validation
    # --------------------------------------------------

    validation = validate_opportunity(opportunity)

    log_event(
        "OPPORTUNITY_VALIDATED",
        agent="opportunity_validator",
        data=validation,
    )

    if not validation["valid"]:

        log_event(
            "GROWTH_CYCLE_REJECTED",
            agent="growth_loop",
            data={
                "reason": validation["reason"],
            },
        )

        return {
            "status": "rejected",
            "reason": validation["reason"],
        }

    # --------------------------------------------------
    # 3. Policy gate
    # --------------------------------------------------

    plan = {
        "requires_razorpay": True,
        "payment_operation": "payment_link",
        "risk_level": "medium",
    }

    policy = validate_payment_plan(plan)

    log_event(
        "POLICY_DECISION",
        agent="policy",
        data=policy,
    )

    if not policy["allowed"]:

        log_event(
            "GROWTH_CYCLE_BLOCKED",
            agent="growth_loop",
            data=policy,
        )

        return {
            "status": "blocked",
            "reason": policy["reason"],
        }

    if policy["requires_approval"]:

        log_event(
            "HUMAN_APPROVAL_REQUIRED",
            agent="growth_loop",
            data=policy,
        )

        return {
            "status": "awaiting_approval",
            "plan": plan,
            "opportunity": opportunity,
        }

    # --------------------------------------------------
    # 4. Find recoverable orders
    # --------------------------------------------------

    orders = [
        order
        for order in get_orders()
        if order["status"] in ("abandoned", "failed")
    ]

    if not orders:

        log_event(
            "NO_TARGET_ORDERS",
            agent="growth_loop",
        )

        return {
            "status": "no_action",
            "reason": "No recoverable orders found",
        }

    target_order = orders[0]

    order_id = target_order["order_id"]

    # --------------------------------------------------
    # 5. Idempotency / duplicate-action protection
    # --------------------------------------------------

    existing_action = get_action(order_id)

    if existing_action:

        log_event(
            "DUPLICATE_ACTION_PREVENTED",
            agent="growth_loop",
            data={
                "order_id": order_id,
                "existing_action": existing_action,
            },
        )

        return {
            "status": "already_processed",
            "order_id": order_id,
            "existing_action": existing_action,
        }

    # --------------------------------------------------
    # 6. Execute Razorpay action
    # --------------------------------------------------

    actions = RazorpayActions()

    try:

        link = actions.create_recovery_payment_link(
            target_order
        )

        # --------------------------------------------------
        # 7. Record successful action
        # --------------------------------------------------

        record_action(
            order_id,
            {
                "action": "payment_link_created",
                "link_id": link.get("id"),
                "short_url": link.get("short_url"),
            },
        )

        log_event(
            "PAYMENT_LINK_CREATED",
            agent="razorpay_actions",
            data={
                "order_id": order_id,
                "link_id": link.get("id"),
                "short_url": link.get("short_url"),
            },
        )

        return {
            "status": "completed",
            "payment_link": link,
        }

    # --------------------------------------------------
    # 8. Permanent / invalid request failure
    # --------------------------------------------------

    except BadRequestError as error:

        log_event(
            "PAYMENT_LINK_FAILED",
            agent="razorpay_actions",
            data={
                "order_id": order_id,
                "error": str(error),
                "action_taken": "escalated_to_human",
            },
        )

        return {
            "status": "failed",
            "reason": str(error),
            "escalated": True,
        }

    # --------------------------------------------------
    # 9. Transient Razorpay failure
    # --------------------------------------------------

    except (ServerError, GatewayError) as error:

        log_event(
            "PAYMENT_LINK_RETRY",
            agent="razorpay_actions",
            data={
                "order_id": order_id,
                "error": str(error),
            },
        )

        try:

            link = actions.create_recovery_payment_link(
                target_order
            )

            # Record successful retry as well
            record_action(
                order_id,
                {
                    "action": "payment_link_created",
                    "link_id": link.get("id"),
                    "short_url": link.get("short_url"),
                    "attempts": 2,
                },
            )

            log_event(
                "PAYMENT_LINK_CREATED_ON_RETRY",
                agent="razorpay_actions",
                data={
                    "order_id": order_id,
                    "link_id": link.get("id"),
                },
            )

            return {
                "status": "completed",
                "payment_link": link,
                "attempts": 2,
            }

        except Exception as retry_error:

            log_event(
                "PAYMENT_LINK_FAILED_FINAL",
                agent="razorpay_actions",
                data={
                    "order_id": order_id,
                    "error": str(retry_error),
                },
            )

            return {
                "status": "failed",
                "reason": str(retry_error),
                "attempts": 2,
            }