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

class OrderItemDAO(DatabaseAccessObject):
    '''
    DAO for managing Order Items in the database.
    Handles ORDER_ITEMS table operations.
    '''
    
    def __init__(self):
        '''
        Initialize the OrderItemDAO for the ORDER_ITEMS table.
        '''
        super().__init__(table_name="ORDER_ITEMS", primary_key="ORDER_ITEM_ID")
    
    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert an ORDER_ITEMS table row to a dictionary.
        
        Args:
            row (tuple): A DB2 result row from the ORDER_ITEMS table
            
        Returns:
            dict[str, Any]: Dictionary representation of the order item
        '''
        return {
            "ORDER_ID": row[0],
            "ORDER_ITEM_ID": row[1],
            "ITEM_TYPE": row[2],
            "UNIT_PRICE": row[3],
            "EXTENDED_PRICE": row[4]
        }
    
    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new order item.
        
        Args:
            entry (dict[str, Any]): The order item data to insert
            
        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name} 
            (ORDER_ID, ORDER_ITEM_ID, ITEM_TYPE, UNIT_PRICE, EXTENDED_PRICE) 
            VALUES (?, ?, ?, ?, ?)
        """
        values = [
            entry.get("ORDER_ID"),
            entry.get("ORDER_ITEM_ID"),
            entry.get("ITEM_TYPE"),
            entry.get("UNIT_PRICE"),
            entry.get("EXTENDED_PRICE")
        ]
        return (sql, values)
    
    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying an order item.
        
        Args:
            updates (dict[str, Any]): The fields to update
            
        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)
