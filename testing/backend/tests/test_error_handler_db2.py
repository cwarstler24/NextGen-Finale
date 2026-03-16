import pytest
from unittest.mock import patch, MagicMock

from main.utilities.error_handler import ResponseCode, get_db2_error_response


# ==================== get_db2_error_response ====================

class TestGetDb2ErrorResponse:
    def test_exact_sqlstate_match(self):
        code, msg = get_db2_error_response(sqlstate="23505")
        assert code == 409
        assert "unique" in msg.lower() or "duplicate" in msg.lower()

    def test_wildcard_sqlstate_class_match(self):
        # "01xxx" is the only wildcard entry in the map; "01999" should hit it
        code, msg = get_db2_error_response(sqlstate="01999")
        assert code == 200

    def test_sqlcode_match(self):
        code, msg = get_db2_error_response(sqlcode=-803)
        assert code == 409

    def test_unknown_returns_500(self):
        code, msg = get_db2_error_response(sqlstate="99ZZZ")
        assert code == 500

    def test_no_args_returns_500_with_default_message(self):
        code, msg = get_db2_error_response()
        assert code == 500

    def test_custom_default_message_used_when_no_match(self):
        code, msg = get_db2_error_response(
            sqlstate="ZZZZZ", default_message="custom msg"
        )
        assert msg == "custom msg"

    def test_02000_maps_to_404(self):
        code, _ = get_db2_error_response(sqlstate="02000")
        assert code == 404

    def test_sqlcode_string_key_match(self):
        # -1 maps to 500
        code, _ = get_db2_error_response(sqlcode=-1)
        assert code == 500


# ==================== ResponseCode with DB2 args ====================

class TestResponseCodeDb2:
    def test_sqlstate_sets_tag(self):
        dummy = MagicMock()
        with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
            rc = ResponseCode(sqlstate="23505")
        assert "SQLSTATE=23505" in rc.get_error_tag()

    def test_sqlcode_sets_tag(self):
        dummy = MagicMock()
        with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
            rc = ResponseCode(sqlcode=-803)
        assert "SQLCODE=-803" in rc.get_error_tag()

    def test_sqlstate_and_sqlcode_both_appear_in_tag(self):
        dummy = MagicMock()
        with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
            rc = ResponseCode(sqlstate="23505", sqlcode=-803)
        tag = rc.get_error_tag()
        assert "SQLSTATE=23505" in tag
        assert "SQLCODE=-803" in tag

    def test_db2_error_is_not_success(self):
        dummy = MagicMock()
        with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
            rc = ResponseCode(sqlstate="23505")
        assert rc.get_success() is False

    def test_base_error_tag_preserved_when_provided(self):
        dummy = MagicMock()
        with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
            rc = ResponseCode(error_tag="WRITE_FAIL", sqlstate="23505")
        assert "WRITE_FAIL" in rc.get_error_tag()

    def test_tag_prefixed_db2error_when_no_base_tag(self):
        dummy = MagicMock()
        with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
            rc = ResponseCode(sqlstate="23505")
        assert rc.get_error_tag().startswith("DB2Error")

    def test_db2_error_code_returned_correctly(self):
        dummy = MagicMock()
        with patch("main.utilities.error_handler.LoggerFactory.get_general_logger", return_value=dummy):
            rc = ResponseCode(sqlstate="23505")
        assert rc.get_error_code() == 409
