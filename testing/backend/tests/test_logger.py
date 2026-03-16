import logging
import os
import pytest
from unittest.mock import patch

from main.utilities.logger import LoggerFactory, _SmartLogger, ALLOWED_LOG_DIR


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch):
    """Reset the LoggerFactory singleton state before each test so tests are independent."""
    monkeypatch.setattr(LoggerFactory, "_initialized", False)
    monkeypatch.setattr(LoggerFactory, "_general_logger", None)
    monkeypatch.setattr(LoggerFactory, "_security_logger", None)
    yield


def test_initialize_sets_initialized_flag():
    LoggerFactory.initialize()
    assert LoggerFactory._initialized is True


def test_initialize_is_idempotent():
    LoggerFactory.initialize()
    LoggerFactory.initialize()
    assert LoggerFactory._initialized is True


def test_get_general_logger_returns_smart_logger():
    logger = LoggerFactory.get_general_logger()
    assert isinstance(logger, _SmartLogger)


def test_get_security_logger_returns_smart_logger():
    logger = LoggerFactory.get_security_logger()
    assert isinstance(logger, _SmartLogger)


def test_get_general_logger_is_singleton():
    first = LoggerFactory.get_general_logger()
    second = LoggerFactory.get_general_logger()
    assert first is second


def test_get_security_logger_is_singleton():
    first = LoggerFactory.get_security_logger()
    second = LoggerFactory.get_security_logger()
    assert first is second


def test_safe_path_within_allowed_dir():
    safe = os.path.join(ALLOWED_LOG_DIR, "output.log")
    assert LoggerFactory._is_safe_log_path(safe) is True


def test_unsafe_path_outside_allowed_dir():
    assert LoggerFactory._is_safe_log_path("/tmp/evil.log") is False


def test_path_traversal_is_blocked():
    traversal = os.path.join(ALLOWED_LOG_DIR, "..", "..", "evil.log")
    assert LoggerFactory._is_safe_log_path(traversal) is False


# --- _SmartLogger method dispatch ---

def test_smart_logger_debug_dispatches_when_enabled():
    LoggerFactory.initialize()
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "debug") as m, \
         patch.object(logger._logger, "isEnabledFor", return_value=True):
        logger.debug("test")
    m.assert_called_once()


def test_smart_logger_debug_skips_when_disabled():
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "debug") as m, \
         patch.object(logger._logger, "isEnabledFor", return_value=False):
        logger.debug("test")
    m.assert_not_called()


def test_smart_logger_info_dispatches_when_enabled():
    LoggerFactory.initialize()
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "info") as m, \
         patch.object(logger._logger, "isEnabledFor", return_value=True):
        logger.info("test")
    m.assert_called_once()


def test_smart_logger_warning_dispatches_when_enabled():
    LoggerFactory.initialize()
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "warning") as m, \
         patch.object(logger._logger, "isEnabledFor", return_value=True):
        logger.warning("test")
    m.assert_called_once()


def test_smart_logger_error_dispatches_when_enabled():
    LoggerFactory.initialize()
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "error") as m, \
         patch.object(logger._logger, "isEnabledFor", return_value=True):
        logger.error("test")
    m.assert_called_once()


def test_smart_logger_critical_always_dispatches():
    LoggerFactory.initialize()
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "critical") as m:
        logger.critical("test")
    m.assert_called_once()


def test_smart_logger_exception_always_dispatches():
    LoggerFactory.initialize()
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "exception") as m:
        logger.exception("test")
    m.assert_called_once()


# --- also_print=True branches ---

def test_debug_also_prints_to_stdout(capsys):
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "isEnabledFor", return_value=False):
        logger.debug("debug-msg", also_print=True)
    assert "debug-msg" in capsys.readouterr().out


def test_info_also_prints_to_stdout(capsys):
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "isEnabledFor", return_value=False):
        logger.info("info-msg", also_print=True)
    assert "info-msg" in capsys.readouterr().out


def test_warning_also_prints_to_stdout(capsys):
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "isEnabledFor", return_value=False):
        logger.warning("warning-msg", also_print=True)
    assert "warning-msg" in capsys.readouterr().out


def test_error_also_prints_to_stdout(capsys):
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "isEnabledFor", return_value=False):
        logger.error("error-msg", also_print=True)
    assert "error-msg" in capsys.readouterr().out


def test_critical_also_prints_to_stdout(capsys):
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "critical"):
        logger.critical("critical-msg", also_print=True)
    assert "critical-msg" in capsys.readouterr().out


def test_exception_also_prints_to_stdout(capsys):
    logger = _SmartLogger("generalLogger")
    with patch.object(logger._logger, "exception"):
        logger.exception("exception-msg", also_print=True)
    assert "exception-msg" in capsys.readouterr().out


# --- Non-SmartLogger fallback branch ---

def test_get_general_logger_returns_standard_logger_when_smart_disabled(monkeypatch):
    monkeypatch.setattr(LoggerFactory, "_initialized", True)
    monkeypatch.setattr(LoggerFactory, "_use_smart_logger", False)
    logger = LoggerFactory.get_general_logger()
    assert not isinstance(logger, _SmartLogger)
    assert isinstance(logger, logging.Logger)


def test_get_security_logger_returns_standard_logger_when_smart_disabled(monkeypatch):
    monkeypatch.setattr(LoggerFactory, "_initialized", True)
    monkeypatch.setattr(LoggerFactory, "_use_smart_logger", False)
    logger = LoggerFactory.get_security_logger()
    assert not isinstance(logger, _SmartLogger)
    assert isinstance(logger, logging.Logger)


# --- Unsafe log path in initialize() ---

def test_initialize_raises_on_unsafe_log_path():
    fake_config = {
        "use_smart_logger": True,
        "handlers": {"evil": {"filename": "{LOG_DIR}/hacked.log"}},
    }
    with patch("main.utilities.logger.yaml.safe_load", return_value=fake_config), \
         patch.object(LoggerFactory, "_is_safe_log_path", return_value=False):
        with pytest.raises(ValueError, match="Unsafe log path detected"):
            LoggerFactory.initialize()

def test_initialize_creates_missing_log_files(tmp_path):
    """Covers the file-creation branch when log files don't yet exist."""
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "logging_config.yaml").write_text(
        "use_smart_logger: true\nhandlers: {}\n"
    )
    fake_file = str(tmp_path / "utilities" / "logger.py")
    with patch("main.utilities.logger.__file__", fake_file), \
         patch("main.utilities.logger.logging.config.dictConfig"):
        LoggerFactory.initialize()
    assert (tmp_path / "logs" / "general.log").exists()
    assert (tmp_path / "logs" / "security.log").exists()