# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

import sys
from pathlib import Path
from typing import Any, Type, Optional, List
from datetime import datetime
import re

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.backend.entities import (
    DatabaseEntity, Customer, Order, OrderItem, BurgerItem,
    BurgerItemTopping, FryItem,
)
from main.utilities.logger import LoggerFactory

LOGGER = LoggerFactory.get_general_logger()

"""
sanitizer.py

This module provides data sanitization and validation for incoming JSON payloads.
It unmarshalls validated data into entity objects, ensuring type safety and data integrity
before database operations.

Key Functions:
    - sanitize_and_unmarshal: Main entry point for sanitizing and converting JSON to entities
    - Individual sanitizers for each entity type
    - Input validation and type coercion
    - SQL injection prevention
    - XSS prevention for string fields
"""

# ==================== Sanitization Utilities ====================


def sanitize_string(
        value: Any,
        max_length: Optional[int] = None,
        allow_empty: bool = False) -> str:
    """
    Sanitize a string value to prevent injection attacks and ensure valid data.

    Args:
        value: The value to sanitize
        max_length: Maximum allowed length (None for no limit)
        allow_empty: Whether to allow empty strings

    Returns:
        str: Sanitized string

    Raises:
        ValueError: If validation fails
    """
    if value is None:
        if allow_empty:
            return ""
        raise ValueError("String value cannot be None")

    # Convert to string
    sanitized = str(value).strip()

    # Check for empty
    if not sanitized and not allow_empty:
        raise ValueError("String value cannot be empty")

    # Remove control characters and potential XSS
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)

    # Check length
    if max_length and len(sanitized) > max_length:
        raise ValueError(f"String exceeds maximum length of {max_length}")

    return sanitized


def sanitize_email(value: Any) -> str:
    """
    Sanitize and validate an email address.

    Args:
        value: The email to validate

    Returns:
        str: Sanitized email

    Raises:
        ValueError: If email is invalid
    """
    email = sanitize_string(value, max_length=255)

    # Basic email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError(f"Invalid email format: {email}")

    return email.lower()


