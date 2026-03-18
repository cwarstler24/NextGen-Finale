from unittest.mock import MagicMock

import populate_test_data


def _make_logger():
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    return logger


def test_returns_error_when_not_test_environment(monkeypatch):
    fake_db_pool = MagicMock()
    fake_db_pool.get_environment.return_value = "DEV"
    fake_db_pool.get_schema.return_value = "APP"
    fake_db_pool.is_test_environment.return_value = False

    fake_logger = _make_logger()

    monkeypatch.setattr(populate_test_data, "db_pool", fake_db_pool)
    monkeypatch.setattr(populate_test_data, "LOGGER", fake_logger)

    result = populate_test_data.main()

    assert result == 1
    fake_db_pool.populate_test_data.assert_not_called()


def test_returns_zero_when_user_cancels(monkeypatch):
    fake_db_pool = MagicMock()
    fake_db_pool.get_environment.return_value = "TEST"
    fake_db_pool.get_schema.return_value = "TEST_SCHEMA"
    fake_db_pool.is_test_environment.return_value = True

    fake_logger = _make_logger()

    monkeypatch.setattr(populate_test_data, "db_pool", fake_db_pool)
    monkeypatch.setattr(populate_test_data, "LOGGER", fake_logger)
    monkeypatch.setattr("builtins.input", lambda _prompt: "no")

    result = populate_test_data.main()

    assert result == 0
    fake_db_pool.populate_test_data.assert_not_called()


def test_returns_error_when_population_blocked(monkeypatch):
    fake_db_pool = MagicMock()
    fake_db_pool.get_environment.return_value = "TEST"
    fake_db_pool.get_schema.return_value = "TEST_SCHEMA"
    fake_db_pool.is_test_environment.return_value = True
    fake_db_pool.populate_test_data.return_value = {
        "status": "blocked",
        "reason": "Not running in TEST",
    }

    fake_logger = _make_logger()

    monkeypatch.setattr(populate_test_data, "db_pool", fake_db_pool)
    monkeypatch.setattr(populate_test_data, "LOGGER", fake_logger)
    monkeypatch.setattr("builtins.input", lambda _prompt: "yes")

    result = populate_test_data.main()

    assert result == 1


def test_reports_success_empty_warning_and_errors(monkeypatch):
    fake_db_pool = MagicMock()
    fake_db_pool.get_environment.return_value = "TEST"
    fake_db_pool.get_schema.return_value = "TEST_SCHEMA"
    fake_db_pool.is_test_environment.return_value = True
    fake_db_pool.populate_test_data.return_value = {
        "TBBUN_TYPES": {"status": "success", "inserted": 2},
        "TBTOPPINGS": {"status": "empty", "inserted": 0},
        "TBBAD": {"status": "error", "error": "insert failed"},
        "TBWEIRD": "unexpected",
    }

    fake_logger = _make_logger()

    monkeypatch.setattr(populate_test_data, "db_pool", fake_db_pool)
    monkeypatch.setattr(populate_test_data, "LOGGER", fake_logger)
    monkeypatch.setattr("builtins.input", lambda _prompt: "y")

    result = populate_test_data.main()

    assert result == 1
    fake_logger.warning.assert_called_once()


def test_returns_zero_when_all_tables_succeed(monkeypatch):
    fake_db_pool = MagicMock()
    fake_db_pool.get_environment.return_value = "TEST"
    fake_db_pool.get_schema.return_value = "TEST_SCHEMA"
    fake_db_pool.is_test_environment.return_value = True
    fake_db_pool.populate_test_data.return_value = {
        "TBFRY_TYPES": {"status": "success", "inserted": 3},
        "TBFRY_SIZES": {"status": "success", "inserted": 2},
    }

    fake_logger = _make_logger()

    monkeypatch.setattr(populate_test_data, "db_pool", fake_db_pool)
    monkeypatch.setattr(populate_test_data, "LOGGER", fake_logger)
    monkeypatch.setattr("builtins.input", lambda _prompt: "yes")

    result = populate_test_data.main()

    assert result == 0
