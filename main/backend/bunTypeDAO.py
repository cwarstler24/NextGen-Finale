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

class BunTypeDAO(DatabaseAccessObject):
    '''
    DAO for managing Bun Types (ingredient lookup) in the database.
    Handles BUN_TYPES table operations.
    '''

    def __init__(self):
        '''
        Initialize the BunTypeDAO for the TBBUN_TYPES table.
        '''
        super().__init__(table_name="TBBUN_TYPES", primary_key="BUN_ID")

    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a BUN_TYPES table row to a dictionary.
        
        Args:
            row (tuple): A DB2 result row from the BUN_TYPES table
            
        Returns:
            dict[str, Any]: Dictionary representation of the bun type
        '''
        return {
            "BUN_ID": row[0],
            "BUN_NAME": row[1],
            "STOCK_QUANTITY": row[2],
            "PRICE": row[3]
        }

    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new bun type.
        
        Args:
            entry (dict[str, Any]): The bun type data to insert
            
        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name}
            (BUN_ID, BUN_NAME, STOCK_QUANTITY, PRICE) 
            VALUES (?, ?, ?, ?)
        """
        values = [
            entry.get("BUN_ID"),
            entry.get("BUN_NAME"),
            entry.get("STOCK_QUANTITY"),
            entry.get("PRICE")
        ]
        return (sql, values)

    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a bun type.
        
        Args:
            updates (dict[str, Any]): The fields to update
            
        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)

    def decrement_stock(self, bun_id: int, amount: int):
        '''
        Decrement the stock quantity for a bun type by the specified amount.
        
        Args:
            bun_id (int): The ID of the bun type to decrement
            amount (int): The amount to decrement by
            
        Returns:
            ResponseCode: Result of the stock decrement operation
        '''
        # Get current record
        current = self.get_by_key(bun_id)
        if not current.success or not current.data:
            return current
        
        # Calculate new stock
        current_stock = current.data.get("STOCK_QUANTITY", 0)
        new_stock = current_stock - amount
        
        # Update with new stock
        return self.update_record(bun_id, {"STOCK_QUANTITY": new_stock})
