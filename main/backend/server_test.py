# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

"""
test_server.py

Test file for the FastAPI server endpoints.
Uses FastAPI's TestClient which doesn't require running the server separately.

To run this test file:
    python main/backend/test_server.py

No need to run server.py separately - TestClient handles that internally!
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from main.backend.server import app
from main.utilities.logger import LoggerFactory

# Initialize logger
LOGGER = LoggerFactory.get_general_logger()

# Create test client (no need to run server separately!)
client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint - health check"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST 1: Root Endpoint (Health Check)", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    response = client.get("/")

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)
    LOGGER.info(f"Response: {response.json()}", also_print=True)

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["status"] == "operational"

    LOGGER.info("[PASS] Root endpoint is operational\n", also_print=True)


def test_get_fries_items():
    """Test GET /Items/Fries endpoint"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST 2: GET /Items/Fries", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    response = client.get("/Items/Fries")

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)

    if response.status_code == 200:
        data = response.json()
        LOGGER.info(
            f"Fry Sizes: {len(data.get('sizes', []))}", also_print=True)
        LOGGER.info(
            f"Fry Types: {len(data.get('types', []))}", also_print=True)
        LOGGER.info(
            f"Fry Seasonings: {len(data.get('seasonings', []))}", also_print=True)

        # Show sample data
        if data.get('sizes'):
            sample_size = data['sizes'][0]
            LOGGER.info(f"Sample Size: {sample_size}", also_print=True)
            # Verify sizes have id, name, price but NOT stock_quantity
            assert "id" in sample_size or "FRY_SIZE_ID" in sample_size
            assert "name" in sample_size or "FRY_SIZE" in sample_size
            assert "price" in sample_size or "PRICE" in sample_size
            assert "quantity" not in sample_size and "STOCK_QUANTITY" not in sample_size, \
                "Fry sizes should not include stock_quantity"
        if data.get('types'):
            sample_type = data['types'][0]
            LOGGER.info(f"Sample Type: {sample_type}", also_print=True)
            # Verify types have stock quantity
            assert "quantity" in sample_type or "STOCK_QUANTITY" in sample_type
        if data.get('seasonings'):
            sample_seasoning = data['seasonings'][0]
            LOGGER.info(
                f"Sample Seasoning: {sample_seasoning}",
                also_print=True)
            # Verify seasonings have stock quantity
            assert "quantity" in sample_seasoning or "STOCK_QUANTITY" in sample_seasoning

        assert "sizes" in data
        assert "types" in data
        assert "seasonings" in data

        LOGGER.info("[PASS] Fries endpoint returned data\n", also_print=True)
    else:
        LOGGER.error(f"[FAIL] {response.json()}", also_print=True)


def test_get_burger_items():
    """Test GET /Items/Burger endpoint"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST 3: GET /Items/Burger", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    response = client.get("/Items/Burger")

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)

    if response.status_code == 200:
        data = response.json()
        LOGGER.info(f"Buns: {len(data.get('buns', []))}", also_print=True)
        LOGGER.info(
            f"Patties: {len(data.get('patties', []))}", also_print=True)
        LOGGER.info(
            f"Toppings: {len(data.get('toppings', []))}", also_print=True)

        # Show sample data
        if data.get('buns'):
            LOGGER.info(f"Sample Bun: {data['buns'][0]}", also_print=True)
        if data.get('patties'):
            LOGGER.info(f"Sample Patty: {data['patties'][0]}", also_print=True)
        if data.get('toppings'):
            LOGGER.info(
                f"Sample Topping: {
                    data['toppings'][0]}",
                also_print=True)

        assert "buns" in data
        assert "patties" in data
        assert "toppings" in data

        LOGGER.info("[PASS] Burger endpoint returned data\n", also_print=True)
    else:
        LOGGER.error(f"[FAIL] {response.json()}", also_print=True)


def test_get_customer_not_found():
    """Test GET /Customer/{email} with non-existent customer"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST 4: GET /Customer/{email} - Not Found", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    test_email = "nonexistent@test.com"
    response = client.get(f"/Customer/{test_email}")

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)
    LOGGER.info(f"Response: {response.json()}", also_print=True)

    # Should return 404 for non-existent customer
    assert response.status_code == 404

    LOGGER.info(
        "[PASS] Returns 404 for non-existent customer\n",
        also_print=True)


