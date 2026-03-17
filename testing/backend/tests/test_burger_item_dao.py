from unittest.mock import MagicMock

import pytest

from main.backend.burgerItemDAO import BurgerItemDAO
from main.utilities.error_handler import ResponseCode


@pytest.fixture
def dao():
    return BurgerItemDAO()


class TestBurgerItemDAOQueryMethods:
    def test_get_burger_with_details_delegates_join_query(self, dao):
        expected = ResponseCode("SUCCESS", [{"BURGER_ID": 10}])
        execute_join_query = MagicMock(return_value=expected)
        dao.execute_join_query = execute_join_query

        result = dao.get_burger_with_details(10)

        assert result is expected
        execute_join_query.assert_called_once_with(
            select_clause="""
                b.BURGER_ID, b.ORDER_ITEM_ID,
                bt.BUN_ID, bt.BUN_NAME, bt.PRICE AS BUN_PRICE, bt.STOCK_QUANTITY AS BUN_STOCK,
                pt.PATTY_ID, pt.PATTY_NAME, pt.PRICE AS PATTY_PRICE, pt.STOCK_QUANTITY AS PATTY_STOCK
            """,
            join_clauses=[
                "INNER JOIN TBBUN_TYPES bt ON b.BUN_TYPE = bt.BUN_ID",
                "INNER JOIN TBPATTY_TYPES pt ON b.PATTY_TYPE = pt.PATTY_ID",
            ],
            where_clause="b.BURGER_ID = ?",
            parameters=[10],
        )

    def test_get_burger_toppings_delegates_join_query(self, dao):
        expected = ResponseCode("SUCCESS", [{"TOPPING_ID": 3}])
        execute_join_query = MagicMock(return_value=expected)
        dao.execute_join_query = execute_join_query

        result = dao.get_burger_toppings(22)

        assert result is expected
        execute_join_query.assert_called_once_with(
            select_clause="""
                b.BURGER_ID, t.TOPPING_ID, t.TOPPING_NAME, t.PRICE, t.STOCK_QUANTITY, bit.TOPPING_COUNT
            """,
            join_clauses=[
                "INNER JOIN TBBURGER_TOPPINGS bit ON b.BURGER_ID = bit.BURGER_ORDER_ID",
                "INNER JOIN TBTOPPINGS t ON bit.TOPPING_ID = t.TOPPING_ID",
            ],
            where_clause="b.BURGER_ID = ?",
            parameters=[22],
        )

    def test_get_burgers_by_order_item_delegates_join_query(self, dao):
        expected = ResponseCode("SUCCESS", [{"ORDER_ITEM_ID": 7}])
        execute_join_query = MagicMock(return_value=expected)
        dao.execute_join_query = execute_join_query

        result = dao.get_burgers_by_order_item(7)

        assert result is expected
        execute_join_query.assert_called_once_with(
            select_clause="""
                b.BURGER_ID, b.ORDER_ITEM_ID,
                bt.BUN_NAME, bt.PRICE AS BUN_PRICE,
                pt.PATTY_NAME, pt.PRICE AS PATTY_PRICE
            """,
            join_clauses=[
                "INNER JOIN TBBUN_TYPES bt ON b.BUN_TYPE = bt.BUN_ID",
                "INNER JOIN TBPATTY_TYPES pt ON b.PATTY_TYPE = pt.PATTY_ID",
            ],
            where_clause="b.ORDER_ITEM_ID = ?",
            parameters=[7],
        )


class TestBurgerItemDAOCompleteBurger:
    def test_returns_base_error_when_burger_lookup_fails(self, dao):
        base_error = ResponseCode(error_tag="DB_ERROR", data="failed")
        dao.get_burger_with_details = MagicMock(return_value=base_error)
        dao.get_burger_toppings = MagicMock()

        result = dao.get_burger_complete(9)

        assert result is base_error
        dao.get_burger_toppings.assert_not_called()

    def test_returns_not_found_when_base_data_empty(self, dao):
        dao.get_burger_with_details = MagicMock(return_value=ResponseCode("SUCCESS", []))
        dao.get_burger_toppings = MagicMock(return_value=ResponseCode("SUCCESS", [{"TOPPING_ID": 1}]))

        result = dao.get_burger_complete(9)

        assert result.success is False
        assert result.error_tag == "NOT_FOUND"
        assert result.data == "Burger 9 not found"

    def test_includes_toppings_when_toppings_call_succeeds(self, dao):
        burger_rows = [{"BURGER_ID": 9, "BUN_NAME": "Sesame", "PATTY_NAME": "Beef"}]
        topping_rows = [{"TOPPING_ID": 1, "TOPPING_NAME": "Lettuce"}]
        dao.get_burger_with_details = MagicMock(return_value=ResponseCode("SUCCESS", burger_rows))
        dao.get_burger_toppings = MagicMock(return_value=ResponseCode("SUCCESS", topping_rows))

        result = dao.get_burger_complete(9)

        assert result.success is True
        assert result.data["BURGER_ID"] == 9
        assert result.data["TOPPINGS"] == topping_rows

    def test_sets_empty_toppings_when_toppings_errors_or_missing(self, dao):
        burger_rows = [{"BURGER_ID": 11, "BUN_NAME": "Pretzel", "PATTY_NAME": "Vegan"}]
        dao.get_burger_with_details = MagicMock(return_value=ResponseCode("SUCCESS", burger_rows))
        dao.get_burger_toppings = MagicMock(return_value=ResponseCode(error_tag="DB_ERROR", data="oops"))

        result = dao.get_burger_complete(11)

        assert result.success is True
        assert result.data["BURGER_ID"] == 11
        assert result.data["TOPPINGS"] == []
