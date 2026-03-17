import json
from unittest.mock import MagicMock, mock_open, patch

import pytest

from main.backend.db_pool import DB2ConnectionPool


@pytest.fixture(autouse=True)
def reset_singleton():
    DB2ConnectionPool._instance = None
    yield
    DB2ConnectionPool._instance = None


def _make_pool():
    dummy_logger = MagicMock()
    with patch("main.backend.db_pool.LoggerFactory.get_general_logger", return_value=dummy_logger):
        pool = DB2ConnectionPool()
    return pool, dummy_logger


def _cursor_cm(cursor):
    ctx = MagicMock()
    ctx.__enter__.return_value = cursor
    ctx.__exit__.return_value = False
    return ctx


def test_load_database_setup_uses_defaults_when_keys_missing():
    pool, _ = _make_pool()
    with patch("builtins.open", mock_open(read_data=json.dumps({}))):
        pool._load_database_setup()

    assert pool.get_environment() == "PRODUCTION"
    assert pool.get_schema() == "TSTFAL"
    assert pool.get_test_data() == {}


def test_load_database_setup_reads_environment_schema_and_test_data():
    pool, _ = _make_pool()
    config = {
        "environment": "TEST",
        "schemas": {"TEST": "TSTFAL", "PRODUCTION": "SKYFAL"},
        "test_data": {"TBTEST": [{"ID": 1}]},
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(config))):
        pool._load_database_setup()

    assert pool.get_environment() == "TEST"
    assert pool.get_schema() == "TSTFAL"
    assert pool.get_test_data("TBTEST") == [{"ID": 1}]


def test_populate_test_data_is_blocked_outside_test_environment():
    pool, logger = _make_pool()
    pool._pool_initialized = True
    pool._environment = "PRODUCTION"

    result = pool.populate_test_data()

    assert result == {"status": "blocked", "reason": "Not in TEST environment"}
    logger.warning.assert_called_once()


def test_populate_test_data_handles_success_empty_and_error_rows():
    pool, _ = _make_pool()
    pool._pool_initialized = True
    pool._environment = "TEST"
    pool._schema = "TSTFAL"
    pool._test_data = {
        "TBGOOD": [{"A": 1, "B": "x"}],
        "TBEMPTY": [],
        "TBFAIL": [{"A": 99}],
    }

    cursor = MagicMock()

    def execute_side_effect(sql, params=None):
        if "INSERT INTO TSTFAL.TBFAIL" in sql:
            raise RuntimeError("insert failed")

    cursor.execute.side_effect = execute_side_effect

    with patch.object(pool, "get_cursor", return_value=_cursor_cm(cursor)):
        result = pool.populate_test_data()

    assert result["TBGOOD"]["status"] == "success"
    assert result["TBGOOD"]["inserted"] == 1
    assert result["TBEMPTY"]["status"] == "empty"
    assert result["TBFAIL"]["status"] == "error"
    assert "insert failed" in result["TBFAIL"]["error"]
