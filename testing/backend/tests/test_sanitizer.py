import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from main.utilities.sanitizer import (
    sanitize_string,
    sanitize_email,
    sanitize_integer,
    sanitize_float,
    sanitize_datetime,
    sanitize_list,
    sanitize_customer,
    sanitize_order,
    sanitize_order_item,
    sanitize_burger_item,
    sanitize_burger_item_topping,
    sanitize_fry_item,
    sanitize_and_unmarshal,
    sanitize_and_unmarshal_list,
)
from main.backend.entities import (
    Customer, Order, OrderItem, BurgerItem, BurgerItemTopping, FryItem,
)


# ==================== sanitize_string ====================

class TestSanitizeString:
    def test_returns_stripped_value(self):
        assert sanitize_string("  hello  ") == "hello"

    def test_allows_normal_string(self):
        assert sanitize_string("hello") == "hello"

    def test_raises_on_none(self):
        with pytest.raises(ValueError):
            sanitize_string(None)

    def test_raises_on_empty_by_default(self):
        with pytest.raises(ValueError):
            sanitize_string("")

    def test_allows_empty_when_flag_set(self):
        assert sanitize_string("", allow_empty=True) == ""

    def test_allows_none_when_flag_set(self):
        assert sanitize_string(None, allow_empty=True) == ""

    def test_raises_when_over_max_length(self):
        with pytest.raises(ValueError):
            sanitize_string("abcde", max_length=3)

    def test_accepts_value_at_max_length(self):
        assert sanitize_string("abc", max_length=3) == "abc"

    def test_strips_control_characters(self):
        result = sanitize_string("hel\x00lo")
        assert "\x00" not in result
        assert "hello" in result

    def test_converts_non_string_to_string(self):
        assert sanitize_string(42) == "42"


# ==================== sanitize_email ====================

class TestSanitizeEmail:
    def test_valid_email_lowercased(self):
        assert sanitize_email("Test@Example.COM") == "test@example.com"

    def test_rejects_missing_at(self):
        with pytest.raises(ValueError):
            sanitize_email("notanemail")

    def test_rejects_missing_domain(self):
        with pytest.raises(ValueError):
            sanitize_email("user@")

    def test_rejects_missing_tld(self):
        with pytest.raises(ValueError):
            sanitize_email("user@domain")

    def test_rejects_none(self):
        with pytest.raises(ValueError):
            sanitize_email(None)

    def test_accepts_subdomain(self):
        result = sanitize_email("user@mail.example.com")
        assert result == "user@mail.example.com"

    def test_rejects_email_over_255_chars(self):
        long_local = "a" * 250
        with pytest.raises(ValueError):
            sanitize_email(f"{long_local}@example.com")


# ==================== sanitize_integer ====================

class TestSanitizeInteger:
    def test_converts_string_digit(self):
        assert sanitize_integer("42") == 42

    def test_passes_through_int(self):
        assert sanitize_integer(7) == 7

    def test_raises_on_none(self):
        with pytest.raises(ValueError):
            sanitize_integer(None)

    def test_raises_on_non_numeric_string(self):
        with pytest.raises(ValueError):
            sanitize_integer("abc")

    def test_raises_below_min(self):
        with pytest.raises(ValueError):
            sanitize_integer(0, min_value=1)

    def test_raises_above_max(self):
        with pytest.raises(ValueError):
            sanitize_integer(100, max_value=50)

    def test_accepts_boundary_min(self):
        assert sanitize_integer(1, min_value=1) == 1

    def test_accepts_boundary_max(self):
        assert sanitize_integer(50, max_value=50) == 50

    def test_truncates_float_to_int(self):
        assert sanitize_integer(3.9) == 3


# ==================== sanitize_float ====================

class TestSanitizeFloat:
    def test_converts_string(self):
        assert sanitize_float("3.14") == pytest.approx(3.14)

    def test_passes_int(self):
        assert sanitize_float(5) == pytest.approx(5.0)

    def test_raises_on_none(self):
        with pytest.raises(ValueError):
            sanitize_float(None)

    def test_raises_on_non_numeric(self):
        with pytest.raises(ValueError):
            sanitize_float("bad")

    def test_raises_below_min(self):
        with pytest.raises(ValueError):
            sanitize_float(-1.0, min_value=0.0)

    def test_raises_above_max(self):
        with pytest.raises(ValueError):
            sanitize_float(200.0, max_value=100.0)

    def test_zero_accepted_when_min_is_zero(self):
        assert sanitize_float(0.0, min_value=0.0) == pytest.approx(0.0)


# ==================== sanitize_datetime ====================

