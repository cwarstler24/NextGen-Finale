"""
Tests for DAO helper methods: _row_to_dict, _build_insert_sql, _build_update_sql.

DAOs can be instantiated directly because AbstractDAO.__init__ only stores
table_name, primary_key, and a logger — no DB connection is attempted.
"""
from main.backend.bunTypeDAO import BunTypeDAO
from main.backend.pattyTypeDAO import PattyTypeDAO
from main.backend.toppingDAO import ToppingDAO
from main.backend.fryTypeDAO import FryTypeDAO
from main.backend.frySizeDAO import FrySizeDAO
from main.backend.frySeasoningDAO import FrySeasoningDAO
from main.backend.orderDAO import OrderDAO
from main.backend.orderItemDAO import OrderItemDAO
from main.backend.customerDAO import CustomerDAO
from main.backend.fryItemDAO import FryItemDAO
from main.backend.burgerItemDAO import BurgerItemDAO
from main.backend.burgerItemToppingDAO import BurgerItemToppingDAO


# ==================== BunTypeDAO ====================

class TestBunTypeDAOMethods:
    def setup_method(self):
        self.dao = BunTypeDAO()

    def test_row_to_dict(self):
        row = (1, "Sesame", 10, 1.50)
        result = self.dao._row_to_dict(row)
        assert result == {"BUN_ID": 1, "BUN_NAME": "Sesame", "STOCK_QUANTITY": 10, "PRICE": 1.50}

    def test_build_insert_sql_contains_insert(self):
        entry = {"BUN_ID": 1, "BUN_NAME": "Sesame", "STOCK_QUANTITY": 10, "PRICE": 1.50}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert values == [1, "Sesame", 10, 1.50]

    def test_build_insert_sql_uses_table_name(self):
        sql, _ = self.dao._build_insert_sql({"BUN_ID": 1, "BUN_NAME": "X", "STOCK_QUANTITY": 1, "PRICE": 0})
        assert "TBBUN_TYPES" in sql

    def test_build_update_sql_single_field(self):
        clause, values = self.dao._build_update_sql({"STOCK_QUANTITY": 5})
        assert "STOCK_QUANTITY = ?" in clause
        assert values == [5]

    def test_build_update_sql_multiple_fields(self):
        clause, values = self.dao._build_update_sql({"STOCK_QUANTITY": 3, "PRICE": 2.00})
        assert "STOCK_QUANTITY = ?" in clause
        assert "PRICE = ?" in clause
        assert len(values) == 2


# ==================== PattyTypeDAO ====================

class TestPattyTypeDAOMethods:
    def setup_method(self):
        self.dao = PattyTypeDAO()

    def test_row_to_dict(self):
        row = (2, "Beef", 5, 3.00)
        assert self.dao._row_to_dict(row) == {
            "PATTY_ID": 2, "PATTY_NAME": "Beef", "STOCK_QUANTITY": 5, "PRICE": 3.00
        }

    def test_build_insert_sql(self):
        entry = {"PATTY_ID": 2, "PATTY_NAME": "Beef", "STOCK_QUANTITY": 5, "PRICE": 3.00}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBPATTY_TYPES" in sql
        assert values == [2, "Beef", 5, 3.00]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"PATTY_NAME": "Chicken", "PRICE": 2.50})
        assert "PATTY_NAME = ?" in clause
        assert values == ["Chicken", 2.50]


# ==================== ToppingDAO ====================

class TestToppingDAOMethods:
    def setup_method(self):
        self.dao = ToppingDAO()

    def test_row_to_dict(self):
        row = (3, "Lettuce", 20, 0.50)
        assert self.dao._row_to_dict(row) == {
            "TOPPING_ID": 3, "TOPPING_NAME": "Lettuce", "STOCK_QUANTITY": 20, "PRICE": 0.50
        }

    def test_build_insert_sql(self):
        entry = {"TOPPING_ID": 3, "TOPPING_NAME": "Lettuce", "STOCK_QUANTITY": 20, "PRICE": 0.50}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBTOPPINGS" in sql
        assert values == [3, "Lettuce", 20, 0.50]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"STOCK_QUANTITY": 15})
        assert "STOCK_QUANTITY = ?" in clause
        assert values == [15]


# ==================== FryTypeDAO ====================

