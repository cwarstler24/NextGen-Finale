"""
Tests for all entity classes in entities.py.
Covers to_dict(), from_dict(), get_primary_key(), and __repr__() for every entity.
"""
from datetime import datetime
from decimal import Decimal

from main.backend.entities import (
    Customer, Order, OrderItem,
    BurgerItem, BurgerItemTopping, FryItem,
    BunType, PattyType, Topping,
    FryType, FrySize, FrySeasoning,
)


# ==================== Customer ====================

class TestCustomerEntity:
    def _make(self):
        return Customer(
            email="jane@example.com",
            name="Jane Doe",
            bill_addr="123 Bill St",
            ship_addr="456 Ship Ave",
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d == {
            "EMAIL": "jane@example.com",
            "NAME": "Jane Doe",
            "BILL_ADDR": "123 Bill St",
            "SHIP_ADDR": "456 Ship Ave",
        }

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = Customer.from_dict(original.to_dict())
        assert restored.email == original.email
        assert restored.name == original.name
        assert restored.bill_addr == original.bill_addr
        assert restored.ship_addr == original.ship_addr

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == "jane@example.com"

    def test_repr_contains_class_name(self):
        assert "Customer" in repr(self._make())

    def test_from_dict_with_none_values(self):
        restored = Customer.from_dict({})
        assert restored.email is None


# ==================== Order ====================

class TestOrderEntity:
    def _make(self):
        return Order(
            order_id=42,
            email="user@example.com",
            purchase_date=datetime(2025, 1, 15, 12, 0, 0),
            order_qty=3,
            total_price=19.99,
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["ORDER_ID"] == 42
        assert d["EMAIL"] == "user@example.com"
        assert d["ORDER_QTY"] == 3
        assert d["TOTAL_PRICE"] == 19.99

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = Order.from_dict(original.to_dict())
        assert restored.order_id == 42
        assert restored.total_price == 19.99

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 42

    def test_repr_contains_class_name(self):
        assert "Order" in repr(self._make())


# ==================== OrderItem ====================

class TestOrderItemEntity:
    def _make(self):
        return OrderItem(
            order_item_id=7,
            order_id=42,
            item_type="BURGER",
            unit_price=8.50,
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d == {
            "ORDER_ITEM_ID": 7,
            "ORDER_ID": 42,
            "ITEM_TYPE": "BURGER",
            "UNIT_PRICE": 8.50,
        }

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = OrderItem.from_dict(original.to_dict())
        assert restored.order_item_id == 7
        assert restored.item_type == "BURGER"

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 7

    def test_repr_contains_class_name(self):
        assert "OrderItem" in repr(self._make())


# ==================== BurgerItem ====================

class TestBurgerItemEntity:
    def _make(self, patty_count=2):
        return BurgerItem(
            burger_id=5,
            order_item_id=7,
            bun_type=1,
            patty_type=2,
            patty_count=patty_count,
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d == {
            "BURGER_ID": 5,
            "ORDER_ITEM_ID": 7,
            "BUN_TYPE": 1,
            "PATTY_TYPE": 2,
            "PATTY_COUNT": 2,
        }

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = BurgerItem.from_dict(original.to_dict())
        assert restored.burger_id == 5
        assert restored.patty_count == 2

    def test_from_dict_default_patty_count(self):
        restored = BurgerItem.from_dict({"BURGER_ID": 1, "ORDER_ITEM_ID": 1, "BUN_TYPE": 1, "PATTY_TYPE": 1})
        assert restored.patty_count == 1

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 5

    def test_repr_contains_class_name(self):
        assert "BurgerItem" in repr(self._make())


# ==================== BurgerItemTopping ====================

class TestBurgerItemToppingEntity:
    def _make(self):
        return BurgerItemTopping(topping_id=3, burger_order_id=5)

    def test_to_dict_keys(self):
        assert self._make().to_dict() == {
            "TOPPING_ID": 3,
            "BURGER_ORDER_ID": 5,
        }

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = BurgerItemTopping.from_dict(original.to_dict())
        assert restored.topping_id == 3
        assert restored.burger_order_id == 5

    def test_get_primary_key_returns_tuple(self):
        key = self._make().get_primary_key()
        assert key == (3, 5)

    def test_repr_contains_class_name(self):
        assert "BurgerItemTopping" in repr(self._make())


# ==================== FryItem ====================

class TestFryItemEntity:
    def _make(self):
        return FryItem(
            fry_id=9,
            order_item_id=7,
            fry_type=2,
            fry_size=3,
            fry_seasoning=4,
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d == {
            "FRY_ID": 9,
            "ORDER_ITEM_ID": 7,
            "FRY_TYPE": 2,
            "FRY_SIZE": 3,
            "FRY_SEASONING": 4,
        }

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = FryItem.from_dict(original.to_dict())
        assert restored.fry_id == 9
        assert restored.fry_seasoning == 4

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 9

    def test_repr_contains_class_name(self):
        assert "FryItem" in repr(self._make())


# ==================== BunType ====================

class TestBunTypeEntity:
    def _make(self):
        return BunType(bun_id=1, bun_name="Sesame", stock_quantity=10, price=Decimal("1.50"))

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["BUN_ID"] == 1
        assert d["BUN_NAME"] == "Sesame"
        assert d["STOCK_QUANTITY"] == 10
        assert d["PRICE"] == 1.50

    def test_to_dict_none_price(self):
        entity = BunType(bun_id=1, bun_name="X", stock_quantity=1, price=None)
        assert entity.to_dict()["PRICE"] is None

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = BunType.from_dict(original.to_dict())
        assert restored.bun_id == 1
        assert restored.bun_name == "Sesame"

    def test_from_dict_none_price(self):
        restored = BunType.from_dict({"BUN_ID": 1, "BUN_NAME": "X", "STOCK_QUANTITY": 1, "PRICE": None})
        assert restored.price is None

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 1

    def test_repr_contains_class_name(self):
        assert "BunType" in repr(self._make())


# ==================== PattyType ====================

class TestPattyTypeEntity:
    def _make(self):
        return PattyType(patty_id=2, patty_name="Beef", stock_quantity=5, price=Decimal("3.00"))

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["PATTY_ID"] == 2
        assert d["PATTY_NAME"] == "Beef"
        assert d["PRICE"] == 3.00

    def test_to_dict_none_price(self):
        entity = PattyType(patty_id=1, patty_name="X", stock_quantity=1, price=None)
        assert entity.to_dict()["PRICE"] is None

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = PattyType.from_dict(original.to_dict())
        assert restored.patty_id == 2
        assert restored.patty_name == "Beef"

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 2

    def test_repr_contains_class_name(self):
        assert "PattyType" in repr(self._make())


# ==================== Topping ====================

class TestToppingEntity:
    def _make(self):
        return Topping(topping_id=3, topping_name="Lettuce", stock_quantity=20, price=Decimal("0.50"))

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["TOPPING_ID"] == 3
        assert d["TOPPING_NAME"] == "Lettuce"
        assert d["PRICE"] == 0.50

    def test_to_dict_none_price(self):
        entity = Topping(topping_id=1, topping_name="X", stock_quantity=1, price=None)
        assert entity.to_dict()["PRICE"] is None

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = Topping.from_dict(original.to_dict())
        assert restored.topping_id == 3
        assert restored.topping_name == "Lettuce"

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 3

    def test_repr_contains_class_name(self):
        assert "Topping" in repr(self._make())


# ==================== FryType ====================

class TestFryTypeEntity:
    def _make(self):
        return FryType(fry_type_id=1, fry_type_name="Shoestring", stock_quantity=8, price=Decimal("0.25"))

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["FRY_TYPE_ID"] == 1
        assert d["FRY_TYPE_NAME"] == "Shoestring"
        assert d["PRICE"] == 0.25

    def test_to_dict_none_price(self):
        entity = FryType(fry_type_id=1, fry_type_name="X", stock_quantity=1, price=None)
        assert entity.to_dict()["PRICE"] is None

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = FryType.from_dict(original.to_dict())
        assert restored.fry_type_id == 1
        assert restored.fry_type_name == "Shoestring"

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 1

    def test_repr_contains_class_name(self):
        assert "FryType" in repr(self._make())


# ==================== FrySize ====================

class TestFrySizeEntity:
    def _make(self):
        return FrySize(fry_size_id=2, fry_size=8, stock_quantity=15, price=Decimal("0.75"))

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["FRY_SIZE_ID"] == 2
        assert d["FRY_SIZE"] == 8
        assert d["PRICE"] == 0.75

    def test_to_dict_none_price(self):
        entity = FrySize(fry_size_id=1, fry_size=4, stock_quantity=1, price=None)
        assert entity.to_dict()["PRICE"] is None

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = FrySize.from_dict(original.to_dict())
        assert restored.fry_size_id == 2
        assert restored.fry_size == 8

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 2

    def test_repr_contains_class_name(self):
        assert "FrySize" in repr(self._make())


# ==================== FrySeasoning ====================

class TestFrySeasoningEntity:
    def _make(self):
        return FrySeasoning(
            fry_seasoning_id=4,
            fry_seasoning_name="Cajun",
            stock_quantity=12,
            price=Decimal("0.10"),
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["FRY_SEASONING_ID"] == 4
        assert d["FRY_SEASONING_NAME"] == "Cajun"
        assert d["PRICE"] == 0.10

    def test_to_dict_none_price(self):
        entity = FrySeasoning(fry_seasoning_id=1, fry_seasoning_name="X", stock_quantity=1, price=None)
        assert entity.to_dict()["PRICE"] is None

    def test_from_dict_roundtrip(self):
        original = self._make()
        restored = FrySeasoning.from_dict(original.to_dict())
        assert restored.fry_seasoning_id == 4
        assert restored.fry_seasoning_name == "Cajun"

    def test_get_primary_key(self):
        assert self._make().get_primary_key() == 4

    def test_repr_contains_class_name(self):
        assert "FrySeasoning" in repr(self._make())
