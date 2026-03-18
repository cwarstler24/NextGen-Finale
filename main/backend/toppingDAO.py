# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

import sys
from pathlib import Path
from typing import Any

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.backend.AbstractDAO import DatabaseAccessObject

class ToppingDAO(DatabaseAccessObject):
    '''
    DAO for managing Toppings (ingredient lookup) in the database.
    Handles TOPPINGS table operations.
    '''

    def __init__(self):
        '''
        Initialize the ToppingDAO for the TBTOPPINGS table.
        '''
        super().__init__(table_name="TBTOPPINGS", primary_key="TOPPING_ID")

    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a TOPPINGS table row to a dictionary.

        Args:
            row (tuple): A DB2 result row from the TOPPINGS table

        Returns:
            dict[str, Any]: Dictionary representation of the topping
        '''
        return {
            "TOPPING_ID": row[0],
            "TOPPING_NAME": row[1],
            "STOCK_QUANTITY": row[2],
            "PRICE": row[3]
        }

    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new topping.

        Args:
            entry (dict[str, Any]): The topping data to insert

        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name}
            (TOPPING_ID, TOPPING_NAME, STOCK_QUANTITY, PRICE)
            VALUES (?, ?, ?, ?)
        """
        values = [
            entry.get("TOPPING_ID"),
            entry.get("TOPPING_NAME"),
            entry.get("STOCK_QUANTITY"),
            entry.get("PRICE")
        ]
        return (sql, values)

    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a topping.

        Args:
            updates (dict[str, Any]): The fields to update

        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)

    def decrement_stock(self, topping_id: int, amount: int, cursor=None):
        '''
        Decrement the stock quantity for a topping by the specified amount.
        Uses optimized single UPDATE query instead of SELECT + UPDATE.

        Args:
            topping_id (int): The ID of the topping to decrement
            amount (int): The amount to decrement by
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: Result of the stock decrement operation
        '''
        # Use atomic UPDATE operation (single query instead of SELECT + UPDATE)
        return self.update_field_by_delta(topping_id, "STOCK_QUANTITY", -amount, cursor=cursor)