class TestFryTypeDAOMethods:
    def setup_method(self):
        self.dao = FryTypeDAO()

    def test_row_to_dict(self):
        row = (1, "Shoestring", 8, 0.25)
        assert self.dao._row_to_dict(row) == {
            "FRY_TYPE_ID": 1, "FRY_TYPE_NAME": "Shoestring", "STOCK_QUANTITY": 8, "PRICE": 0.25
        }

    def test_build_insert_sql(self):
        entry = {"FRY_TYPE_ID": 1, "FRY_TYPE_NAME": "Shoestring", "STOCK_QUANTITY": 8, "PRICE": 0.25}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBFRY_TYPES" in sql
        assert values == [1, "Shoestring", 8, 0.25]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"FRY_TYPE_NAME": "Crinkle"})
        assert "FRY_TYPE_NAME = ?" in clause
        assert values == ["Crinkle"]


# ==================== FrySizeDAO ====================

class TestFrySizeDAOMethods:
    def setup_method(self):
        self.dao = FrySizeDAO()

    def test_row_to_dict(self):
        row = (2, 8, 15, 0.75)
        assert self.dao._row_to_dict(row) == {
            "FRY_SIZE_ID": 2, "FRY_SIZE": 8, "STOCK_QUANTITY": 15, "PRICE": 0.75
        }

    def test_build_insert_sql(self):
        entry = {"FRY_SIZE_ID": 2, "FRY_SIZE": 8, "STOCK_QUANTITY": 15, "PRICE": 0.75}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBFRY_SIZES" in sql
        assert values == [2, 8, 15, 0.75]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"PRICE": 1.00, "STOCK_QUANTITY": 10})
        assert "PRICE = ?" in clause
        assert "STOCK_QUANTITY = ?" in clause


# ==================== FrySeasoningDAO ====================

class TestFrySeasoningDAOMethods:
    def setup_method(self):
        self.dao = FrySeasoningDAO()

    def test_row_to_dict(self):
        row = (4, "Cajun", 12, 0.10)
        assert self.dao._row_to_dict(row) == {
            "FRY_SEASONING_ID": 4, "FRY_SEASONING_NAME": "Cajun", "STOCK_QUANTITY": 12, "PRICE": 0.10
        }

    def test_build_insert_sql(self):
        entry = {"FRY_SEASONING_ID": 4, "FRY_SEASONING_NAME": "Cajun", "STOCK_QUANTITY": 12, "PRICE": 0.10}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBFRY_SEASONINGS" in sql
        assert values == [4, "Cajun", 12, 0.10]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"FRY_SEASONING_NAME": "Salt"})
        assert "FRY_SEASONING_NAME = ?" in clause
        assert values == ["Salt"]


# ==================== OrderDAO ====================

class TestOrderDAOMethods:
    def setup_method(self):
        self.dao = OrderDAO()

    def test_row_to_dict(self):
        from datetime import datetime
        dt = datetime(2025, 1, 15, 12, 0, 0)
        row = (42, "user@example.com", dt, 3, 19.99)
        result = self.dao._row_to_dict(row)
        assert result == {
            "ORDER_ID": 42,
            "EMAIL": "user@example.com",
            "PURCHASE_DATE": dt,
            "ORDER_QTY": 3,
            "TOTAL_PRICE": 19.99,
        }

    def test_build_insert_sql(self):
        from datetime import datetime
        dt = datetime(2025, 1, 15, 12, 0, 0)
        entry = {"ORDER_ID": 42, "EMAIL": "user@example.com", "PURCHASE_DATE": dt, "ORDER_QTY": 3, "TOTAL_PRICE": 19.99}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBORDERS" in sql
        assert values == [42, "user@example.com", dt, 3, 19.99]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"ORDER_QTY": 5, "TOTAL_PRICE": 29.99})
        assert "ORDER_QTY = ?" in clause
        assert "TOTAL_PRICE = ?" in clause


# ==================== OrderItemDAO ====================

class TestOrderItemDAOMethods:
    def setup_method(self):
        self.dao = OrderItemDAO()

    def test_row_to_dict(self):
        row = (42, 7, "BURGER", 8.50)
        result = self.dao._row_to_dict(row)
        assert result == {
            "ORDER_ID": 42,
            "ORDER_ITEM_ID": 7,
            "ITEM_TYPE": "BURGER",
            "UNIT_PRICE": 8.50,
        }

    def test_build_insert_sql(self):
        entry = {"ORDER_ID": 42, "ORDER_ITEM_ID": 7, "ITEM_TYPE": "BURGER", "UNIT_PRICE": 8.50}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBORDER_ITEMS" in sql
        assert values == [42, 7, "BURGER", 8.50]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"UNIT_PRICE": 9.00})
        assert "UNIT_PRICE = ?" in clause
        assert values == [9.00]


