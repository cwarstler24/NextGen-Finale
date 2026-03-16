"""
Tests for AbstractDAO shared behavior and db2_safe decorator.

All database interactions are mocked through get_db_cursor.
"""

from unittest.mock import MagicMock, patch

import pytest

from main.backend.AbstractDAO import DatabaseAccessObject, db2_safe
from main.utilities.error_handler import ResponseCode


class DummyDAO(DatabaseAccessObject):
    """Concrete DAO for testing AbstractDAO behavior."""

    def __init__(self):
        super().__init__(table_name="TBTEST", primary_key="ID")

    def _prepare_entry(self, entry):
        enriched = dict(entry)
        enriched.setdefault("DEFAULTED", "YES")
        return enriched

    def _row_to_dict(self, row):
        return {"ID": row[0], "NAME": row[1]}

    def _build_insert_sql(self, entry):
        return "INSERT INTO TBTEST (ID, NAME, DEFAULTED) VALUES (?, ?, ?)", [
            entry.get("ID"),
            entry.get("NAME"),
            entry.get("DEFAULTED"),
        ]

    def _build_update_sql(self, updates):
        fields = list(updates.keys())
        clause = ", ".join([f"{field} = ?" for field in fields])
        values = [updates[field] for field in fields]
        return clause, values


def _cursor_cm(cursor):
    ctx = MagicMock()
    ctx.__enter__.return_value = cursor
    ctx.__exit__.return_value = False
    return ctx


@pytest.fixture
def dao():
    return DummyDAO()


class TestDb2SafeDecorator:
    def test_wraps_non_response_success(self):
        @db2_safe
        def do_work():
            return {"ok": True}

        result = do_work()
        assert isinstance(result, ResponseCode)
        assert result.success is True
        assert result.data == {"ok": True}

    def test_does_not_double_wrap_response_code(self):
        rc = ResponseCode("SUCCESS", {"x": 1})

        @db2_safe
        def do_work():
            return rc

        result = do_work()
        assert result is rc

    def test_parses_sqlstate_and_sqlcode_from_exception(self):
        @db2_safe
        def do_work():
            raise Exception("DB blew up SQLSTATE=23505 SQLCODE=-803")

        result = do_work()
        assert result.success is False
        assert result.error_code == 409
        assert "SQLSTATE=23505" in result.error_tag
        assert "SQLCODE=-803" in result.error_tag

    def test_returns_generic_error_when_no_db2_codes(self):
        @db2_safe
        def do_work():
            raise ValueError("plain error")

        result = do_work()
        assert result.success is False
        assert result.error_tag == "ValueError"
        assert "plain error" in result.data


class TestGetByKey:
    def test_returns_record_when_found(self, dao):
        cursor = MagicMock()
        cursor.fetchone.return_value = (1, "Alice")

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_by_key(1)

        assert result.success is True
        assert result.data == {"ID": 1, "NAME": "Alice"}
        cursor.execute.assert_called_once_with("SELECT * FROM TBTEST WHERE ID = ?", (1,))

    def test_returns_not_found_when_missing(self, dao):
        cursor = MagicMock()
        cursor.fetchone.return_value = None

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_by_key(999)

        assert result.success is False
        assert result.error_tag == "NOT_FOUND"


