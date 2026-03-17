from unittest.mock import MagicMock, patch

from main.backend.AbstractDAO import DatabaseAccessObject


class DummyDAO(DatabaseAccessObject):
    def __init__(self):
        super().__init__(table_name="TBTEST", primary_key="ID")

    def _row_to_dict(self, row):
        return {"ID": row[0]}

    def _build_insert_sql(self, entry):
        return "INSERT INTO TBTEST (ID) VALUES (?)", [entry.get("ID")]

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


def test_get_max_id_returns_zero_when_table_empty():
    dao = DummyDAO()
    cursor = MagicMock()
    cursor.fetchone.return_value = (None,)

    with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
        result = dao.get_max_id()

    assert result.success is True
    assert result.data == 0


def test_get_max_id_returns_value_when_present():
    dao = DummyDAO()
    cursor = MagicMock()
    cursor.fetchone.return_value = (42,)

    with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
        result = dao.get_max_id()

    assert result.success is True
    assert result.data == 42


def test_update_field_by_delta_returns_not_found_when_rowcount_zero():
    dao = DummyDAO()
    cursor = MagicMock()
    cursor.rowcount = 0

    with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
        result = dao.update_field_by_delta(7, "STOCK_QUANTITY", -1)

    assert result.success is False
    assert result.error_tag == "NOT_FOUND"


def test_update_field_by_delta_returns_updated_count_when_successful():
    dao = DummyDAO()
    cursor = MagicMock()
    cursor.rowcount = 1

    with patch("main.backend.AbstractDAO.get_db_cursor", return_value=_cursor_cm(cursor)):
        result = dao.update_field_by_delta(7, "STOCK_QUANTITY", -1)

    assert result.success is True
    assert result.data == {"updated_count": 1}
    cursor.execute.assert_called_once_with(
        "UPDATE TBTEST SET STOCK_QUANTITY = STOCK_QUANTITY + ? WHERE ID = ?",
        (-1, 7),
    )
