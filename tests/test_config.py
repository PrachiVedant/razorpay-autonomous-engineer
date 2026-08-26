import importlib


def test_config_defaults(monkeypatch):

    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )

    monkeypatch.delenv(
        "TEST_COMMAND",
        raising=False,
    )

    monkeypatch.delenv(
        "MAX_REPAIR_RETRIES",
        raising=False,
    )

    import config

    importlib.reload(config)

    assert config.OPENAI_MODEL == "gpt-4o-mini"

    assert (
        config.TEST_COMMAND
        == "uv run pytest tests/"
    )

    assert config.MAX_REPAIR_RETRIES == 3


def test_config_environment_override(monkeypatch):

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model",
    )

    monkeypatch.setenv(
        "TEST_COMMAND",
        "uv run pytest tests/test_sample.py",
    )

    monkeypatch.setenv(
        "MAX_REPAIR_RETRIES",
        "5",
    )

    import config

    importlib.reload(config)

    assert config.OPENAI_MODEL == "test-model"

    assert (
        config.TEST_COMMAND
        == "uv run pytest tests/test_sample.py"
    )

    assert config.MAX_REPAIR_RETRIES == 5


def test_required_environment_variable():

    import config

    try:
        config.get_env(
            "THIS_VARIABLE_DOES_NOT_EXIST",
            required=True,
        )

    except RuntimeError as error:

        assert (
            "THIS_VARIABLE_DOES_NOT_EXIST"
            in str(error)
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )