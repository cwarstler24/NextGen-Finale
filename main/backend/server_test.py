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
            LOGGER.info(f"Sample Size: {data['sizes'][0]}", also_print=True)
        if data.get('types'):
            LOGGER.info(f"Sample Type: {data['types'][0]}", also_print=True)
        if data.get('seasonings'):
            LOGGER.info(f"Sample Seasoning: {data['seasonings'][0]}",also_print=True)

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
            LOGGER.info(f"Sample Topping: {data['toppings'][0]}",also_print=True)

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
    LOGGER.info(f"  - Burgers: {len(order_data['burgers'])} (with {order_data['burgers'][0]['patty_count']} patties)", also_print=True)
    LOGGER.info(f"  - Fries: {len(order_data['fries'])}", also_print=True)

    response = client.post("/Order/", json=order_data)

    LOGGER.info(f"Status Code: {response.status_code}", also_print=True)

    if response.status_code == 200:
        data = response.json()
        LOGGER.info(f"Order ID: {data.get('order_id')}", also_print=True)
        LOGGER.info(f"Message: {data.get('message')}", also_print=True)
        LOGGER.info(f"Total Price: ${data.get('total_price',0):.2f}",also_print=True)

        assert "order_id" in data
        assert "total_price" in data
        assert data["total_price"] > 0

        LOGGER.info("[PASS] Order created successfully\n", also_print=True)
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
        test_create_order_invalid_ingredient
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
                f"[FAIL] TEST FAILED: {test.__name__}",
                also_print=True)
            LOGGER.error(f"   Error: {str(e)}\n", also_print=True)
        except Exception as e:
            failed += 1
            LOGGER.error(
                f"[FAIL] TEST ERROR: {test.__name__}",
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
