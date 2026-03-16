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

class FryTypeDAO(DatabaseAccessObject):
    '''
    DAO for managing Fry Types (ingredient lookup) in the database.
    Handles FRY_TYPES table operations.
    '''

    def __init__(self):
        '''
        Initialize the FryTypeDAO for the TBFRY_TYPES table.
        '''
        super().__init__(table_name="TBFRY_TYPES", primary_key="FRY_TYPE_ID")

    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a FRY_TYPES table row to a dictionary.

        Args:
            row (tuple): A DB2 result row from the FRY_TYPES table

        Returns:
            dict[str, Any]: Dictionary representation of the fry type
        '''
        return {
            "FRY_TYPE_ID": row[0],
            "FRY_TYPE_NAME": row[1],
            "STOCK_QUANTITY": row[2],
            "PRICE": row[3]
        }

    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new fry type.

        Args:
            entry (dict[str, Any]): The fry type data to insert

        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name}
            (FRY_TYPE_ID, FRY_TYPE_NAME, STOCK_QUANTITY, PRICE)
            VALUES (?, ?, ?, ?)
        """
        values = [
            entry.get("FRY_TYPE_ID"),
            entry.get("FRY_TYPE_NAME"),
            entry.get("STOCK_QUANTITY"),
            entry.get("PRICE")
        ]
        return (sql, values)

    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a fry type.

        Args:
            updates (dict[str, Any]): The fields to update

        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)

    def decrement_stock(self, fry_type_id: int, amount: int):
        '''
        Decrement the stock quantity for a fry type by the specified amount.

        Args:
            fry_type_id (int): The ID of the fry type to decrement
            amount (int): The amount to decrement by

        Returns:
            ResponseCode: Result of the stock decrement operation
        '''
        # Get current record
        current = self.get_by_key(fry_type_id)
        if not current.success or not current.data:
            return current
        
        # Calculate new stock
        current_stock = current.data.get("STOCK_QUANTITY", 0)
        new_stock = current_stock - amount
        
        # Update with new stock
        return self.update_record(fry_type_id, {"STOCK_QUANTITY": new_stock})
