from rzp_gate.outcome_verifier import verify_payment_link


def test_valid_payment_link_is_verified():

    result = verify_payment_link(
        {
            "id": "plink_test_001",
            "short_url": "https://rzp.io/test",
            "amount": 49900,
            "currency": "INR",
        },
        expected_amount=499,
    )

    assert result["verified"] is True


def test_missing_payment_link_id_is_rejected():

    result = verify_payment_link(
        {
            "short_url": "https://rzp.io/test",
            "amount": 49900,
            "currency": "INR",
        },
        expected_amount=499,
    )

    assert result["verified"] is False

    assert "missing its ID" in result["reason"]


def test_missing_short_url_is_rejected():

    result = verify_payment_link(
        {
            "id": "plink_test_001",
            "amount": 49900,
            "currency": "INR",
        },
        expected_amount=499,
    )

    assert result["verified"] is False

    assert "short URL" in result["reason"]


def test_incorrect_amount_is_rejected():

    result = verify_payment_link(
        {
            "id": "plink_test_001",
            "short_url": "https://rzp.io/test",
            "amount": 99900,
            "currency": "INR",
        },
        expected_amount=499,
    )

    assert result["verified"] is False

    assert "amount does not match" in result["reason"]


def test_incorrect_currency_is_rejected():

    result = verify_payment_link(
        {
            "id": "plink_test_001",
            "short_url": "https://rzp.io/test",
            "amount": 49900,
            "currency": "USD",
        },
        expected_amount=499,
    )

    assert result["verified"] is False

    assert "currency does not match" in result["reason"]


def test_malformed_response_is_rejected():

    result = verify_payment_link(
        None,
        expected_amount=499,
    )

    assert result["verified"] is False

    assert "not a dictionary" in result["reason"]