class TestSanitizeDateTime:
    def test_passes_through_datetime_object(self):
        dt = datetime(2025, 1, 15, 12, 0, 0)
        assert sanitize_datetime(dt) == dt

    def test_parses_iso_string(self):
        result = sanitize_datetime("2025-01-15 12:00:00")
        assert result == datetime(2025, 1, 15, 12, 0, 0)

    def test_parses_date_only_string(self):
        result = sanitize_datetime("2025-06-01")
        assert result == datetime(2025, 6, 1)

    def test_parses_t_format(self):
        result = sanitize_datetime("2025-01-15T12:00:00")
        assert result == datetime(2025, 1, 15, 12, 0, 0)

    def test_raises_on_none(self):
        with pytest.raises(ValueError):
            sanitize_datetime(None)

    def test_raises_on_unparseable_string(self):
        with pytest.raises(ValueError):
            sanitize_datetime("not-a-date")

    def test_accepts_unix_timestamp(self):
        result = sanitize_datetime(0.0)
        assert isinstance(result, datetime)


# ==================== sanitize_list ====================

class TestSanitizeList:
    def test_empty_list_returns_empty(self):
        result = sanitize_list([], int, sanitize_integer)
        assert result == []

    def test_none_returns_empty(self):
        result = sanitize_list(None, int, sanitize_integer)
        assert result == []

    def test_converts_items(self):
        result = sanitize_list(["1", "2", "3"], int, sanitize_integer)
        assert result == [1, 2, 3]

    def test_raises_on_non_list(self):
        with pytest.raises(ValueError):
            sanitize_list("not-a-list", int, sanitize_integer)

    def test_error_message_includes_index(self):
        with pytest.raises(ValueError, match="item 1"):
            sanitize_list(["1", "bad", "3"], int, sanitize_integer)


# ==================== sanitize_customer ====================

class TestSanitizeCustomer:
    def _valid_data(self):
        return {
            "email": "test@example.com",
            "name": "Jane Doe",
            "billing_address": "123 Bill St",
            "shipping_address": "456 Ship Ave",
        }

    def test_returns_customer_entity(self):
        result = sanitize_customer(self._valid_data())
        assert isinstance(result, Customer)

    def test_email_is_lowercased(self):
        data = self._valid_data()
        data["email"] = "TEST@EXAMPLE.COM"
        result = sanitize_customer(data)
        assert result.email == "test@example.com"

    def test_accepts_bill_addr_key(self):
        data = self._valid_data()
        del data["billing_address"]
        data["bill_addr"] = "123 Bill St"
        result = sanitize_customer(data)
        assert isinstance(result, Customer)

    def test_accepts_ship_addr_key(self):
        data = self._valid_data()
        del data["shipping_address"]
        data["ship_addr"] = "456 Ship Ave"
        result = sanitize_customer(data)
        assert isinstance(result, Customer)

    def test_raises_on_invalid_email(self):
        data = self._valid_data()
        data["email"] = "not-an-email"
        with pytest.raises(ValueError):
            sanitize_customer(data)

    def test_raises_on_missing_name(self):
        data = self._valid_data()
        data["name"] = None
        with pytest.raises(ValueError):
            sanitize_customer(data)


# ==================== sanitize_order ====================

class TestSanitizeOrder:
    def _valid_data(self):
        return {
            "order_id": 1,
            "email": "user@example.com",
            "purchase_date": "2025-01-15 12:00:00",
            "order_qty": 2,
            "total_price": 15.99,
        }

    def test_returns_order_entity(self):
        result = sanitize_order(self._valid_data())
        assert isinstance(result, Order)

    def test_raises_on_zero_order_id(self):
        data = self._valid_data()
        data["order_id"] = 0
        with pytest.raises(ValueError):
            sanitize_order(data)

    def test_raises_on_negative_price(self):
        data = self._valid_data()
        data["total_price"] = -1.0
        with pytest.raises(ValueError):
            sanitize_order(data)

    def test_accepts_order_quantity_key(self):
        data = self._valid_data()
        del data["order_qty"]
        data["order_quantity"] = 3
        result = sanitize_order(data)
        assert isinstance(result, Order)


# ==================== sanitize_order_item ====================

class TestSanitizeOrderItem:
    def _valid_data(self):
        return {
            "order_item_id": 1,
            "order_id": 1,
            "item_type": "BURGER",
            "unit_price": 7.50,
        }

    def test_returns_order_item_entity(self):
        result = sanitize_order_item(self._valid_data())
        assert isinstance(result, OrderItem)

    def test_raises_on_negative_unit_price(self):
        data = self._valid_data()
        data["unit_price"] = -5.0
        with pytest.raises(ValueError):
            sanitize_order_item(data)


# ==================== sanitize_burger_item ====================

