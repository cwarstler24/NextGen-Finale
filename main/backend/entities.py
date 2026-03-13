# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime
from decimal import Decimal

"""
entities.py

This module defines entity classes that represent database tables as Python objects.
Each entity corresponds to a table in the DB2 database and provides an object-oriented
interface for working with database records.

Hierarchy:
    DatabaseEntity (ABC) - Abstract base class
        ├── Customer
        ├── Order
        ├── OrderItem
        ├── BurgerItem
        ├── BurgerItemTopping
        ├── FryItem
        ├── BunType
        ├── PattyType
        ├── Topping
        ├── FryType
        ├── FrySize
        └── FrySeasoning
"""

# ==================== Abstract Base Entity ====================


class DatabaseEntity(ABC):
    """
    Abstract base class for all database entities.
    Provides common functionality for converting between database rows and objects.
    """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the entity to a dictionary representation.

        Returns:
            dict[str, Any]: Dictionary containing all entity fields
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DatabaseEntity':
        """
        Create an entity instance from a dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing entity data

        Returns:
            DatabaseEntity: New instance of the entity
        """
        pass

    @abstractmethod
    def get_primary_key(self) -> Any:
        """
        Get the primary key value of this entity.

        Returns:
            Any: The primary key value
        """
        pass

    def __repr__(self) -> str:
        """String representation of the entity"""
        return f"{self.__class__.__name__}({self.to_dict()})"


# ==================== Customer Entity ====================

