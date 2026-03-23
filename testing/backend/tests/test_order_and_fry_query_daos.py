from unittest.mock import MagicMock

from main.backend.fryItemDAO import FryItemDAO
from main.backend.orderDAO import OrderDAO
from main.backend.orderItemDAO import OrderItemDAO
from main.utilities.error_handler import ResponseCode


def test_order_dao_get_order_with_customer_delegates_join_query():
    dao = OrderDAO()
    expected = ResponseCode("SUCCESS", [{"ORDER_ID": 1}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_order_with_customer(1)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                o.ORDER_ID, o.EMAIL, o.PURCHASE_DATE, o.ORDER_QTY, o.TOTAL_PRICE,
                c.NAME AS CUSTOMER_NAME, c.BILL_ADDR, c.SHIP_ADDR
            """,
        join_clauses=["INNER JOIN TBCUSTOMER c ON o.EMAIL = c.EMAIL"],
        where_clause="o.ORDER_ID = ?",
        parameters=[1],
    )


def test_order_dao_get_orders_by_customer_passes_limit():
    dao = OrderDAO()
    expected = ResponseCode("SUCCESS", [{"ORDER_ID": 2}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_orders_by_customer("user@example.com", limit=5)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                o.ORDER_ID, o.EMAIL, o.PURCHASE_DATE, o.ORDER_QTY, o.TOTAL_PRICE,
                c.NAME AS CUSTOMER_NAME
            """,
        join_clauses=["INNER JOIN TBCUSTOMER c ON o.EMAIL = c.EMAIL"],
        where_clause="o.EMAIL = ?",
        parameters=["user@example.com"],
        limit=5,
    )


def test_order_dao_get_order_items_delegates_join_query():
    dao = OrderDAO()
    expected = ResponseCode("SUCCESS", [{"ORDER_ITEM_ID": 9}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_order_items(42)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, 
                oi.UNIT_PRICE,
            """,
        join_clauses=["INNER JOIN TBORDER_ITEMS oi ON o.ORDER_ID = oi.ORDER_ID"],
        where_clause="o.ORDER_ID = ?",
        parameters=[42],
    )


def test_order_item_dao_get_burger_items_delegates_join_query():
    dao = OrderItemDAO()
    expected = ResponseCode("SUCCESS", [{"ITEM_TYPE": "BURGER"}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_order_items_with_burgers(10)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, oi.UNIT_PRICE,
                b.BURGER_ID, b.PATTY_COUNT,
                bt.BUN_NAME, bt.PRICE AS BUN_PRICE,
                pt.PATTY_NAME, pt.PRICE AS PATTY_PRICE
            """,
        join_clauses=[
            "INNER JOIN TBBURGER_ITEMS b ON oi.ORDER_ITEM_ID = b.ORDER_ITEM_ID",
            "INNER JOIN TBBUN_TYPES bt ON b.BUN_TYPE = bt.BUN_ID",
            "INNER JOIN TBPATTY_TYPES pt ON b.PATTY_TYPE = pt.PATTY_ID",
        ],
        where_clause="oi.ORDER_ID = ? AND oi.ITEM_TYPE = 'BURGER'",
        parameters=[10],
    )


def test_order_item_dao_get_fry_items_delegates_join_query():
    dao = OrderItemDAO()
    expected = ResponseCode("SUCCESS", [{"ITEM_TYPE": "FRIES"}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_order_items_with_fries(10)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, oi.UNIT_PRICE,
                f.FRY_ID,
                ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE,
                fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE,
                fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE
            """,
        join_clauses=[
            "INNER JOIN TBFRY_ITEMS f ON oi.ORDER_ITEM_ID = f.ORDER_ITEM_ID",
            "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
            "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
            "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID",
        ],
        where_clause="oi.ORDER_ID = ? AND oi.ITEM_TYPE = 'FRIES'",
        parameters=[10],
    )


def test_order_item_dao_combines_both_item_types_when_successful():
    dao = OrderItemDAO()
    dao.get_order_items_with_burgers = MagicMock(return_value=ResponseCode("SUCCESS", [{"ID": 1}]))
    dao.get_order_items_with_fries = MagicMock(return_value=ResponseCode("SUCCESS", [{"ID": 2}]))

    result = dao.get_all_order_items_with_details(11)

    assert result.success is True
    assert result.data == {"burgers": [{"ID": 1}], "fries": [{"ID": 2}]}


def test_order_item_dao_combines_with_empty_lists_on_partial_failures():
    dao = OrderItemDAO()
    dao.get_order_items_with_burgers = MagicMock(return_value=ResponseCode(error_tag="DB_ERROR", data="x"))
    dao.get_order_items_with_fries = MagicMock(return_value=ResponseCode("SUCCESS", [{"ID": 2}]))

    result = dao.get_all_order_items_with_details(11)

    assert result.success is True
    assert result.data == {"burgers": [], "fries": [{"ID": 2}]}


def test_order_item_dao_get_burgers_for_orders_returns_empty_on_empty_input():
    dao = OrderItemDAO()
    dao.execute_join_query = MagicMock()

    result = dao.get_burgers_for_orders([])

    assert result.success is True
    assert result.data == []
    dao.execute_join_query.assert_not_called()


def test_order_item_dao_get_fries_for_orders_returns_empty_on_empty_input():
    dao = OrderItemDAO()
    dao.execute_join_query = MagicMock()

    result = dao.get_fries_for_orders([])

    assert result.success is True
    assert result.data == []
    dao.execute_join_query.assert_not_called()


def test_order_item_dao_get_burgers_for_orders_delegates_join_query():
    dao = OrderItemDAO()
    expected = ResponseCode("SUCCESS", [{"ORDER_ID": 10, "ITEM_TYPE": "BURGER"}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_burgers_for_orders([10, 11])

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, oi.UNIT_PRICE,
                b.BURGER_ID, b.PATTY_COUNT,
                bt.BUN_NAME, bt.PRICE AS BUN_PRICE,
                pt.PATTY_NAME, pt.PRICE AS PATTY_PRICE
            """,
        join_clauses=[
            "INNER JOIN TBBURGER_ITEMS b ON oi.ORDER_ITEM_ID = b.ORDER_ITEM_ID",
            "INNER JOIN TBBUN_TYPES bt ON b.BUN_TYPE = bt.BUN_ID",
            "INNER JOIN TBPATTY_TYPES pt ON b.PATTY_TYPE = pt.PATTY_ID",
        ],
        where_clause="oi.ORDER_ID IN (?, ?) AND oi.ITEM_TYPE = 'BURGER'",
        parameters=[10, 11],
    )


def test_order_item_dao_get_fries_for_orders_delegates_join_query():
    dao = OrderItemDAO()
    expected = ResponseCode("SUCCESS", [{"ORDER_ID": 10, "ITEM_TYPE": "FRIES"}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_fries_for_orders([10, 11])

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, oi.UNIT_PRICE,
                f.FRY_ID,
                ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE,
                fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE,
                fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE
            """,
        join_clauses=[
            "INNER JOIN TBFRY_ITEMS f ON oi.ORDER_ITEM_ID = f.ORDER_ITEM_ID",
            "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
            "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
            "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID",
        ],
        where_clause="oi.ORDER_ID IN (?, ?) AND oi.ITEM_TYPE = 'FRIES'",
        parameters=[10, 11],
    )


def test_fry_item_dao_get_fry_with_details_delegates_join_query():
    dao = FryItemDAO()
    expected = ResponseCode("SUCCESS", [{"FRY_ID": 1}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_fry_with_details(1)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                f.FRY_ID, f.ORDER_ITEM_ID,
                ft.FRY_TYPE_ID, ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE, ft.STOCK_QUANTITY AS TYPE_STOCK,
                fs.FRY_SIZE_ID, fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE, fs.STOCK_QUANTITY AS SIZE_STOCK,
                fse.FRY_SEASONING_ID, fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE, fse.STOCK_QUANTITY AS SEASONING_STOCK
            """,
        join_clauses=[
            "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
            "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
            "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID",
        ],
        where_clause="f.FRY_ID = ?",
        parameters=[1],
    )


def test_fry_item_dao_get_all_fries_with_details_passes_limit():
    dao = FryItemDAO()
    expected = ResponseCode("SUCCESS", [{"FRY_ID": 2}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_all_fries_with_details(limit=3)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                f.FRY_ID, f.ORDER_ITEM_ID,
                ft.FRY_TYPE_ID, ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE,
                fs.FRY_SIZE_ID, fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE,
                fse.FRY_SEASONING_ID, fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE
            """,
        join_clauses=[
            "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
            "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
            "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID",
        ],
        limit=3,
    )


def test_fry_item_dao_get_fries_by_order_item_delegates_join_query():
    dao = FryItemDAO()
    expected = ResponseCode("SUCCESS", [{"ORDER_ITEM_ID": 5}])
    execute_join_query = MagicMock(return_value=expected)
    dao.execute_join_query = execute_join_query

    result = dao.get_fries_by_order_item(5)

    assert result is expected
    execute_join_query.assert_called_once_with(
        select_clause="""
                f.FRY_ID, f.ORDER_ITEM_ID,
                ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE,
                fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE,
                fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE
            """,
        join_clauses=[
            "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
            "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
            "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID",
        ],
        where_clause="f.ORDER_ITEM_ID = ?",
        parameters=[5],
    )