class TestGetByFields:
    def test_bad_request_when_filters_empty(self, dao):
        result = dao.get_by_fields({})
        assert result.success is False
        assert result.error_tag == "BAD_REQUEST"

    def test_builds_where_clause_and_returns_records(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_by_fields({"NAME": "Alice", "ACTIVE": 1})

        assert result.success is True
        assert result.data == [{"ID": 1, "NAME": "Alice"}, {"ID": 2, "NAME": "Bob"}]
        cursor.execute.assert_called_once_with(
            "SELECT * FROM TBTEST WHERE NAME = ? AND ACTIVE = ?", ["Alice", 1]
        )


class TestGetAllRecords:
    def test_returns_not_found_for_empty_table(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = []

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_all_records()

        assert result.success is False
        assert result.error_tag == "NOT_FOUND"

    def test_returns_all_records_without_limit(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(1, "A")]

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_all_records()

        assert result.success is True
        assert result.data == [{"ID": 1, "NAME": "A"}]
        cursor.execute.assert_called_once_with("SELECT * FROM TBTEST")

    def test_applies_limit_clause(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(1, "A")]

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_all_records(limit=1)

        assert result.success is True
        cursor.execute.assert_called_once_with("SELECT * FROM TBTEST FETCH FIRST 1 ROWS ONLY")


class TestGetRandom:
    def test_get_random_without_filters(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(1, "A")]

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_random(num_returned=1)

        assert result.success is True
        cursor.execute.assert_called_once_with(
            "SELECT * FROM TBTEST ORDER BY RAND() FETCH FIRST 1 ROWS ONLY"
        )

    def test_get_random_with_filters(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(2, "B")]

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_random(num_returned=2, filters={"ACTIVE": 1})

        assert result.success is True
        cursor.execute.assert_called_once_with(
            "SELECT * FROM TBTEST WHERE ACTIVE = ? ORDER BY RAND() FETCH FIRST 2 ROWS ONLY",
            [1],
        )

    def test_warns_when_less_rows_than_requested(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(2, "B")]

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.get_random(num_returned=2)

        assert result.success is True


class TestUpdateRecord:
    def test_bad_request_when_updates_empty(self, dao):
        result = dao.update_record(1, {})
        assert result.success is False
        assert result.error_tag == "BAD_REQUEST"

    def test_not_found_when_rowcount_zero(self, dao):
        cursor = MagicMock()
        cursor.rowcount = 0

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.update_record(1, {"NAME": "New"})

        assert result.success is False
        assert result.error_tag == "NOT_FOUND"

    def test_returns_key_when_update_succeeds(self, dao):
        cursor = MagicMock()
        cursor.rowcount = 1

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.update_record(7, {"NAME": "Updated"})

        assert result.success is True
        assert result.data == 7
        cursor.execute.assert_called_once_with(
            "UPDATE TBTEST SET NAME = ? WHERE ID = ?", ["Updated", 7]
        )


class TestCreateRecord:
    def test_uses_prepare_entry_and_returns_primary_key(self, dao):
        cursor = MagicMock()

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.create_record({"ID": 55, "NAME": "Created"})

        assert result.success is True
        assert result.data == 55
        cursor.execute.assert_called_once_with(
            "INSERT INTO TBTEST (ID, NAME, DEFAULTED) VALUES (?, ?, ?)",
            [55, "Created", "YES"],
        )

    def test_returns_unknown_when_pk_missing(self, dao):
        cursor = MagicMock()

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.create_record({"NAME": "NoPk"})

        assert result.success is True
        assert result.data == "unknown"


class TestDeleteRecord:
    def test_not_found_when_rowcount_zero(self, dao):
        cursor = MagicMock()
        cursor.rowcount = 0

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.delete_record(3)

        assert result.success is False
        assert result.error_tag == "NOT_FOUND"

    def test_returns_deleted_count(self, dao):
        cursor = MagicMock()
        cursor.rowcount = 2

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.delete_record(3)

        assert result.success is True
        assert result.data == {"deleted_count": 2}
        cursor.execute.assert_called_once_with("DELETE FROM TBTEST WHERE ID = ?", (3,))


class TestDeleteRecordByField:
    def test_bad_request_when_filter_empty(self, dao):
        result = dao.delete_record_by_field({})
        assert result.success is False
        assert result.error_tag == "BAD_REQUEST"

    def test_bad_request_when_multiple_fields(self, dao):
        result = dao.delete_record_by_field({"A": 1, "B": 2})
        assert result.success is False
        assert result.error_tag == "BAD_REQUEST"

    def test_deletes_by_single_field(self, dao):
        cursor = MagicMock()
        cursor.rowcount = 4

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.delete_record_by_field({"STATUS": "ARCHIVED"})

        assert result.success is True
        assert result.data == {"deleted_count": 4}
        cursor.execute.assert_called_once_with(
            "DELETE FROM TBTEST WHERE STATUS = ?", ("ARCHIVED",)
        )


class TestExecuteJoinQuery:
    def test_executes_join_query_and_returns_dict_rows(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(1, "Alice")]
        cursor.description = [("ID",), ("NAME",)]

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.execute_join_query(
                select_clause="t.ID, t.NAME",
                join_clauses=["INNER JOIN TBOther o ON t.ID = o.TEST_ID"],
                where_clause="o.FLAG = ?",
                parameters=[1],
                limit=5,
            )

        assert result.success is True
        assert result.data == [{"ID": 1, "NAME": "Alice"}]
        cursor.execute.assert_called_once_with(
            "SELECT t.ID, t.NAME FROM TBTEST t INNER JOIN TBOther o ON t.ID = o.TEST_ID WHERE o.FLAG = ? FETCH FIRST 5 ROWS ONLY",
            [1],
        )

    def test_returns_empty_success_when_no_rows(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = []

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.execute_join_query(
                select_clause="t.ID",
                join_clauses=[],
            )

        assert result.success is True
        assert result.data == []

    def test_fallback_alias_uses_first_letter_when_no_alias_in_select(self, dao):
        cursor = MagicMock()
        cursor.fetchall.return_value = []

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            dao.execute_join_query(select_clause="ID", join_clauses=[])

        cursor.execute.assert_called_once_with("SELECT ID FROM TBTEST t", [])

    def test_returns_database_error_on_exception(self, dao):
        cursor = MagicMock()
        cursor.execute.side_effect = RuntimeError("join failed")

        with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
            result = dao.execute_join_query(
                select_clause="t.ID",
                join_clauses=[],
            )

        assert result.success is False
        assert result.error_tag == "DATABASE_ERROR"
        assert "join failed" in result.data
