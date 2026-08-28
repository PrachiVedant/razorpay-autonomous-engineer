from fastapi.testclient import TestClient

from api.main import (
    app,
    normalize_growth_response,
)


client = TestClient(app)

def test_health_check():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

def test_audit_endpoint():

    response = client.get("/audit")

    assert response.status_code == 200

    data = response.json()

    assert "events" in data


def test_live_mode_is_rejected():

    response = client.post(
        "/growth/execute",
        json={
            "mode": "live",
        },
    )

    assert response.status_code == 422


def test_invalid_mode_is_rejected():

    response = client.post(
        "/growth/execute",
        json={
            "mode": "production",
        },
    )

    assert response.status_code == 422


def test_test_mode_is_accepted():

    response = client.post(
        "/growth/execute",
        json={
            "mode": "test",
        },
    )

    assert response.status_code == 200

def test_normalize_growth_response_success():

    result = normalize_growth_response(
        {
            "success": True,
            "stage": "completed",
            "amount": 55000,
            "payment_link_id": "plink_test_001",
            "short_url": "https://rzp.io/test",
            "opportunity": {
                "opportunity": "bounded_upsell",
            },
        }
    )

    assert result["success"] is True

    assert result["stage"] == "completed"

    assert result["amount"] == 55000

    assert result["currency"] == "INR"

    assert (
        result["payment_link_id"]
        == "plink_test_001"
    )

    assert (
        result["short_url"]
        == "https://rzp.io/test"
    )

    assert result["opportunity"] is not None


def test_normalize_growth_response_failure():

    result = normalize_growth_response(
        {
            "success": False,
            "stage": "outcome_verification",
            "reason": (
                "Invalid Payment Link response."
            ),
        }
    )

    assert result["success"] is False

    assert (
        result["stage"]
        == "outcome_verification"
    )

    assert (
        result["reason"]
        == "Invalid Payment Link response."
    )

    assert result["amount"] is None

    assert result["payment_link_id"] is None

    assert result["short_url"] is None

    assert result["currency"] == "INR"