import pytest
from unittest.mock import patch, MagicMock

from main.utilities.error_handler import ResponseCode

@pytest.fixture
def mock_logger():
    """Patch LoggerFactory so tests don't write to disk."""
    dummy = MagicMock()
    with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
        yield dummy


# --- HTTP status code mapping ---

def test_success_code(mock_logger):
    rc = ResponseCode("SUCCESS")
    assert rc.get_error_code() == 200
    assert rc.get_success() is True


def test_bad_request_code(mock_logger):
    rc = ResponseCode("BAD_REQUEST")
    assert rc.get_error_code() == 400
    assert rc.get_success() is False


def test_unauthorized_code(mock_logger):
    rc = ResponseCode("UNAUTHORIZED")
    assert rc.get_error_code() == 401
    assert rc.get_success() is False


def test_forbidden_code(mock_logger):
    rc = ResponseCode("FORBIDDEN")
    assert rc.get_error_code() == 403
    assert rc.get_success() is False


def test_not_found_code(mock_logger):
    rc = ResponseCode("NOT_FOUND")
    assert rc.get_error_code() == 404
    assert rc.get_success() is False


def test_method_not_allowed_code(mock_logger):
    rc = ResponseCode("METHOD_NOT_ALLOWED")
    assert rc.get_error_code() == 405


def test_conflict_code(mock_logger):
    rc = ResponseCode("CONFLICT")
    assert rc.get_error_code() == 409


def test_internal_server_error_code(mock_logger):
    rc = ResponseCode("INTERNAL_SERVER_ERROR")
    assert rc.get_error_code() == 500
    assert rc.get_success() is False


def test_unknown_tag_defaults_to_500(mock_logger):
    rc = ResponseCode("TOTALLY_UNKNOWN")
    assert rc.get_error_code() == 500
    assert rc.get_success() is False


# --- Getters ---

def test_get_error_tag(mock_logger):
    rc = ResponseCode("NOT_FOUND")
    assert rc.get_error_tag() == "NOT_FOUND"


def test_get_message_contains_meaningful_text(mock_logger):
    rc = ResponseCode("NOT_FOUND")
    assert len(rc.get_message()) > 0


def test_get_data_none_by_default(mock_logger):
    rc = ResponseCode("SUCCESS")
    assert rc.get_data() is None


def test_get_data_returns_provided_value(mock_logger):
    rc = ResponseCode("SUCCESS", data={"id": 42})
    assert rc.get_data() == {"id": 42}


# --- to_http_response ---

def test_to_http_response_returns_correct_code(mock_logger):
    rc = ResponseCode("SUCCESS")
    code, _ = rc.to_http_response()
    assert code == 200


def test_to_http_response_success_status_field(mock_logger):
    rc = ResponseCode("SUCCESS")
    _, body = rc.to_http_response()
    assert body["status"] == "success"


def test_to_http_response_error_status_field(mock_logger):
    rc = ResponseCode("NOT_FOUND")
    _, body = rc.to_http_response()
    assert body["status"] == "error"


def test_to_http_response_contains_code_tag(mock_logger):
    rc = ResponseCode("BAD_REQUEST")
    _, body = rc.to_http_response()
    assert body["code_tag"] == "BAD_REQUEST"


def test_to_http_response_contains_message(mock_logger):
    rc = ResponseCode("SUCCESS")
    _, body = rc.to_http_response()
    assert "message" in body


def test_to_http_response_omits_data_key_when_none(mock_logger):
    rc = ResponseCode("SUCCESS")
    _, body = rc.to_http_response()
    assert "data" not in body


def test_to_http_response_includes_data_when_provided(mock_logger):
    rc = ResponseCode("SUCCESS", data=[1, 2, 3])
    _, body = rc.to_http_response()
    assert body["data"] == [1, 2, 3]


# --- Logging behaviour ---

def test_error_response_calls_logger_error():
    dummy = MagicMock()
    with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
        ResponseCode("BAD_REQUEST")
    dummy.error.assert_called_once()


def test_success_response_calls_logger_info():
    dummy = MagicMock()
    with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
        ResponseCode("SUCCESS")
    dummy.info.assert_called_once()


# --- Property accessors ---

def test_property_success_true_for_success_code(mock_logger):
    rc = ResponseCode("SUCCESS")
    assert rc.success is True


def test_property_success_false_for_error_code(mock_logger):
    rc = ResponseCode("NOT_FOUND")
    assert rc.success is False


def test_property_error_code_matches_getter(mock_logger):
    rc = ResponseCode("BAD_REQUEST")
    assert rc.error_code == rc.get_error_code()


def test_property_error_tag_matches_getter(mock_logger):
    rc = ResponseCode("FORBIDDEN")
    assert rc.error_tag == rc.get_error_tag()


def test_property_message_matches_getter(mock_logger):
    rc = ResponseCode("NOT_FOUND")
    assert rc.message == rc.get_message()


def test_property_data_matches_getter(mock_logger):
    rc = ResponseCode("SUCCESS", data={"x": 1})
    assert rc.data == rc.get_data()
    assert rc.data == {"x": 1}