# ==================== CustomerDAO ====================

class TestCustomerDAOMethods:
    def setup_method(self):
        self.dao = CustomerDAO()

    def test_row_to_dict(self):
        row = ("jane@example.com", "Jane Doe", "123 Bill St", "456 Ship Ave")
        result = self.dao._row_to_dict(row)
        assert result == {
            "EMAIL": "jane@example.com",
            "NAME": "Jane Doe",
            "BILL_ADDR": "123 Bill St",
            "SHIP_ADDR": "456 Ship Ave",
        }

    def test_build_insert_sql(self):
        entry = {"EMAIL": "jane@example.com", "NAME": "Jane", "BILL_ADDR": "1 St", "SHIP_ADDR": "2 Ave"}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBCUSTOMER" in sql
        assert values == ["jane@example.com", "Jane", "1 St", "2 Ave"]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"NAME": "Jane Smith", "SHIP_ADDR": "789 New Ave"})
        assert "NAME = ?" in clause
        assert "SHIP_ADDR = ?" in clause
        assert values == ["Jane Smith", "789 New Ave"]


# ==================== FryItemDAO ====================

class TestFryItemDAOMethods:
    def setup_method(self):
        self.dao = FryItemDAO()

    def test_row_to_dict(self):
        row = (9, 7, 2, 3, 4)
        result = self.dao._row_to_dict(row)
        assert result == {
            "FRY_ID": 9,
            "ORDER_ITEM_ID": 7,
            "FRY_TYPE": 2,
            "FRY_SIZE": 3,
            "FRY_SEASONING": 4,
        }

    def test_build_insert_sql(self):
        entry = {"FRY_ID": 9, "ORDER_ITEM_ID": 7, "FRY_TYPE": 2, "FRY_SIZE": 3, "FRY_SEASONING": 4}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBFRY_ITEMS" in sql
        assert values == [9, 7, 2, 3, 4]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"FRY_SIZE": 5, "FRY_SEASONING": 2})
        assert "FRY_SIZE = ?" in clause
        assert "FRY_SEASONING = ?" in clause


# ==================== BurgerItemDAO ====================

class TestBurgerItemDAOMethods:
    def setup_method(self):
        self.dao = BurgerItemDAO()

    def test_row_to_dict_four_columns(self):
        """_row_to_dict maps rows with 4 fields (PATTY_COUNT is absent from DB rows)."""
        row = (5, 7, 1, 2)
        result = self.dao._row_to_dict(row)
        assert result == {
            "BURGER_ID": 5,
            "ORDER_ITEM_ID": 7,
            "BUN_TYPE": 1,
            "PATTY_TYPE": 2,
        }

    def test_build_insert_sql_five_columns(self):
        entry = {"BURGER_ID": 5, "ORDER_ITEM_ID": 7, "BUN_TYPE": 1, "PATTY_TYPE": 2, "PATTY_COUNT": 3}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBBURGER_ITEMS" in sql
        assert values == [5, 7, 1, 2, 3]

    def test_build_insert_sql_defaults_patty_count_to_one(self):
        entry = {"BURGER_ID": 5, "ORDER_ITEM_ID": 7, "BUN_TYPE": 1, "PATTY_TYPE": 2}
        _, values = self.dao._build_insert_sql(entry)
        assert values[4] == 1

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"BUN_TYPE": 2, "PATTY_COUNT": 2})
        assert "BUN_TYPE = ?" in clause
        assert "PATTY_COUNT = ?" in clause


# ==================== BurgerItemToppingDAO ====================

class TestBurgerItemToppingDAOMethods:
    def setup_method(self):
        self.dao = BurgerItemToppingDAO()

    def test_row_to_dict(self):
        row = (3, 5)
        result = self.dao._row_to_dict(row)
        assert result == {"TOPPING_ID": 3, "BURGER_ORDER_ID": 5}

    def test_build_insert_sql(self):
        entry = {"TOPPING_ID": 3, "BURGER_ORDER_ID": 5}
        sql, values = self.dao._build_insert_sql(entry)
        assert "INSERT INTO" in sql
        assert "TBBURGER_TOPPINGS" in sql
        assert values == [3, 5]

    def test_build_update_sql(self):
        clause, values = self.dao._build_update_sql({"TOPPING_ID": 4})
        assert "TOPPING_ID = ?" in clause
        assert values == [4]