def test_get_customer_found():
    """Test GET /Customer/{email} with existing customer (if data exists)"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info(
        "TEST 5: GET /Customer/{email} - Found (if exists)",
        also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    # This test will pass if a customer exists in the database
    # Try a common test email
    test_email = "test@example.com"
    response = client.get(f"/Customer/{test_email}")

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)

    if response.status_code == 200:
        data = response.json()
        LOGGER.info(f"Customer Name: {data.get('name')}", also_print=True)
        LOGGER.info(f"Customer Email: {data.get('email')}", also_print=True)
        LOGGER.info(
            f"Number of Orders: {len(data.get('orders', []))}", also_print=True)

        assert "name" in data
        assert "email" in data
        assert "orders" in data

        # Check order structure if orders exist
        if data.get('orders'):
            first_order = data['orders'][0]
            assert "order_id" in first_order, "Order should have order_id"
            assert "date" in first_order, "Order should have date"
            assert "price" in first_order, "Order should have price"
            assert "items" in first_order, "Order should have items list"

            # Check item structure if items exist
            if first_order.get('items'):
                first_item = first_order['items'][0]
                assert "item_type" in first_item, "Item should have item_type"
                assert "name" in first_item, "Item should have name"
                assert "price" in first_item, "Item should have price"
                LOGGER.info(
                    f"Sample Order Item: {
                        first_item['name']}",
                    also_print=True)

        LOGGER.info(
            "[PASS] Customer endpoint returned data\n",
            also_print=True)
    else:
        LOGGER.info(
            f"[INFO] SKIPPED: No customer found with email {test_email}\n",
            also_print=True)


def test_create_order():
    """Test POST /Order/ endpoint"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST 6: POST /Order/ - Create Order", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    # First, get available items to use valid IDs
    fries_response = client.get("/Items/Fries")
    burger_response = client.get("/Items/Burger")

    if fries_response.status_code != 200 or burger_response.status_code != 200:
        LOGGER.error(
            "[FAIL] Cannot get ingredient data for order test\n",
            also_print=True)
        return

    fries_data = fries_response.json()
    burger_data = burger_response.json()

    # Check if we have ingredients
    if (not burger_data.get('buns') or not burger_data.get('patties') or
        not fries_data.get('sizes') or not fries_data.get('types') or
            not fries_data.get('seasonings')):
        LOGGER.error(
            "[FAIL] Not enough ingredient data in database\n",
            also_print=True)
        return

    # Capture initial stock quantities
    initial_bun_stock = burger_data['buns'][0].get('quantity', 0)
    initial_patty_stock = burger_data['patties'][0].get('quantity', 0)
    initial_topping_stock = burger_data['toppings'][0].get(
        'quantity', 0) if burger_data.get('toppings') else 0
    initial_fry_type_stock = fries_data['types'][0].get('quantity', 0)
    initial_fry_seasoning_stock = fries_data['seasonings'][0].get(
        'quantity', 0)
    fry_size_value = fries_data['sizes'][0].get(
        'name', fries_data['sizes'][0].get('FRY_SIZE', 0))

    # Extract numeric size value (e.g., "8 oz" -> 8)
    if isinstance(fry_size_value, str):
        fry_size_value = int(''.join(filter(str.isdigit, fry_size_value)))

    LOGGER.info("Initial Stock Quantities:", also_print=True)
    LOGGER.info(f"  - Bun: {initial_bun_stock}", also_print=True)
    LOGGER.info(f"  - Patty: {initial_patty_stock}", also_print=True)
    LOGGER.info(f"  - Topping: {initial_topping_stock}", also_print=True)
    LOGGER.info(f"  - Fry Type: {initial_fry_type_stock}", also_print=True)
    LOGGER.info(
        f"  - Fry Seasoning: {initial_fry_seasoning_stock}",
        also_print=True)
    LOGGER.info(f"  - Fry Size Multiplier: {fry_size_value}", also_print=True)

    # Create test order with valid IDs
    order_data = {
        "customer": {
            "name": "Test Customer",
            "email": "testorder@example.com",
            "shipping_address": "123 Test St",
            "billing_address": "123 Test St"},
        "burgers": [
            {
                "bun_id": burger_data['buns'][0]['id'],
                "patty_id": burger_data['patties'][0]['id'],
                "patty_count": 2,
                "topping_ids": [
                    burger_data['toppings'][0]['id']] if burger_data.get('toppings') else []}],
        "fries": [
            {
                "size_id": fries_data['sizes'][0]['id'],
                "type_id": fries_data['types'][0]['id'],
                "seasoning_id": fries_data['seasonings'][0]['id']}],
        "date": datetime.now().isoformat()}

    LOGGER.info("Creating order with:", also_print=True)
    LOGGER.info(
        f"  - Customer: {order_data['customer']['email']}", also_print=True)
    LOGGER.info(
        f"  - Burgers: {
            len(
                order_data['burgers'])} (with {
            order_data['burgers'][0]['patty_count']} patties)",
        also_print=True)
    LOGGER.info(f"  - Fries: {len(order_data['fries'])}", also_print=True)

    response = client.post("/Order/", json=order_data)

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)

    if response.status_code == 200:
        data = response.json()
        LOGGER.info(f"Order ID: {data.get('order_id')}", also_print=True)
        LOGGER.info(f"Message: {data.get('message')}", also_print=True)
        LOGGER.info(
            f"Total Price: ${
                data.get(
                    'total_price',
                    0):.2f}",
            also_print=True)

        assert "order_id" in data
        assert "total_price" in data
        assert data["total_price"] > 0

        # Get stock quantities AFTER order to verify decrementation
        fries_response_after = client.get("/Items/Fries")
        burger_response_after = client.get("/Items/Burger")

        if fries_response_after.status_code == 200 and burger_response_after.status_code == 200:
            fries_data_after = fries_response_after.json()
            burger_data_after = burger_response_after.json()

            final_bun_stock = burger_data_after['buns'][0].get('quantity', 0)
            final_patty_stock = burger_data_after['patties'][0].get(
                'quantity', 0)
            final_topping_stock = burger_data_after['toppings'][0].get(
                'quantity', 0) if burger_data_after.get('toppings') else 0
            final_fry_type_stock = fries_data_after['types'][0].get(
                'quantity', 0)
            final_fry_seasoning_stock = fries_data_after['seasonings'][0].get(
                'quantity', 0)

            LOGGER.info("\nFinal Stock Quantities:", also_print=True)
            LOGGER.info(f"  - Bun: {final_bun_stock}", also_print=True)
            LOGGER.info(f"  - Patty: {final_patty_stock}", also_print=True)
            LOGGER.info(f"  - Topping: {final_topping_stock}", also_print=True)
            LOGGER.info(
                f"  - Fry Type: {final_fry_type_stock}",
                also_print=True)
            LOGGER.info(
                f"  - Fry Seasoning: {final_fry_seasoning_stock}",
                also_print=True)

            # Verify decrementation
            LOGGER.info("\nStock Changes:", also_print=True)
            bun_change = initial_bun_stock - final_bun_stock
            patty_change = initial_patty_stock - final_patty_stock
            topping_change = initial_topping_stock - final_topping_stock
            fry_type_change = initial_fry_type_stock - final_fry_type_stock
            fry_seasoning_change = initial_fry_seasoning_stock - final_fry_seasoning_stock

            LOGGER.info(
                f"  - Bun: -{bun_change} (expected -1)",
                also_print=True)
            LOGGER.info(
                f"  - Patty: -{patty_change} (expected -2)",
                also_print=True)
            LOGGER.info(
                f"  - Topping: -{topping_change} (expected -1)",
                also_print=True)
            LOGGER.info(
                f"  - Fry Type: -{fry_type_change} (expected -{fry_size_value})",
                also_print=True)
            LOGGER.info(
                f"  - Fry Seasoning: -{fry_seasoning_change} (expected -{fry_size_value})",
                also_print=True)

            # Assert correct decrementation
            assert bun_change == 1, f"Bun stock should decrease by 1, but decreased by {bun_change}"
            assert patty_change == 2, f"Patty stock should decrease by 2 (patty_count), but decreased by {patty_change}"
            if burger_data.get('toppings'):
                assert topping_change == 1, f"Topping stock should decrease by 1, but decreased by {topping_change}"
            assert fry_type_change == fry_size_value, f"Fry type stock should decrease by {fry_size_value} (fry size), but decreased by {fry_type_change}"
            assert fry_seasoning_change == fry_size_value, f"Fry seasoning stock should decrease by {fry_size_value} (fry size), but decreased by {fry_seasoning_change}"

            LOGGER.info(
                "\n[PASS] Order created successfully and inventory decremented correctly\n",
                also_print=True)
        else:
            LOGGER.info(
                "\n[PASS] Order created successfully (could not verify decrementation)\n",
                also_print=True)
    else:
        LOGGER.error(f"[FAIL] {response.json()}\n", also_print=True)