class Customer(DatabaseEntity):
    """
    Entity representing a customer in the CUSTOMER table.
    Primary Key: EMAIL
    """

    def __init__(
        self,
        email: str,
        name: str,
        bill_addr: str,
        ship_addr: str
    ):
        self.email = email
        self.name = name
        self.bill_addr = bill_addr
        self.ship_addr = ship_addr

    def to_dict(self) -> dict[str, Any]:
        return {
            "EMAIL": self.email,
            "NAME": self.name,
            "BILL_ADDR": self.bill_addr,
            "SHIP_ADDR": self.ship_addr
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Customer':
        return cls(
            email=data.get("EMAIL"),
            name=data.get("NAME"),
            bill_addr=data.get("BILL_ADDR"),
            ship_addr=data.get("SHIP_ADDR")
        )

    def get_primary_key(self) -> str:
        return self.email


# ==================== Order Entity ====================

class Order(DatabaseEntity):
    """
    Entity representing an order in the ORDERS table.
    Primary Key: ORDER_ID
    """

    def __init__(
        self,
        order_id: int,
        email: str,
        purchase_date: datetime,
        order_qty: int,
        total_price: float
    ):
        self.order_id = order_id
        self.email = email
        self.purchase_date = purchase_date
        self.order_qty = order_qty
        self.total_price = total_price

    def to_dict(self) -> dict[str, Any]:
        return {
            "ORDER_ID": self.order_id,
            "EMAIL": self.email,
            "PURCHASE_DATE": self.purchase_date,
            "ORDER_QTY": self.order_qty,
            "TOTAL_PRICE": self.total_price
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Order':
        return cls(
            order_id=data.get("ORDER_ID"),
            email=data.get("EMAIL"),
            purchase_date=data.get("PURCHASE_DATE"),
            order_qty=data.get("ORDER_QTY"),
            total_price=data.get("TOTAL_PRICE")
        )

    def get_primary_key(self) -> int:
        return self.order_id


# ==================== OrderItem Entity ====================

class OrderItem(DatabaseEntity):
    """
    Entity representing an order item in the ORDER_ITEMS table.
    Primary Key: ORDER_ITEM_ID
    """

    def __init__(
        self,
        order_item_id: int,
        order_id: int,
        item_type: str,
        unit_price: float,
    ):
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.item_type = item_type
        self.unit_price = unit_price

    def to_dict(self) -> dict[str, Any]:
        return {
            "ORDER_ITEM_ID": self.order_item_id,
            "ORDER_ID": self.order_id,
            "ITEM_TYPE": self.item_type,
            "UNIT_PRICE": self.unit_price,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'OrderItem':
        return cls(
            order_item_id=data.get("ORDER_ITEM_ID"),
            order_id=data.get("ORDER_ID"),
            item_type=data.get("ITEM_TYPE"),
            unit_price=data.get("UNIT_PRICE"),
        )

    def get_primary_key(self) -> int:
        return self.order_item_id


# ==================== BurgerItem Entity ====================

class BurgerItem(DatabaseEntity):
    """
    Entity representing a burger item in the BURGER_ITEMS table.
    Primary Key: BURGER_ID
    """

    def __init__(
        self,
        burger_id: int,
        order_item_id: int,
        bun_type: int,
        patty_type: int,
        patty_count: int = 1
    ):
        self.burger_id = burger_id
        self.order_item_id = order_item_id
        self.bun_type = bun_type
        self.patty_type = patty_type
        self.patty_count = patty_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "BURGER_ID": self.burger_id,
            "ORDER_ITEM_ID": self.order_item_id,
            "BUN_TYPE": self.bun_type,
            "PATTY_TYPE": self.patty_type,
            "PATTY_COUNT": self.patty_count
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BurgerItem':
        return cls(
            burger_id=data.get("BURGER_ID"),
            order_item_id=data.get("ORDER_ITEM_ID"),
            bun_type=data.get("BUN_TYPE"),
            patty_type=data.get("PATTY_TYPE"),
            patty_count=data.get("PATTY_COUNT", 1)
        )

    def get_primary_key(self) -> int:
        return self.burger_id


# ==================== BurgerItemTopping Entity ====================

class BurgerItemTopping(DatabaseEntity):
    """
    Entity representing a burger-topping association in the BURGER_ITEM_TOPPINGS table.
    Composite Key: (TOPPING_ID, BURGER_ORDER_ID)
    """

    def __init__(
        self,
        topping_id: int,
        burger_order_id: int
    ):
        self.topping_id = topping_id
        self.burger_order_id = burger_order_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "TOPPING_ID": self.topping_id,
            "BURGER_ORDER_ID": self.burger_order_id
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BurgerItemTopping':
        return cls(
            topping_id=data.get("TOPPING_ID"),
            burger_order_id=data.get("BURGER_ORDER_ID")
        )

    def get_primary_key(self) -> tuple[int, int]:
        """Returns composite key as tuple"""
        return (self.topping_id, self.burger_order_id)


# ==================== FryItem Entity ====================

class FryItem(DatabaseEntity):
    """
    Entity representing a fry item in the FRY_ITEMS table.
    Primary Key: FRY_ID
    """

    def __init__(
        self,
        fry_id: int,
        order_item_id: int,
        fry_type: int,
        fry_size: int,
        fry_seasoning: int
    ):
        self.fry_id = fry_id
        self.order_item_id = order_item_id
        self.fry_type = fry_type
        self.fry_size = fry_size
        self.fry_seasoning = fry_seasoning

    def to_dict(self) -> dict[str, Any]:
        return {
            "FRY_ID": self.fry_id,
            "ORDER_ITEM_ID": self.order_item_id,
            "FRY_TYPE": self.fry_type,
            "FRY_SIZE": self.fry_size,
            "FRY_SEASONING": self.fry_seasoning
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FryItem':
        return cls(
            fry_id=data.get("FRY_ID"),
            order_item_id=data.get("ORDER_ITEM_ID"),
            fry_type=data.get("FRY_TYPE"),
            fry_size=data.get("FRY_SIZE"),
            fry_seasoning=data.get("FRY_SEASONING")
        )

    def get_primary_key(self) -> int:
        return self.fry_id


# ==================== Ingredient/Lookup Entities ====================

class BunType(DatabaseEntity):
    """
    Entity representing a bun type in the BUN_TYPES table.
    Primary Key: BUN_ID
    """

    def __init__(
        self,
        bun_id: int,
        bun_name: str,
        stock_quantity: int,
        price: Decimal
    ):
        self.bun_id = bun_id
        self.bun_name = bun_name
        self.stock_quantity = stock_quantity
        self.price = price

    def to_dict(self) -> dict[str, Any]:
        return {
            "BUN_ID": self.bun_id,
            "BUN_NAME": self.bun_name,
            "STOCK_QUANTITY": self.stock_quantity,
            "PRICE": float(self.price) if self.price else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BunType':
        return cls(
            bun_id=data.get("BUN_ID"),
            bun_name=data.get("BUN_NAME"),
            stock_quantity=data.get("STOCK_QUANTITY"),
            price=Decimal(str(data.get("PRICE"))) if data.get("PRICE") else None
        )

    def get_primary_key(self) -> int:
        return self.bun_id


class PattyType(DatabaseEntity):
    """
    Entity representing a patty type in the PATTY_TYPES table.
    Primary Key: PATTY_ID
    """

    def __init__(
        self,
        patty_id: int,
        patty_name: str,
        stock_quantity: int,
        price: Decimal
    ):
        self.patty_id = patty_id
        self.patty_name = patty_name
        self.stock_quantity = stock_quantity
        self.price = price

    def to_dict(self) -> dict[str, Any]:
        return {
            "PATTY_ID": self.patty_id,
            "PATTY_NAME": self.patty_name,
            "STOCK_QUANTITY": self.stock_quantity,
            "PRICE": float(self.price) if self.price else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PattyType':
        return cls(
            patty_id=data.get("PATTY_ID"),
            patty_name=data.get("PATTY_NAME"),
            stock_quantity=data.get("STOCK_QUANTITY"),
            price=Decimal(str(data.get("PRICE"))) if data.get("PRICE") else None
        )

    def get_primary_key(self) -> int:
        return self.patty_id


class Topping(DatabaseEntity):
    """
    Entity representing a topping in the TOPPINGS table.
    Primary Key: TOPPING_ID
    """

    def __init__(
        self,
        topping_id: int,
        topping_name: str,
        stock_quantity: int,
        price: Decimal
    ):
        self.topping_id = topping_id
        self.topping_name = topping_name
        self.stock_quantity = stock_quantity
        self.price = price

    def to_dict(self) -> dict[str, Any]:
        return {
            "TOPPING_ID": self.topping_id,
            "TOPPING_NAME": self.topping_name,
            "STOCK_QUANTITY": self.stock_quantity,
            "PRICE": float(self.price) if self.price else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Topping':
        return cls(
            topping_id=data.get("TOPPING_ID"),
            topping_name=data.get("TOPPING_NAME"),
            stock_quantity=data.get("STOCK_QUANTITY"),
            price=Decimal(str(data.get("PRICE"))) if data.get("PRICE") else None
        )

    def get_primary_key(self) -> int:
        return self.topping_id


class FryType(DatabaseEntity):
    """
    Entity representing a fry type in the FRY_TYPES table.
    Primary Key: FRY_TYPE_ID
    """

    def __init__(
        self,
        fry_type_id: int,
        fry_type_name: str,
        stock_quantity: int,
        price: Decimal
    ):
        self.fry_type_id = fry_type_id
        self.fry_type_name = fry_type_name
        self.stock_quantity = stock_quantity
        self.price = price

    def to_dict(self) -> dict[str, Any]:
        return {
            "FRY_TYPE_ID": self.fry_type_id,
            "FRY_TYPE_NAME": self.fry_type_name,
            "STOCK_QUANTITY": self.stock_quantity,
            "PRICE": float(self.price) if self.price else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FryType':
        return cls(
            fry_type_id=data.get("FRY_TYPE_ID"),
            fry_type_name=data.get("FRY_TYPE_NAME"),
            stock_quantity=data.get("STOCK_QUANTITY"),
            price=Decimal(str(data.get("PRICE"))) if data.get("PRICE") else None
        )

    def get_primary_key(self) -> int:
        return self.fry_type_id


class FrySize(DatabaseEntity):
    """
    Entity representing a fry size in the FRY_SIZES table.
    Primary Key: FRY_SIZE_ID
    """

    def __init__(
        self,
        fry_size_id: int,
        fry_size: int,
        stock_quantity: int,
        price: Decimal
    ):
        self.fry_size_id = fry_size_id
        self.fry_size = fry_size
        self.stock_quantity = stock_quantity
        self.price = price

    def to_dict(self) -> dict[str, Any]:
        return {
            "FRY_SIZE_ID": self.fry_size_id,
            "FRY_SIZE": self.fry_size,
            "STOCK_QUANTITY": self.stock_quantity,
            "PRICE": float(self.price) if self.price else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FrySize':
        return cls(
            fry_size_id=data.get("FRY_SIZE_ID"),
            fry_size=data.get("FRY_SIZE"),
            stock_quantity=data.get("STOCK_QUANTITY"),
            price=Decimal(str(data.get("PRICE"))) if data.get("PRICE") else None
        )

    def get_primary_key(self) -> int:
        return self.fry_size_id


class FrySeasoning(DatabaseEntity):
    """
    Entity representing a fry seasoning in the FRY_SEASONINGS table.
    Primary Key: FRY_SEASONING_ID
    """

    def __init__(
        self,
        fry_seasoning_id: int,
        fry_seasoning_name: str,
        stock_quantity: int,
        price: Decimal
    ):
        self.fry_seasoning_id = fry_seasoning_id
        self.fry_seasoning_name = fry_seasoning_name
        self.stock_quantity = stock_quantity
        self.price = price

    def to_dict(self) -> dict[str, Any]:
        return {
            "FRY_SEASONING_ID": self.fry_seasoning_id,
            "FRY_SEASONING_NAME": self.fry_seasoning_name,
            "STOCK_QUANTITY": self.stock_quantity,
            "PRICE": float(self.price) if self.price else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FrySeasoning':
        return cls(
            fry_seasoning_id=data.get("FRY_SEASONING_ID"),
            fry_seasoning_name=data.get("FRY_SEASONING_NAME"),
            stock_quantity=data.get("STOCK_QUANTITY"),
            price=Decimal(str(data.get("PRICE"))) if data.get("PRICE") else None
        )

    def get_primary_key(self) -> int:
        return self.fry_seasoning_id