class TestSanitizeBurgerItem:
    def _valid_data(self):
        return {
            "burger_id": 1,
            "order_item_id": 1,
            "bun_type": 2,
            "patty_type": 3,
        }

    def test_returns_burger_item_entity(self):
        result = sanitize_burger_item(self._valid_data())
        assert isinstance(result, BurgerItem)

    def test_accepts_bun_id_key(self):
        data = self._valid_data()
        del data["bun_type"]
        data["bun_id"] = 2
        result = sanitize_burger_item(data)
        assert isinstance(result, BurgerItem)

    def test_raises_on_zero_burger_id(self):
        data = self._valid_data()
        data["burger_id"] = 0
        with pytest.raises(ValueError):
            sanitize_burger_item(data)


# ==================== sanitize_burger_item_topping ====================

class TestSanitizeBurgerItemTopping:
    def test_returns_topping_entity(self):
        result = sanitize_burger_item_topping(
            {"topping_id": 5, "burger_order_id": 1}
        )
        assert isinstance(result, BurgerItemTopping)

    def test_accepts_burger_id_key(self):
        result = sanitize_burger_item_topping(
            {"topping_id": 5, "burger_id": 1}
        )
        assert isinstance(result, BurgerItemTopping)

    def test_raises_on_zero_topping_id(self):
        with pytest.raises(ValueError):
            sanitize_burger_item_topping({"topping_id": 0, "burger_order_id": 1})


# ==================== sanitize_fry_item ====================

class TestSanitizeFryItem:
    def _valid_data(self):
        return {
            "fry_id": 1,
            "order_item_id": 1,
            "fry_type": 2,
            "fry_size": 3,
            "fry_seasoning": 4,
        }

    def test_returns_fry_item_entity(self):
        result = sanitize_fry_item(self._valid_data())
        assert isinstance(result, FryItem)

    def test_accepts_type_id_key(self):
        data = self._valid_data()
        del data["fry_type"]
        data["type_id"] = 2
        result = sanitize_fry_item(data)
        assert isinstance(result, FryItem)

    def test_raises_on_zero_fry_id(self):
        data = self._valid_data()
        data["fry_id"] = 0
        with pytest.raises(ValueError):
            sanitize_fry_item(data)


# ==================== sanitize_and_unmarshal ====================

class TestSanitizeAndUnmarshal:
    def _customer_data(self):
        return {
            "email": "test@example.com",
            "name": "Jane Doe",
            "billing_address": "123 Bill St",
            "shipping_address": "456 Ship Ave",
        }

    def test_unmarshals_customer(self):
        result = sanitize_and_unmarshal(self._customer_data(), Customer)
        assert isinstance(result, Customer)

    def test_raises_on_empty_dict(self):
        with pytest.raises(ValueError):
            sanitize_and_unmarshal({}, Customer)

    def test_raises_on_none(self):
        with pytest.raises(ValueError):
            sanitize_and_unmarshal(None, Customer)

    def test_raises_on_non_dict(self):
        with pytest.raises(ValueError):
            sanitize_and_unmarshal("bad input", Customer)

    def test_raises_on_unsupported_entity_type(self):
        class Unsupported:
            pass
        with pytest.raises(ValueError, match="No sanitizer available"):
            sanitize_and_unmarshal(self._customer_data(), Unsupported)


# ==================== sanitize_and_unmarshal_list ====================

class TestSanitizeAndUnmarshalList:
    def _customer_data(self):
        return {
            "email": "test@example.com",
            "name": "Jane Doe",
            "billing_address": "123 Bill St",
            "shipping_address": "456 Ship Ave",
        }

    def test_unmarshals_list_of_customers(self):
        data_list = [self._customer_data(), {**self._customer_data(), "email": "other@example.com"}]
        results = sanitize_and_unmarshal_list(data_list, Customer)
        assert len(results) == 2
        assert all(isinstance(r, Customer) for r in results)

    def test_raises_on_non_list(self):
        with pytest.raises(ValueError):
            sanitize_and_unmarshal_list("not-a-list", Customer)

    def test_empty_list_returns_empty(self):
        results = sanitize_and_unmarshal_list([], Customer)
        assert results == []

    def test_error_message_includes_index(self):
        bad_item = {"email": "bad", "name": "X", "billing_address": "B", "shipping_address": "S"}
        with pytest.raises(ValueError, match="item 0"):
            sanitize_and_unmarshal_list([bad_item], Customer)


# ==================== sanitize_datetime timestamp branch ====================

class TestSanitizeDatetimeTimestamp:
    def test_accepts_integer_unix_timestamp(self):
        from datetime import datetime
        from main.utilities.sanitizer import sanitize_datetime
        result = sanitize_datetime(1000000)
        assert isinstance(result, datetime)

    def test_accepts_float_unix_timestamp(self):
        from datetime import datetime
        from main.utilities.sanitizer import sanitize_datetime
        result = sanitize_datetime(1000000.5)
        assert isinstance(result, datetime)