def test_create_order_invalid_ingredient():
    """Test POST /Order/ with invalid ingredient ID"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST 7: POST /Order/ - Invalid Ingredient", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    # Create order with invalid ingredient IDs
    order_data = {
        "customer": {
            "name": "Test Customer",
            "email": "testorder2@example.com",
            "shipping_address": "123 Test St",
            "billing_address": "123 Test St"
        },
        "burgers": [
            {
                "bun_id": 99999,  # Invalid ID
                "patty_id": 99999,  # Invalid ID
                "patty_count": 1,
                "topping_ids": []
            }
        ],
        "fries": []
    }

    response = client.post("/Order/", json=order_data)

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)
    LOGGER.info(f"Response: {response.json()}", also_print=True)

    # Should return 400 for invalid ingredient
    assert response.status_code == 400

    LOGGER.info("[PASS] Returns 400 for invalid ingredient\n", also_print=True)


def test_insufficient_inventory():
    """Test POST /Order/ with insufficient inventory"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info(
        "TEST 8: POST /Order/ - Insufficient Inventory",
        also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    # Get available items
    burger_response = client.get("/Items/Burger")
    if burger_response.status_code != 200:
        LOGGER.info(
            "[INFO] SKIPPED: Cannot get ingredient data\n",
            also_print=True)
        return

    burger_data = burger_response.json()
    if not burger_data.get('patties'):
        LOGGER.info(
            "[INFO] SKIPPED: No patty data available\n",
            also_print=True)
        return

    # Try to order more patties than available
    patty = burger_data['patties'][0]
    available_stock = patty.get('quantity', 0)

    if available_stock < 1:
        LOGGER.info(
            "[INFO] SKIPPED: No patty stock available\n",
            also_print=True)
        return

    order_data = {
        "customer": {
            "name": "Test Customer",
            "email": "testorder3@example.com",
            "shipping_address": "123 Test St",
            "billing_address": "123 Test St"
        },
        "burgers": [
            {
                "bun_id": burger_data['buns'][0]['id'],
                "patty_id": patty['id'],
                "patty_count": available_stock + 100,  # More than available
                "topping_ids": []
            }
        ],
        "fries": []
    }

    response = client.post("/Order/", json=order_data)

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)
    LOGGER.info(f"Response: {response.json()}", also_print=True)

    # Should return 400 for insufficient stock
    assert response.status_code == 400
    assert "Insufficient stock" in response.json().get('detail', '')

    LOGGER.info(
        "[PASS] Returns 400 for insufficient inventory\n",
        also_print=True)


