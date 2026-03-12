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

class FryItemDAO(DatabaseAccessObject):
    '''
    DAO for managing Fry Items in the database.
    Handles FRY_ITEMS table operations.
    '''
    
    def __init__(self):
        '''
        Initialize the FryItemDAO for the FRY_ITEMS table.
        '''
        super().__init__(table_name="FRY_ITEMS", primary_key="FRY_ID")
    
    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a FRY_ITEMS table row to a dictionary.
        
        Args:
            row (tuple): A DB2 result row from the FRY_ITEMS table
            
        Returns:
            dict[str, Any]: Dictionary representation of the fry item
        '''
        return {
            "FRY_ID": row[0],
            "ORDER_ITEM_ID": row[1],
            "FRY_TYPE": row[2],
            "FRY_SIZE": row[3],
            "FRY_SEASONING": row[4]
        }
    
    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new fry item.
        
        Args:
            entry (dict[str, Any]): The fry item data to insert
            
        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name} 
            (FRY_ID, ORDER_ITEM_ID, FRY_TYPE, FRY_SIZE, FRY_SEASONING) 
            VALUES (?, ?, ?, ?, ?)
        """
        values = [
            entry.get("FRY_ID"),
            entry.get("ORDER_ITEM_ID"),
            entry.get("FRY_TYPE"),
            entry.get("FRY_SIZE"),
            entry.get("FRY_SEASONING")
        ]
        return (sql, values)
    
    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a fry item.
        
        Args:
            updates (dict[str, Any]): The fields to update
            
        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)