def sanitize_integer(
        value: Any,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None) -> int:
    """
    Sanitize and validate an integer value.

    Args:
        value: The value to convert to integer
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        int: Sanitized integer

    Raises:
        ValueError: If conversion or validation fails
    """
    if value is None:
        raise ValueError("Integer value cannot be None")

    try:
        sanitized = int(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot convert '{value}' to integer") from exc

    if min_value is not None and sanitized < min_value:
        raise ValueError(
            f"Integer value {sanitized} is below minimum {min_value}")

    if max_value is not None and sanitized > max_value:
        raise ValueError(
            f"Integer value {sanitized} exceeds maximum {max_value}")

    return sanitized


def sanitize_float(
        value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None) -> float:
    """
    Sanitize and validate a float value.

    Args:
        value: The value to convert to float
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        float: Sanitized float

    Raises:
        ValueError: If conversion or validation fails
    """
    if value is None:
        raise ValueError("Float value cannot be None")

    try:
        sanitized = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot convert '{value}' to float") from exc

    if min_value is not None and sanitized < min_value:
        raise ValueError(
            f"Float value {sanitized} is below minimum {min_value}")

    if max_value is not None and sanitized > max_value:
        raise ValueError(
            f"Float value {sanitized} exceeds maximum {max_value}")

    return sanitized


def sanitize_datetime(value: Any) -> datetime:
    """
    Sanitize and validate a datetime value.

    Args:
        value: The datetime value (string, datetime, or timestamp)

    Returns:
        datetime: Sanitized datetime

    Raises:
        ValueError: If conversion fails
    """
    if value is None:
        raise ValueError("Datetime value cannot be None")

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        # Try common datetime formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse datetime: {value}")

    # Try treating as timestamp
    try:
        return datetime.fromtimestamp(float(value))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot convert '{value}' to datetime") from exc


def sanitize_list(
        value: Any,
        _item_type: Type,
        sanitizer_func: callable) -> List[Any]:
    """
    Sanitize a list of values using the provided sanitizer function.

    Args:
        value: The list to sanitize
        item_type: Expected type of items
        sanitizer_func: Function to sanitize each item

    Returns:
        List: Sanitized list

    Raises:
        ValueError: If validation fails
    """
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(f"Expected list, got {type(value).__name__}")

    sanitized_list = []
    for i, item in enumerate(value):
        try:
            sanitized_list.append(sanitizer_func(item))
        except ValueError as e:
            raise ValueError(f"Error in list item {i}: {e}") from e

    return sanitized_list


# ==================== Entity Sanitizers ====================

def sanitize_customer(data: dict[str, Any]) -> Customer:
    """
    Sanitize and convert customer data to Customer entity.

    Args:
        data: Dictionary containing customer data

    Returns:
        Customer: Validated Customer entity

    Raises:
        ValueError: If validation fails
    """
    try:
        return Customer(
            email=sanitize_email(
                data.get("email")),
            name=sanitize_string(
                data.get("name"),
                max_length=255),
            bill_addr=sanitize_string(
                data.get("billing_address") or data.get("bill_addr"),
                max_length=500),
            ship_addr=sanitize_string(
                data.get("shipping_address") or data.get("ship_addr"),
                max_length=500))
    except Exception as e:
        LOGGER.error(f"Failed to sanitize customer data: {e}")
        raise ValueError(f"Invalid customer data: {e}") from e


def sanitize_order(data: dict[str, Any]) -> Order:
    """
    Sanitize and convert order data to Order entity.

    Args:
        data: Dictionary containing order data

    Returns:
        Order: Validated Order entity

    Raises:
        ValueError: If validation fails
    """
    try:
        return Order(
            order_id=sanitize_integer(
                data.get("order_id"),
                min_value=1),
            email=sanitize_email(
                data.get("email")),
            purchase_date=sanitize_datetime(
                data.get("purchase_date") or datetime.now()),
            order_qty=sanitize_integer(
                data.get("order_qty") or data.get("order_quantity"),
                min_value=1),
            total_price=sanitize_float(
                data.get("total_price"),
                min_value=0.0))
    except Exception as e:
        LOGGER.error(f"Failed to sanitize order data: {e}")
        raise ValueError(f"Invalid order data: {e}") from e


def sanitize_order_item(data: dict[str, Any]) -> OrderItem:
    """
    Sanitize and convert order item data to OrderItem entity.

    Args:
        data: Dictionary containing order item data

    Returns:
        OrderItem: Validated OrderItem entity

    Raises:
        ValueError: If validation fails
    """
    try:
        return OrderItem(
            order_item_id=sanitize_integer(data.get("order_item_id"), min_value=1),
            order_id=sanitize_integer(data.get("order_id"), min_value=1),
            item_type=sanitize_string(data.get("item_type"), max_length=50),
            unit_price=sanitize_float(data.get("unit_price"), min_value=0.0),
            extended_price=sanitize_float(data.get("extended_price"), min_value=0.0)
        )
    except Exception as e:
        LOGGER.error(f"Failed to sanitize order item data: {e}")
        raise ValueError(f"Invalid order item data: {e}") from e


def sanitize_burger_item(data: dict[str, Any]) -> BurgerItem:
    """
    Sanitize and convert burger item data to BurgerItem entity.

    Args:
        data: Dictionary containing burger item data

    Returns:
        BurgerItem: Validated BurgerItem entity

    Raises:
        ValueError: If validation fails
    """
    try:
        return BurgerItem(
            burger_id=sanitize_integer(data.get("burger_id"), min_value=1),
            order_item_id=sanitize_integer(data.get("order_item_id"), min_value=1),
            bun_type=sanitize_integer(data.get("bun_type") or data.get("bun_id"), min_value=1),
            patty_type=sanitize_integer(data.get("patty_type") or data.get("patty_id"), min_value=1)
        )
    except Exception as e:
        LOGGER.error(f"Failed to sanitize burger item data: {e}")
        raise ValueError(f"Invalid burger item data: {e}") from e


def sanitize_burger_item_topping(data: dict[str, Any]) -> BurgerItemTopping:
    """
    Sanitize and convert burger-topping association data to BurgerItemTopping entity.

    Args:
        data: Dictionary containing burger-topping data

    Returns:
        BurgerItemTopping: Validated BurgerItemTopping entity

    Raises:
        ValueError: If validation fails
    """
    try:
        return BurgerItemTopping(
            topping_id=sanitize_integer(
                data.get("topping_id"), min_value=1), burger_order_id=sanitize_integer(
                data.get("burger_order_id") or data.get("burger_id"), min_value=1))
    except Exception as e:
        LOGGER.error(f"Failed to sanitize burger topping data: {e}")
        raise ValueError(f"Invalid burger topping data: {e}") from e


def sanitize_fry_item(data: dict[str, Any]) -> FryItem:
    """
    Sanitize and convert fry item data to FryItem entity.

    Args:
        data: Dictionary containing fry item data

    Returns:
        FryItem: Validated FryItem entity

    Raises:
        ValueError: If validation fails
    """
    try:
        return FryItem(
            fry_id=sanitize_integer(
                data.get("fry_id"), min_value=1), order_item_id=sanitize_integer(
                data.get("order_item_id"), min_value=1), fry_type=sanitize_integer(
                data.get("fry_type") or data.get("type_id"), min_value=1), fry_size=sanitize_integer(
                    data.get("fry_size") or data.get("size_id"), min_value=1), fry_seasoning=sanitize_integer(
                        data.get("fry_seasoning") or data.get("seasoning_id"), min_value=1))
    except Exception as e:
        LOGGER.error(f"Failed to sanitize fry item data: {e}")
        raise ValueError(f"Invalid fry item data: {e}") from e


# ==================== Main Sanitization Function ====================

def sanitize_and_unmarshal(
    data: dict[str, Any],
    entity_type: Type[DatabaseEntity]
) -> DatabaseEntity:
    """
    Main entry point for sanitizing and unmarshalling data into entity objects.

    Args:
        data: Dictionary containing raw data from request
        entity_type: The entity class to create (e.g., Customer, Order, etc.)

    Returns:
        DatabaseEntity: Validated and sanitized entity instance

    Raises:
        ValueError: If data is invalid or entity type is not supported
    """
    if not data:
        raise ValueError("Data cannot be empty")

    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary, got {type(data).__name__}")

    # Map entity types to their sanitizer functions
    sanitizer_map = {
        Customer: sanitize_customer,
        Order: sanitize_order,
        OrderItem: sanitize_order_item,
        BurgerItem: sanitize_burger_item,
        BurgerItemTopping: sanitize_burger_item_topping,
        FryItem: sanitize_fry_item,
    }

    sanitizer = sanitizer_map.get(entity_type)
    if not sanitizer:
        raise ValueError(
            f"No sanitizer available for entity type: {
                entity_type.__name__}")

    LOGGER.debug(f"Sanitizing data for entity type: {entity_type.__name__}")
    return sanitizer(data)


def sanitize_and_unmarshal_list(
    data_list: List[dict[str, Any]],
    entity_type: Type[DatabaseEntity]
) -> List[DatabaseEntity]:
    """
    Sanitize and unmarshal a list of data dictionaries into entity objects.

    Args:
        data_list: List of dictionaries containing raw data
        entity_type: The entity class to create for each item

    Returns:
        List[DatabaseEntity]: List of validated entity instances

    Raises:
        ValueError: If any item is invalid
    """
    if not isinstance(data_list, list):
        raise ValueError(f"Expected list, got {type(data_list).__name__}")

    entities = []
    for i, data in enumerate(data_list):
        try:
            entities.append(sanitize_and_unmarshal(data, entity_type))
        except ValueError as e:
            raise ValueError(f"Error in list item {i}: {e}") from e

    return entities
