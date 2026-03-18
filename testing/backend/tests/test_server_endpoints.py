"""
Integration-style tests for the FastAPI server endpoints.

All DAO and database calls are mocked — no real database connection is needed.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main.backend.server import app
from main.utilities.error_handler import ResponseCode

client = TestClient(app)


@pytest.fixture(autouse=True)
def _no_real_db(monkeypatch):
    """Prevent every test in this module from ever touching a real DB2 connection."""
    fake_cursor = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=fake_cursor)
    mock_cm.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("main.backend.server.get_db_cursor", lambda: mock_cm)


def _ok(data=None):
    """Build a mock ResponseCode that reports success."""
    rc = MagicMock()
    rc.success = True
    rc.data = data
    return rc


def _fail():
    """Build a mock ResponseCode that reports failure."""
    rc = MagicMock()
    rc.success = False
    rc.data = None
    return rc


# ==================== GET /Items/Fries ====================

FRIES_SIZES = [{"FRY_SIZE_ID": 1, "FRY_SIZE": 4, "PRICE": 0.50, "STOCK_QUANTITY": 10}]
FRIES_TYPES = [{"FRY_TYPE_ID": 1, "FRY_TYPE_NAME": "Shoestring", "PRICE": 0.00, "STOCK_QUANTITY": 10}]
FRIES_SEASONINGS = [{"FRY_SEASONING_ID": 1, "FRY_SEASONING_NAME": "Salt", "PRICE": 0.00, "STOCK_QUANTITY": 10}]


def _patch_fries_daos(size_data=None, type_data=None, seasoning_data=None,
                      sizes_ok=True, types_ok=True, seasonings_ok=True):
    size_dao = MagicMock()
    type_dao = MagicMock()
    seasoning_dao = MagicMock()

    size_dao.get_all_records.return_value = _ok(size_data or FRIES_SIZES) if sizes_ok else _fail()
    type_dao.get_all_records.return_value = _ok(type_data or FRIES_TYPES) if types_ok else _fail()
    seasoning_dao.get_all_records.return_value = _ok(seasoning_data or FRIES_SEASONINGS) if seasonings_ok else _fail()

    def dao_factory(name):
        return {"FrySizeDAO": size_dao, "FryTypeDAO": type_dao, "FrySeasoningDAO": seasoning_dao}[name]

    return patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=dao_factory)


class TestGetFriesItems:
    def test_returns_200_with_all_fields(self):
        with _patch_fries_daos():
            response = client.get("/Items/Fries")
        assert response.status_code == 200
        body = response.json()
        assert "sizes" in body
        assert "types" in body
        assert "seasonings" in body

    def test_size_name_appends_oz(self):
        with _patch_fries_daos():
            response = client.get("/Items/Fries")
        size = response.json()["sizes"][0]
        assert "oz" in size["name"]

    def test_returns_500_if_sizes_fail(self):
        with _patch_fries_daos(sizes_ok=False):
            response = client.get("/Items/Fries")
        assert response.status_code == 500

    def test_returns_500_if_types_fail(self):
        with _patch_fries_daos(types_ok=False):
            response = client.get("/Items/Fries")
        assert response.status_code == 500

    def test_returns_500_if_seasonings_fail(self):
        with _patch_fries_daos(seasonings_ok=False):
            response = client.get("/Items/Fries")
        assert response.status_code == 500

    def test_returns_correct_price_and_no_quantity(self):
        with _patch_fries_daos():
            response = client.get("/Items/Fries")
        size = response.json()["sizes"][0]
        assert size["price"] == pytest.approx(0.50)
        assert "quantity" not in size


# ==================== GET /Items/Burger ====================

BURGER_BUNS = [{"BUN_ID": 1, "BUN_NAME": "Sesame", "PRICE": 1.00, "STOCK_QUANTITY": 5}]
BURGER_PATTIES = [{"PATTY_ID": 1, "PATTY_NAME": "Beef", "PRICE": 3.00, "STOCK_QUANTITY": 5}]
BURGER_TOPPINGS = [{"TOPPING_ID": 1, "TOPPING_NAME": "Lettuce", "PRICE": 0.50, "STOCK_QUANTITY": 5}]


def _patch_burger_daos(bun_data=None, patty_data=None, topping_data=None,
                       buns_ok=True, patties_ok=True, toppings_ok=True):
    bun_dao = MagicMock()
    patty_dao = MagicMock()
    topping_dao = MagicMock()

    bun_dao.get_all_records.return_value = _ok(bun_data or BURGER_BUNS) if buns_ok else _fail()
    patty_dao.get_all_records.return_value = _ok(patty_data or BURGER_PATTIES) if patties_ok else _fail()
    topping_dao.get_all_records.return_value = _ok(topping_data or BURGER_TOPPINGS) if toppings_ok else _fail()

    def dao_factory(name):
        return {"BunTypeDAO": bun_dao, "PattyTypeDAO": patty_dao, "ToppingDAO": topping_dao}[name]

    return patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=dao_factory)


class TestGetBurgerItems:
    def test_returns_200_with_all_fields(self):
        with _patch_burger_daos():
            response = client.get("/Items/Burger")
        assert response.status_code == 200
        body = response.json()
        assert "buns" in body
        assert "patties" in body
        assert "toppings" in body

    def test_returns_500_if_buns_fail(self):
        with _patch_burger_daos(buns_ok=False):
            response = client.get("/Items/Burger")
        assert response.status_code == 500

    def test_returns_500_if_patties_fail(self):
        with _patch_burger_daos(patties_ok=False):
            response = client.get("/Items/Burger")
        assert response.status_code == 500

    def test_returns_500_if_toppings_fail(self):
        with _patch_burger_daos(toppings_ok=False):
            response = client.get("/Items/Burger")
        assert response.status_code == 500

    def test_bun_fields_mapped_correctly(self):
        with _patch_burger_daos():
            response = client.get("/Items/Burger")
        bun = response.json()["buns"][0]
        assert bun["id"] == 1
        assert bun["name"] == "Sesame"
        assert bun["price"] == pytest.approx(1.00)
        assert bun["quantity"] == 5


# ==================== GET /Customer/{email} ====================

CUSTOMER_ROW = {
    "NAME": "Jane Doe",
    "EMAIL": "jane@example.com",
    "SHIP_ADDR": "456 Ship Ave",
    "BILL_ADDR": "123 Bill St",
    "ORDER_ID": 10,
    "PURCHASE_DATE": "2025-01-15T12:00:00",
    "TOTAL_PRICE": 9.99,
}

CUSTOMER_NO_ORDERS = {
    "NAME": "No Orders",
    "EMAIL": "none@example.com",
    "SHIP_ADDR": "1 Ave",
    "BILL_ADDR": "2 St",
    "ORDER_ID": None,
    "PURCHASE_DATE": None,
    "TOTAL_PRICE": None,
}


def _patch_customer_dao(data=None, ok=True):
    customer_dao = MagicMock()
    if ok:
        customer_dao.get_customer_with_orders.return_value = _ok(data or [CUSTOMER_ROW])
    else:
        customer_dao.get_customer_with_orders.return_value = _fail()

    order_item_dao = MagicMock()
    order_item_dao.get_all_order_items_with_details.return_value = _ok({"burgers": [], "fries": []})

    burger_item_dao = MagicMock()
    burger_item_dao.get_burger_toppings.return_value = _ok([])

    def dao_factory(name):
        return {
            "CustomerDAO": customer_dao,
            "OrderItemDAO": order_item_dao,
            "BurgerItemDAO": burger_item_dao,
        }[name]

    return patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=dao_factory)


class TestGetCustomer:
    def test_returns_200_for_valid_email(self):
        with _patch_customer_dao():
            response = client.get("/Customer/jane@example.com")
        assert response.status_code == 200

    def test_returns_customer_name_and_addresses(self):
        with _patch_customer_dao():
            response = client.get("/Customer/jane@example.com")
        body = response.json()
        assert body["name"] == "Jane Doe"
        assert body["shipping_address"] == "456 Ship Ave"
        assert body["billing_address"] == "123 Bill St"

    def test_orders_are_included(self):
        with _patch_customer_dao():
            response = client.get("/Customer/jane@example.com")
        orders = response.json()["orders"]
        assert len(orders) == 1
        assert orders[0]["price"] == pytest.approx(9.99)

    def test_customer_with_no_orders_returns_empty_list(self):
        with _patch_customer_dao(data=[CUSTOMER_NO_ORDERS]):
            response = client.get("/Customer/none@example.com")
        assert response.status_code == 200
        assert response.json()["orders"] == []

    def test_returns_404_if_dao_fails(self):
        with _patch_customer_dao(ok=False):
            response = client.get("/Customer/jane@example.com")
        assert response.status_code == 404

    def test_returns_404_if_data_is_empty(self):
        customer_dao = MagicMock()
        customer_dao.get_customer_with_orders.return_value = _ok([])

        with patch("main.backend.server.DAOFactory.get_or_create_dao", return_value=customer_dao):
            response = client.get("/Customer/jane@example.com")
        assert response.status_code == 404

    def test_returns_400_for_invalid_email_format(self):
        response = client.get("/Customer/not-an-email")
        assert response.status_code == 400

    def test_multiple_orders_all_included(self):
        row2 = {**CUSTOMER_ROW, "ORDER_ID": 11, "PURCHASE_DATE": "2025-02-01T00:00:00", "TOTAL_PRICE": 5.00}
        with _patch_customer_dao(data=[CUSTOMER_ROW, row2]):
            response = client.get("/Customer/jane@example.com")
        assert len(response.json()["orders"]) == 2


# ==================== POST /Order/ ====================

def _build_order_payload(burgers=None, fries=None, date=None):
    payload = {
        "customer": {
            "name": "Test User",
            "email": "testuser@example.com",
            "shipping_address": "1 Ship St",
            "billing_address": "2 Bill Ave",
        },
        "burgers": burgers or [],
        "fries": fries or [],
    }
    if date:
        payload["date"] = date
    return payload


from contextlib import contextmanager


@contextmanager
def _mock_db_cursor():
    """Patch get_db_cursor in the server module so no real DB connection is attempted."""
    fake_cursor = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=fake_cursor)
    mock_cm.__exit__ = MagicMock(return_value=False)
    with patch("main.backend.server.get_db_cursor", return_value=mock_cm):
        yield fake_cursor


def _build_order_daos(
    customer_exists=True, order_create_ok=True,
    order_item_create_ok=True, burger_create_ok=True, topping_create_ok=True,
    fry_create_ok=True
):
    """Return a dict of mock DAOs suitable for an order with one burger and one fries item."""
    customer_dao = MagicMock()
    customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"}) if customer_exists else _fail()

    order_dao = MagicMock()
    order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 5}])
    order_dao.create_record.return_value = _ok() if order_create_ok else _fail()

    order_item_dao = MagicMock()
    order_item_dao.get_all_records.return_value = _ok([{"ORDER_ITEM_ID": 3}])
    order_item_dao.create_record.return_value = _ok() if order_item_create_ok else _fail()
    order_item_dao.create_records_batch.return_value = _ok() if order_item_create_ok else _fail()

    burger_item_dao = MagicMock()
    burger_item_dao.get_all_records.return_value = _ok([{"BURGER_ID": 2}])
    burger_item_dao.create_record.return_value = _ok() if burger_create_ok else _fail()
    burger_item_dao.create_records_batch.return_value = _ok() if burger_create_ok else _fail()

    burger_topping_dao = MagicMock()
    burger_topping_dao.create_record.return_value = _ok() if topping_create_ok else _fail()
    burger_topping_dao.create_records_batch.return_value = _ok() if topping_create_ok else _fail()

    fry_item_dao = MagicMock()
    fry_item_dao.get_all_records.return_value = _ok([{"FRY_ID": 1}])
    fry_item_dao.create_record.return_value = _ok() if fry_create_ok else _fail()
    fry_item_dao.create_records_batch.return_value = _ok() if fry_create_ok else _fail()

    bun_dao = MagicMock()
    bun_dao.get_by_key.return_value = _ok({"PRICE": 1.00})

    patty_dao = MagicMock()
    patty_dao.get_by_key.return_value = _ok({"PRICE": 3.00})

    topping_dao = MagicMock()
    topping_dao.get_by_key.return_value = _ok({"PRICE": 0.50})

    fry_type_dao = MagicMock()
    fry_type_dao.get_by_key.return_value = _ok({"PRICE": 0.50})

    fry_size_dao = MagicMock()
    fry_size_dao.get_by_key.return_value = _ok({"PRICE": 0.25})

    fry_seasoning_dao = MagicMock()
    fry_seasoning_dao.get_by_key.return_value = _ok({"PRICE": 0.00})

    dao_map = {
        "CustomerDAO": customer_dao,
        "OrderDAO": order_dao,
        "OrderItemDAO": order_item_dao,
        "BurgerItemDAO": burger_item_dao,
        "BurgerItemToppingDAO": burger_topping_dao,
        "FryItemDAO": fry_item_dao,
        "BunTypeDAO": bun_dao,
        "PattyTypeDAO": patty_dao,
        "ToppingDAO": topping_dao,
        "FryTypeDAO": fry_type_dao,
        "FrySizeDAO": fry_size_dao,
        "FrySeasoningDAO": fry_seasoning_dao,
    }
    from contextlib import ExitStack
    from unittest.mock import patch as _patch

    class _Combined:
        """Combines the DAO patch and the get_db_cursor patch in one context manager."""
        def __enter__(self):
            self._stack = ExitStack()
            fake_cursor = MagicMock()
            mock_cm = MagicMock()
            mock_cm.__enter__ = MagicMock(return_value=fake_cursor)
            mock_cm.__exit__ = MagicMock(return_value=False)
            self._stack.enter_context(
                _patch("main.backend.server.get_db_cursor", return_value=mock_cm)
            )
            self._stack.enter_context(
                _patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n])
            )
            return self

        def __exit__(self, *args):
            return self._stack.__exit__(*args)

    return _Combined()


class TestCreateOrder:
    def _burger(self):
        return {"bun_id": 1, "patty_id": 1, "patty_count": 1, "topping_ids": [1]}

    def _fries(self):
        return {"size_id": 1, "type_id": 1, "seasoning_id": 1}

    def test_create_order_with_burger_returns_201_or_200(self):
        with _build_order_daos():
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code in (200, 201)

    def test_response_contains_order_id_and_total(self):
        with _build_order_daos():
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        body = response.json()
        assert "order_id" in body
        assert "total_price" in body

    def test_burger_price_calculated_as_bun_plus_patty_plus_topping(self):
        with _build_order_daos():
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        # bun=1.00, patty=3.00, topping=0.50 → 4.50
        assert response.json()["total_price"] == pytest.approx(4.50)

    def test_fries_price_calculated_correctly(self):
        with _build_order_daos():
            response = client.post("/Order/", json=_build_order_payload(fries=[self._fries()]))
        # type=0.50, size=0.25, seasoning=0.00 → 0.75
        assert response.json()["total_price"] == pytest.approx(0.75)

    def test_creates_new_customer_when_not_found(self):
        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _fail()
        customer_dao.create_record.return_value = _ok()

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([])
        order_dao.create_record.return_value = _ok()

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([])
        order_item_dao.create_record.return_value = _ok()

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([])
        burger_item_dao.create_record.return_value = _ok()

        burger_topping_dao = MagicMock()
        burger_topping_dao.create_record.return_value = _ok()

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([])

        bun_dao = MagicMock()
        bun_dao.get_by_key.return_value = _ok({"PRICE": 1.00})
        patty_dao = MagicMock()
        patty_dao.get_by_key.return_value = _ok({"PRICE": 3.00})
        topping_dao = MagicMock()
        topping_dao.get_by_key.return_value = _ok({"PRICE": 0.50})
        fry_type_dao = MagicMock()
        fry_size_dao = MagicMock()
        fry_seasoning_dao = MagicMock()

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": burger_topping_dao, "FryItemDAO": fry_item_dao,
            "BunTypeDAO": bun_dao, "PattyTypeDAO": patty_dao, "ToppingDAO": topping_dao,
            "FryTypeDAO": fry_type_dao, "FrySizeDAO": fry_size_dao, "FrySeasoningDAO": fry_seasoning_dao,
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code in (200, 201)
        customer_dao.create_record.assert_called_once()

    def test_returns_400_for_invalid_bun_id(self):
        bun_dao = MagicMock()
        bun_dao.get_by_key.return_value = _fail()

        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"})

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 5}])

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([{"ORDER_ITEM_ID": 3}])

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([{"BURGER_ID": 2}])

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([{"FRY_ID": 1}])

        patty_dao = MagicMock()
        topping_dao = MagicMock()
        fry_type_dao = MagicMock()
        fry_size_dao = MagicMock()
        fry_seasoning_dao = MagicMock()
        burger_topping_dao = MagicMock()

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": burger_topping_dao, "FryItemDAO": fry_item_dao,
            "BunTypeDAO": bun_dao, "PattyTypeDAO": patty_dao, "ToppingDAO": topping_dao,
            "FryTypeDAO": fry_type_dao, "FrySizeDAO": fry_size_dao, "FrySeasoningDAO": fry_seasoning_dao,
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 400

    def test_returns_400_for_invalid_fry_type_id(self):
        fry_type_dao = MagicMock()
        fry_type_dao.get_by_key.return_value = _fail()

        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"})

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 5}])

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([{"ORDER_ITEM_ID": 3}])

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([{"BURGER_ID": 2}])

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([{"FRY_ID": 1}])

        bun_dao = MagicMock()
        patty_dao = MagicMock()
        topping_dao = MagicMock()
        fry_size_dao = MagicMock()
        fry_seasoning_dao = MagicMock()
        burger_topping_dao = MagicMock()

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": burger_topping_dao, "FryItemDAO": fry_item_dao,
            "BunTypeDAO": bun_dao, "PattyTypeDAO": patty_dao, "ToppingDAO": topping_dao,
            "FryTypeDAO": fry_type_dao, "FrySizeDAO": fry_size_dao, "FrySeasoningDAO": fry_seasoning_dao,
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(fries=[self._fries()]))
        assert response.status_code == 400

    def test_returns_500_if_order_record_creation_fails(self):
        with _build_order_daos(order_create_ok=False):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 500

    def test_order_ids_start_at_one_when_table_empty(self):
        """When all tables are empty, the first IDs generated should be 1."""
        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"})

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([])
        order_dao.create_record.return_value = _ok()

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([])
        order_item_dao.create_record.return_value = _ok()

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([])
        burger_item_dao.create_record.return_value = _ok()

        burger_topping_dao = MagicMock()
        burger_topping_dao.create_record.return_value = _ok()

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([])

        bun_dao = MagicMock()
        bun_dao.get_by_key.return_value = _ok({"PRICE": 1.00})
        patty_dao = MagicMock()
        patty_dao.get_by_key.return_value = _ok({"PRICE": 3.00})
        topping_dao = MagicMock()
        topping_dao.get_by_key.return_value = _ok({"PRICE": 0.00})
        fry_type_dao = MagicMock()
        fry_size_dao = MagicMock()
        fry_seasoning_dao = MagicMock()

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": burger_topping_dao, "FryItemDAO": fry_item_dao,
            "BunTypeDAO": bun_dao, "PattyTypeDAO": patty_dao, "ToppingDAO": topping_dao,
            "FryTypeDAO": fry_type_dao, "FrySizeDAO": fry_size_dao, "FrySeasoningDAO": fry_seasoning_dao,
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code in (200, 201)
        assert response.json()["order_id"] == 1

    def test_returns_422_for_missing_customer_field(self):
        """FastAPI/Pydantic validation should reject a payload missing required fields."""
        payload = {"customer": {"email": "x@y.com"}, "burgers": [], "fries": []}
        response = client.post("/Order/", json=payload)
        assert response.status_code == 422

    def test_returns_500_if_customer_create_fails(self):
        """When customer doesn't exist and creation fails, expect 500."""
        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _fail()
        customer_dao.create_record.return_value = _fail()

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 1}])

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([])

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([])

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([])

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": MagicMock(), "FryItemDAO": fry_item_dao,
            "BunTypeDAO": MagicMock(), "PattyTypeDAO": MagicMock(), "ToppingDAO": MagicMock(),
            "FryTypeDAO": MagicMock(), "FrySizeDAO": MagicMock(), "FrySeasoningDAO": MagicMock(),
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload())
        assert response.status_code == 500

    def test_returns_400_for_invalid_patty_id(self):
        """When bun is valid but patty lookup fails, expect 400."""
        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"})

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 5}])

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([{"ORDER_ITEM_ID": 3}])

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([{"BURGER_ID": 2}])

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([{"FRY_ID": 1}])

        bun_dao = MagicMock()
        bun_dao.get_by_key.return_value = _ok({"PRICE": 1.00})

        patty_dao = MagicMock()
        patty_dao.get_by_key.return_value = _fail()  # patty fails

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": MagicMock(), "FryItemDAO": fry_item_dao,
            "BunTypeDAO": bun_dao, "PattyTypeDAO": patty_dao, "ToppingDAO": MagicMock(),
            "FryTypeDAO": MagicMock(), "FrySizeDAO": MagicMock(), "FrySeasoningDAO": MagicMock(),
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 400

    def test_returns_400_for_invalid_topping_id(self):
        """When bun and patty are valid but topping lookup fails, expect 400."""
        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"})

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 5}])

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([{"ORDER_ITEM_ID": 3}])

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([{"BURGER_ID": 2}])

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([{"FRY_ID": 1}])

        bun_dao = MagicMock()
        bun_dao.get_by_key.return_value = _ok({"PRICE": 1.00})

        patty_dao = MagicMock()
        patty_dao.get_by_key.return_value = _ok({"PRICE": 3.00})

        topping_dao = MagicMock()
        topping_dao.get_by_key.return_value = _fail()  # topping fails

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": MagicMock(), "FryItemDAO": fry_item_dao,
            "BunTypeDAO": bun_dao, "PattyTypeDAO": patty_dao, "ToppingDAO": topping_dao,
            "FryTypeDAO": MagicMock(), "FrySizeDAO": MagicMock(), "FrySeasoningDAO": MagicMock(),
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 400

    def test_returns_400_for_invalid_fry_size_id(self):
        """When fry type is valid but size lookup fails, expect 400."""
        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"})

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 5}])

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([{"ORDER_ITEM_ID": 3}])

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([{"BURGER_ID": 2}])

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([{"FRY_ID": 1}])

        fry_type_dao = MagicMock()
        fry_type_dao.get_by_key.return_value = _ok({"PRICE": 0.50})

        fry_size_dao = MagicMock()
        fry_size_dao.get_by_key.return_value = _fail()  # size fails

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": MagicMock(), "FryItemDAO": fry_item_dao,
            "BunTypeDAO": MagicMock(), "PattyTypeDAO": MagicMock(), "ToppingDAO": MagicMock(),
            "FryTypeDAO": fry_type_dao, "FrySizeDAO": fry_size_dao, "FrySeasoningDAO": MagicMock(),
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(fries=[self._fries()]))
        assert response.status_code == 400

    def test_returns_400_for_invalid_fry_seasoning_id(self):
        """When fry type and size are valid but seasoning lookup fails, expect 400."""
        customer_dao = MagicMock()
        customer_dao.get_by_key.return_value = _ok({"EMAIL": "testuser@example.com"})

        order_dao = MagicMock()
        order_dao.get_all_records.return_value = _ok([{"ORDER_ID": 5}])

        order_item_dao = MagicMock()
        order_item_dao.get_all_records.return_value = _ok([{"ORDER_ITEM_ID": 3}])

        burger_item_dao = MagicMock()
        burger_item_dao.get_all_records.return_value = _ok([{"BURGER_ID": 2}])

        fry_item_dao = MagicMock()
        fry_item_dao.get_all_records.return_value = _ok([{"FRY_ID": 1}])

        fry_type_dao = MagicMock()
        fry_type_dao.get_by_key.return_value = _ok({"PRICE": 0.50})

        fry_size_dao = MagicMock()
        fry_size_dao.get_by_key.return_value = _ok({"PRICE": 0.25})

        fry_seasoning_dao = MagicMock()
        fry_seasoning_dao.get_by_key.return_value = _fail()  # seasoning fails

        dao_map = {
            "CustomerDAO": customer_dao, "OrderDAO": order_dao,
            "OrderItemDAO": order_item_dao, "BurgerItemDAO": burger_item_dao,
            "BurgerItemToppingDAO": MagicMock(), "FryItemDAO": fry_item_dao,
            "BunTypeDAO": MagicMock(), "PattyTypeDAO": MagicMock(), "ToppingDAO": MagicMock(),
            "FryTypeDAO": fry_type_dao, "FrySizeDAO": fry_size_dao, "FrySeasoningDAO": fry_seasoning_dao,
        }
        with patch("main.backend.server.DAOFactory.get_or_create_dao", side_effect=lambda n: dao_map[n]):
            response = client.post("/Order/", json=_build_order_payload(fries=[self._fries()]))
        assert response.status_code == 400

    def test_returns_500_if_burger_order_item_creation_fails(self):
        with _build_order_daos(order_item_create_ok=False):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 500

    def test_returns_500_if_burger_item_creation_fails(self):
        with _build_order_daos(burger_create_ok=False):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 500

    def test_returns_500_if_burger_topping_creation_fails(self):
        with _build_order_daos(topping_create_ok=False):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 500

    def test_returns_500_if_fry_order_item_creation_fails(self):
        with _build_order_daos(order_item_create_ok=False):
            response = client.post("/Order/", json=_build_order_payload(fries=[self._fries()]))
        assert response.status_code == 500

    def test_returns_500_if_fry_item_creation_fails(self):
        with _build_order_daos(fry_create_ok=False):
            response = client.post("/Order/", json=_build_order_payload(fries=[self._fries()]))
        assert response.status_code == 500

    def test_returns_400_on_value_error_in_create_order(self):
        """When sanitize_and_unmarshal raises ValueError, expect 400."""
        with patch("main.backend.server.sanitize_and_unmarshal",
                   side_effect=ValueError("bad data")):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 400

    def test_returns_500_on_unhandled_exception_in_create_order(self):
        """When a generic Exception escapes the DAO calls, expect 500."""
        with patch("main.backend.server.DAOFactory.get_or_create_dao",
                   side_effect=RuntimeError("unexpected")):
            response = client.post("/Order/", json=_build_order_payload(burgers=[self._burger()]))
        assert response.status_code == 500


