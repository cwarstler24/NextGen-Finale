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

class BurgerItemDAO(DatabaseAccessObject):
    '''
    DAO for managing Burger Items in the database.
    Handles BURGER_ITEMS table operations.
    '''
    
    def __init__(self):
        '''
        Initialize the BurgerItemDAO for the BURGER_ITEMS table.
        '''
        super().__init__(table_name="BURGER_ITEMS", primary_key="BURGER_ID")
    
    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a BURGER_ITEMS table row to a dictionary.
        
        Args:
            row (tuple): A DB2 result row from the BURGER_ITEMS table
            
        Returns:
            dict[str, Any]: Dictionary representation of the burger item
        '''
        return {
            "BURGER_ID": row[0],
            "ORDER_ITEM_ID": row[1],
            "BUN_TYPE": row[2],
            "PATTY_TYPE": row[3]
        }
    
    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new burger item.
        
        Args:
            entry (dict[str, Any]): The burger item data to insert
            
        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name} 
            (BURGER_ID, ORDER_ITEM_ID, BUN_TYPE, PATTY_TYPE) 
            VALUES (?, ?, ?, ?)
        """
        values = [
            entry.get("BURGER_ID"),
            entry.get("ORDER_ITEM_ID"),
            entry.get("BUN_TYPE"),
            entry.get("PATTY_TYPE")
        ]
        return (sql, values)
    
    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a burger item.
        
        Args:
            updates (dict[str, Any]): The fields to update
            
        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)