def test_order_history_with_toppings():
    """Test that order history includes topping details"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info(
        "TEST 9: GET /Customer/{email} - Order History with Toppings",
        also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    # Use the testorder@example.com created in test_create_order
    test_email = "testorder@example.com"
    response = client.get(f"/Customer/{test_email}")

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)

    if response.status_code == 200:
        data = response.json()
        orders = data.get('orders', [])

        if orders:
            LOGGER.info(f"Found {len(orders)} order(s)", also_print=True)

            # Check first order
            first_order = orders[0]
            LOGGER.info(
                f"Order ID: {
                    first_order.get('order_id')}",
                also_print=True)
            LOGGER.info(
                f"Order Date: {
                    first_order.get('date')}",
                also_print=True)
            LOGGER.info(
                f"Order Price: ${
                    first_order.get(
                        'price',
                        0):.2f}",
                also_print=True)

            items = first_order.get('items', [])
            LOGGER.info(f"Order Items: {len(items)}", also_print=True)

            for item in items:
                LOGGER.info(
                    f"  - {item['item_type']}: {item['name']} (${item['price']:.2f})", also_print=True)

            # Verify structure
            assert 'order_id' in first_order
            assert 'items' in first_order
            assert len(items) > 0

            # Check for burger with toppings (if created in test 6)
            burger_items = [
                item for item in items if item['item_type'] == 'Burger']
            if burger_items and 'topping' not in burger_items[0]['name'].lower(
            ):
                LOGGER.info(
                    "[INFO] Burger item found but no toppings in name (may not have been ordered with toppings)",
                    also_print=True)

            LOGGER.info(
                "[PASS] Order history includes detailed items\n",
                also_print=True)
        else:
            LOGGER.info(
                "[INFO] No orders found for test customer\n",
                also_print=True)
    else:
        LOGGER.info(
            f"[INFO] SKIPPED: Customer not found (status {
                response.status_code})\n",
            also_print=True)


def run_all_tests():
    """Run all test functions"""
    LOGGER.info("\n" + "=" * 60, also_print=True)
    LOGGER.info("STARTING SERVER ENDPOINT TESTS", also_print=True)
    LOGGER.info("=" * 60 + "\n", also_print=True)

    tests = [
        test_root_endpoint,
        test_get_fries_items,
        test_get_burger_items,
        test_get_customer_not_found,
        test_get_customer_found,
        test_create_order,
        test_create_order_invalid_ingredient,
        test_insufficient_inventory,
        test_order_history_with_toppings
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            LOGGER.error(
                f"[FAIL] TEST FAILED: {
                    test.__name__}",
                also_print=True)
            LOGGER.error(f"   Error: {str(e)}\n", also_print=True)
        except Exception as e:
            failed += 1
            LOGGER.error(
                f"[FAIL] TEST ERROR: {
                    test.__name__}",
                also_print=True)
            LOGGER.error(f"   Exception: {str(e)}\n", also_print=True)

    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST SUMMARY", also_print=True)
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info(f"Total Tests: {passed + failed}", also_print=True)
    LOGGER.info(f"[PASS] Passed: {passed}", also_print=True)
    LOGGER.info(f"[FAIL] Failed: {failed}", also_print=True)
    LOGGER.info("=" * 60 + "\n", also_print=True)


if __name__ == "__main__":
    run_all_tests()