# ==================== Exception path tests for GET endpoints ====================

class TestGetEndpointExceptionPaths:
    def test_fries_endpoint_returns_500_on_dao_exception(self):
        with patch("main.backend.server.DAOFactory.get_or_create_dao",
                   side_effect=RuntimeError("db connection lost")):
            response = client.get("/Items/Fries")
        assert response.status_code == 500

    def test_burger_endpoint_returns_500_on_dao_exception(self):
        with patch("main.backend.server.DAOFactory.get_or_create_dao",
                   side_effect=RuntimeError("db connection lost")):
            response = client.get("/Items/Burger")
        assert response.status_code == 500

    def test_customer_endpoint_returns_500_on_general_exception(self):
        customer_dao = MagicMock()
        customer_dao.get_customer_with_orders.side_effect = RuntimeError("unexpected error")
        with patch("main.backend.server.DAOFactory.get_or_create_dao", return_value=customer_dao):
            response = client.get("/Customer/jane@example.com")
        assert response.status_code == 500


# ==================== Lifespan ====================

class TestLifespan:
    def test_lifespan_startup_and_shutdown(self):
        """Using TestClient as context manager exercises the lifespan events."""
        with TestClient(app) as c:
            response = c.get("/")
        assert response.status_code == 200


# ==================== Global exception handler ====================

class TestGlobalExceptionHandler:
    def test_global_handler_returns_500_json(self):
        """Add a transient test route to trigger the global exception handler."""
        from main.backend.server import app as _app
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/test-global-exc-internal-only")
        async def _raise():
            raise RuntimeError("deliberate test error")

        _app.include_router(router)
        with TestClient(_app, raise_server_exceptions=False) as c:
            response = c.get("/test-global-exc-internal-only")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}
