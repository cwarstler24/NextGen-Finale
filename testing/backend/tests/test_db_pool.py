"""
Tests for DB2ConnectionPool in db_pool.py.

All IBM DB2 driver calls and file I/O are mocked — no real DB connection is needed.
"""
import json
from queue import Empty
from unittest.mock import patch, MagicMock, mock_open
import pytest

from main.backend.db_pool import DB2ConnectionPool, get_db_cursor


SAMPLE_CREDENTIALS = {
    "database": "TESTDB",
    "hostname": "localhost",
    "port": 5000,
    "protocol": "TCPIP",
    "authentication": "SERVER",
    "uid": "testuser",
    "pwd": "testpass",
}

CREDENTIALS_JSON = json.dumps(SAMPLE_CREDENTIALS)


# ==================== Fixtures ====================

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton before and after every test so each test gets a clean pool."""
    DB2ConnectionPool._instance = None
    yield
    DB2ConnectionPool._instance = None


def _make_pool():
    """Create a fresh pool with a mocked logger. Returns (pool, logger_mock)."""
    dummy = MagicMock()
    with patch("main.backend.db_pool.LoggerFactory.get_general_logger", return_value=dummy):
        p = DB2ConnectionPool()
    return p, dummy


# ==================== Singleton ====================

class TestSingleton:
    def test_returns_same_instance_on_repeated_calls(self):
        pool1, _ = _make_pool()
        pool2 = DB2ConnectionPool()
        assert pool1 is pool2

    def test_pool_initialized_false_by_default(self):
        pool, _ = _make_pool()
        assert pool._pool_initialized is False

    def test_initial_current_size_is_zero(self):
        pool, _ = _make_pool()
        assert pool._current_size == 0

    def test_pool_queue_is_empty_initially(self):
        pool, _ = _make_pool()
        assert pool._pool.empty()

    def test_all_connections_is_empty_initially(self):
        pool, _ = _make_pool()
        assert pool._all_connections == []


# ==================== _load_credentials ====================

class TestLoadCredentials:
    def test_builds_connection_string_from_json(self):
        pool, _ = _make_pool()
        with patch("builtins.open", mock_open(read_data=CREDENTIALS_JSON)):
            pool._load_credentials()
        assert "DATABASE=TESTDB" in pool._conn_str
        assert "HOSTNAME=localhost" in pool._conn_str
        assert "PORT=5000" in pool._conn_str
        assert "UID=testuser" in pool._conn_str
        assert "PWD=testpass" in pool._conn_str

    def test_connection_string_includes_schema(self):
        pool, _ = _make_pool()
        with patch("builtins.open", mock_open(read_data=CREDENTIALS_JSON)):
            pool._load_credentials()
        assert "CURRENTSCHEMA=SKYFAL" in pool._conn_str

    def test_connection_string_includes_protocol_and_auth(self):
        pool, _ = _make_pool()
        with patch("builtins.open", mock_open(read_data=CREDENTIALS_JSON)):
            pool._load_credentials()
        assert "PROTOCOL=TCPIP" in pool._conn_str
        assert "AUTHENTICATION=SERVER" in pool._conn_str

    def test_raises_on_missing_credentials_file(self):
        pool, _ = _make_pool()
        with patch("builtins.open", side_effect=FileNotFoundError("no file")):
            with pytest.raises(FileNotFoundError):
                pool._load_credentials()

    def test_raises_on_invalid_json(self):
        pool, _ = _make_pool()
        with patch("builtins.open", mock_open(read_data="not-valid-json{")):
            with pytest.raises(json.JSONDecodeError):
                pool._load_credentials()

    def test_logs_success(self):
        pool, dummy = _make_pool()
        with patch("builtins.open", mock_open(read_data=CREDENTIALS_JSON)):
            pool._load_credentials()
        dummy.info.assert_called()


# ==================== _create_connection ====================

class TestCreateConnection:
    def test_raises_when_ibm_db_is_none(self):
        pool, _ = _make_pool()
        with patch("main.backend.db_pool.ibm_db", None), \
             patch("main.backend.db_pool.ibm_db_dbi", None):
            with pytest.raises(RuntimeError, match="DB2 driver is not available"):
                pool._create_connection()

    def test_increments_current_size(self):
        pool, _ = _make_pool()
        fake_dbi_conn = MagicMock()
        with patch("main.backend.db_pool.ibm_db") as mock_ibm_db, \
             patch("main.backend.db_pool.ibm_db_dbi") as mock_ibm_db_dbi:
            mock_ibm_db.connect.return_value = MagicMock()
            mock_ibm_db_dbi.Connection.return_value = fake_dbi_conn
            pool._create_connection()
        assert pool._current_size == 1

    def test_appends_to_all_connections(self):
        pool, _ = _make_pool()
        fake_dbi_conn = MagicMock()
        with patch("main.backend.db_pool.ibm_db") as mock_ibm_db, \
             patch("main.backend.db_pool.ibm_db_dbi") as mock_ibm_db_dbi:
            mock_ibm_db.connect.return_value = MagicMock()
            mock_ibm_db_dbi.Connection.return_value = fake_dbi_conn
            pool._create_connection()
        assert fake_dbi_conn in pool._all_connections

    def test_returns_dbi_connection(self):
        pool, _ = _make_pool()
        fake_dbi_conn = MagicMock()
        with patch("main.backend.db_pool.ibm_db") as mock_ibm_db, \
             patch("main.backend.db_pool.ibm_db_dbi") as mock_ibm_db_dbi:
            mock_ibm_db.connect.return_value = MagicMock()
            mock_ibm_db_dbi.Connection.return_value = fake_dbi_conn
            result = pool._create_connection()
        assert result is fake_dbi_conn

    def test_re_raises_on_connect_failure(self):
        pool, _ = _make_pool()
        pool._conn_str = "fake"
        with patch("main.backend.db_pool.ibm_db") as mock_ibm_db, \
             patch("main.backend.db_pool.ibm_db_dbi"), \
             patch("main.backend.db_pool.ResponseCode"):
            mock_ibm_db.connect.side_effect = Exception("connection refused")
            with pytest.raises(Exception, match="connection refused"):
                pool._create_connection()

    def test_logs_error_on_failure(self):
        pool, dummy = _make_pool()
        pool._conn_str = "fake"
        with patch("main.backend.db_pool.ibm_db") as mock_ibm_db, \
             patch("main.backend.db_pool.ibm_db_dbi"), \
             patch("main.backend.db_pool.ResponseCode"):
            mock_ibm_db.connect.side_effect = Exception("boom")
            with pytest.raises(Exception):
                pool._create_connection()
        dummy.error.assert_called()

    def test_multiple_connections_accumulate_correctly(self):
        pool, _ = _make_pool()
        with patch("main.backend.db_pool.ibm_db") as mock_ibm_db, \
             patch("main.backend.db_pool.ibm_db_dbi") as mock_ibm_db_dbi:
            mock_ibm_db.connect.return_value = MagicMock()
            mock_ibm_db_dbi.Connection.side_effect = [MagicMock(), MagicMock()]
            pool._create_connection()
            pool._create_connection()
        assert pool._current_size == 2
        assert len(pool._all_connections) == 2


# ==================== _initialize_pool ====================

class TestInitializePool:
    def test_creates_min_connections(self):
        pool, _ = _make_pool()
        with patch.object(pool, "_create_connection", return_value=MagicMock()) as mock_create:
            pool._initialize_pool()
        assert mock_create.call_count == pool._min_connections

    def test_puts_connections_in_queue(self):
        pool, _ = _make_pool()
        with patch.object(pool, "_create_connection", return_value=MagicMock()):
            pool._initialize_pool()
        assert pool._pool.qsize() == pool._min_connections


# ==================== _ensure_pool_initialized ====================

class TestEnsurePoolInitialized:
    def test_calls_load_credentials_and_initialize_pool(self):
        pool, _ = _make_pool()
        with patch.object(pool, "_load_credentials") as mock_creds, \
             patch.object(pool, "_initialize_pool") as mock_init:
            pool._ensure_pool_initialized()
        mock_creds.assert_called_once()
        mock_init.assert_called_once()

    def test_sets_pool_initialized_to_true(self):
        pool, _ = _make_pool()
        with patch.object(pool, "_load_credentials"), \
             patch.object(pool, "_initialize_pool"):
            pool._ensure_pool_initialized()
        assert pool._pool_initialized is True

    def test_skips_when_already_initialized(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        with patch.object(pool, "_load_credentials") as mock_creds:
            pool._ensure_pool_initialized()
        mock_creds.assert_not_called()

    def test_idempotent_on_repeated_calls(self):
        pool, _ = _make_pool()
        call_count = 0

        def counting_load():
            nonlocal call_count
            call_count += 1

        with patch.object(pool, "_load_credentials", side_effect=counting_load), \
             patch.object(pool, "_initialize_pool"):
            pool._ensure_pool_initialized()
            pool._ensure_pool_initialized()
        assert call_count == 1


# ==================== get_connection ====================

class TestGetConnection:
    def _initialized_pool(self, queue_size=0):
        pool, dummy = _make_pool()
        pool._pool_initialized = True
        for _ in range(queue_size):
            conn = MagicMock()
            pool._pool.put(conn)
            pool._all_connections.append(conn)
            pool._current_size += 1
        return pool, dummy

    def test_returns_connection_from_queue(self):
        pool, _ = self._initialized_pool(queue_size=1)
        conn = pool.get_connection(timeout=1)
        assert conn is not None

    def test_pool_queue_shrinks_after_get(self):
        pool, _ = self._initialized_pool(queue_size=2)
        pool.get_connection(timeout=1)
        assert pool._pool.qsize() == 1

    def test_creates_new_connection_when_queue_empty_and_under_max(self):
        pool, _ = self._initialized_pool(queue_size=0)
        pool._current_size = 0
        pool._max_connections = 10
        new_conn = MagicMock()
        with patch.object(pool._pool, "get", side_effect=Empty), \
             patch.object(pool, "_create_connection", return_value=new_conn) as mock_create:
            result = pool.get_connection(timeout=0)
        mock_create.assert_called_once()
        assert result is new_conn

    def test_raises_runtime_error_when_pool_exhausted(self):
        pool, _ = self._initialized_pool(queue_size=0)
        pool._current_size = pool._max_connections
        with patch.object(pool._pool, "get", side_effect=Empty), \
             patch("main.backend.db_pool.ResponseCode"):
            with pytest.raises(RuntimeError, match="pool exhausted"):
                pool.get_connection(timeout=0)

    def test_exhaustion_message_includes_max_connections(self):
        pool, _ = self._initialized_pool(queue_size=0)
        pool._current_size = pool._max_connections
        with patch.object(pool._pool, "get", side_effect=Empty), \
             patch("main.backend.db_pool.ResponseCode"):
            with pytest.raises(RuntimeError, match=str(pool._max_connections)):
                pool.get_connection(timeout=0)


# ==================== return_connection ====================

class TestReturnConnection:
    def test_none_connection_is_a_noop(self):
        pool, _ = _make_pool()
        pool.return_connection(None)  # must not raise

    def test_puts_connection_back_in_queue(self):
        pool, _ = _make_pool()
        fake_conn = MagicMock()
        pool.return_connection(fake_conn)
        assert pool._pool.qsize() == 1

    def test_calls_rollback_before_returning(self):
        pool, _ = _make_pool()
        fake_conn = MagicMock()
        pool.return_connection(fake_conn)
        fake_conn.rollback.assert_called_once()

    def test_removes_connection_on_rollback_error(self):
        pool, _ = _make_pool()
        fake_conn = MagicMock()
        fake_conn.rollback.side_effect = Exception("rollback failed")
        with patch.object(pool, "_remove_connection") as mock_remove:
            pool.return_connection(fake_conn)
        mock_remove.assert_called_once_with(fake_conn)

    def test_logs_error_on_rollback_failure(self):
        pool, dummy = _make_pool()
        fake_conn = MagicMock()
        fake_conn.rollback.side_effect = Exception("boom")
        with patch.object(pool, "_remove_connection"):
            pool.return_connection(fake_conn)
        dummy.error.assert_called()

    def test_does_not_return_to_pool_on_rollback_error(self):
        pool, _ = _make_pool()
        fake_conn = MagicMock()
        fake_conn.rollback.side_effect = Exception("boom")
        with patch.object(pool, "_remove_connection"):
            pool.return_connection(fake_conn)
        assert pool._pool.empty()


# ==================== _remove_connection ====================

class TestRemoveConnection:
    def _pool_with_conn(self):
        pool, dummy = _make_pool()
        fake_conn = MagicMock()
        pool._all_connections.append(fake_conn)
        pool._current_size = 1
        return pool, dummy, fake_conn

    def test_decrements_current_size(self):
        pool, _, fake_conn = self._pool_with_conn()
        pool._remove_connection(fake_conn)
        assert pool._current_size == 0

    def test_removes_from_all_connections(self):
        pool, _, fake_conn = self._pool_with_conn()
        pool._remove_connection(fake_conn)
        assert fake_conn not in pool._all_connections

    def test_calls_close_on_connection(self):
        pool, _, fake_conn = self._pool_with_conn()
        pool._remove_connection(fake_conn)
        fake_conn.close.assert_called_once()

    def test_swallows_close_exception(self):
        pool, _, fake_conn = self._pool_with_conn()
        fake_conn.close.side_effect = Exception("close failed")
        pool._remove_connection(fake_conn)  # must not raise

    def test_noop_when_conn_not_in_all_connections(self):
        pool, _ = _make_pool()
        other_conn = MagicMock()
        pool._current_size = 1
        pool._remove_connection(other_conn)
        assert pool._current_size == 1  # unchanged


# ==================== get_cursor ====================

class TestGetCursor:
    def _ready_pool(self):
        pool, dummy = _make_pool()
        pool._pool_initialized = True
        return pool, dummy

    def test_yields_cursor(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_conn.cursor.return_value = fake_cursor
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection"):
            with pool.get_cursor() as cursor:
                assert cursor is fake_cursor

    def test_commits_on_success(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection"):
            with pool.get_cursor():
                pass
        fake_conn.commit.assert_called_once()

    def test_rolls_back_on_exception_in_body(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection"):
            with pytest.raises(ValueError):
                with pool.get_cursor():
                    raise ValueError("query error")
        fake_conn.rollback.assert_called_once()

    def test_reraises_exception_from_body(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection"):
            with pytest.raises(ValueError, match="query error"):
                with pool.get_cursor():
                    raise ValueError("query error")

    def test_closes_cursor_on_success(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_conn.cursor.return_value = fake_cursor
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection"):
            with pool.get_cursor():
                pass
        fake_cursor.close.assert_called_once()

    def test_closes_cursor_on_exception(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_conn.cursor.return_value = fake_cursor
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection"):
            with pytest.raises(RuntimeError):
                with pool.get_cursor():
                    raise RuntimeError("error")
        fake_cursor.close.assert_called_once()

    def test_returns_connection_to_pool_on_success(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection") as mock_return:
            with pool.get_cursor():
                pass
        mock_return.assert_called_once_with(fake_conn)

    def test_returns_connection_to_pool_on_exception(self):
        pool, _ = self._ready_pool()
        fake_conn = MagicMock()
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection") as mock_return:
            with pytest.raises(RuntimeError):
                with pool.get_cursor():
                    raise RuntimeError("error")
        mock_return.assert_called_once_with(fake_conn)

    def test_logs_error_on_exception(self):
        pool, dummy = self._ready_pool()
        fake_conn = MagicMock()
        with patch.object(pool, "get_connection", return_value=fake_conn), \
             patch.object(pool, "return_connection"):
            with pytest.raises(RuntimeError):
                with pool.get_cursor():
                    raise RuntimeError("error")
        dummy.error.assert_called()

    def test_propagates_get_connection_failure(self):
        pool, _ = self._ready_pool()
        with patch.object(pool, "get_connection", side_effect=RuntimeError("no conn")):
            with pytest.raises(RuntimeError, match="no conn"):
                with pool.get_cursor():
                    pass  # pragma: no cover


# ==================== close_all ====================

class TestCloseAll:
    def test_noop_when_not_initialized(self):
        pool, dummy = _make_pool()
        pool._pool_initialized = False
        pool.close_all()
        dummy.info.assert_not_called()

    def test_drains_pool_queue(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        for _ in range(3):
            pool._pool.put(MagicMock())
        pool.close_all()
        assert pool._pool.empty()

    def test_closes_queued_connections(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        conns = [MagicMock() for _ in range(2)]
        for c in conns:
            pool._pool.put(c)
        pool.close_all()
        for c in conns:
            c.close.assert_called()

    def test_closes_all_active_connections(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        conns = [MagicMock() for _ in range(2)]
        pool._all_connections.extend(conns)
        pool.close_all()
        for c in conns:
            c.close.assert_called()

    def test_sets_pool_initialized_to_false(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        pool.close_all()
        assert pool._pool_initialized is False

    def test_resets_current_size_to_zero(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        pool._current_size = 5
        pool.close_all()
        assert pool._current_size == 0

    def test_clears_all_connections_list(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        pool._all_connections.append(MagicMock())
        pool.close_all()
        assert pool._all_connections == []

    def test_swallows_close_exceptions_in_queue(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        bad_conn = MagicMock()
        bad_conn.close.side_effect = Exception("close failed")
        pool._pool.put(bad_conn)
        pool.close_all()  # must not raise

    def test_swallows_close_exceptions_in_all_connections(self):
        pool, _ = _make_pool()
        pool._pool_initialized = True
        bad_conn = MagicMock()
        bad_conn.close.side_effect = Exception("close failed")
        pool._all_connections.append(bad_conn)
        pool.close_all()  # must not raise

    def test_logs_open_and_close_messages(self):
        pool, dummy = _make_pool()
        pool._pool_initialized = True
        pool.close_all()
        assert dummy.info.call_count >= 2


# ==================== get_pool_status ====================

class TestGetPoolStatus:
    def test_returns_dict(self):
        pool, _ = _make_pool()
        assert isinstance(pool.get_pool_status(), dict)

    def test_contains_expected_keys(self):
        pool, _ = _make_pool()
        status = pool.get_pool_status()
        assert "pool_size" in status
        assert "total_connections" in status
        assert "max_connections" in status
        assert "min_connections" in status

    def test_pool_size_reflects_queue_depth(self):
        pool, _ = _make_pool()
        pool._pool.put(MagicMock())
        assert pool.get_pool_status()["pool_size"] == 1

    def test_total_connections_reflects_current_size(self):
        pool, _ = _make_pool()
        pool._current_size = 4
        assert pool.get_pool_status()["total_connections"] == 4

    def test_max_and_min_match_defaults(self):
        pool, _ = _make_pool()
        status = pool.get_pool_status()
        assert status["max_connections"] == pool._max_connections
        assert status["min_connections"] == pool._min_connections


# ==================== get_db_cursor (module-level function) ====================

class TestGetDbCursor:
    def test_delegates_to_pool_get_cursor(self):
        fake_cursor = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=fake_cursor)
        mock_ctx.__exit__ = MagicMock(return_value=False)

        import main.backend.db_pool as db_pool_module
        with patch.object(db_pool_module.db_pool, "get_cursor", return_value=mock_ctx):
            with get_db_cursor() as cursor:
                assert cursor is fake_cursor
