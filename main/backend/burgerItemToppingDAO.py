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

class BurgerItemToppingDAO(DatabaseAccessObject):
    '''
    DAO for managing Burger Item Toppings (join table) in the database.
    Handles BURGER_ITEM_TOPPINGS table operations.
    Note: This table has a composite primary key, so we use TOPPING_ID as the key.
    '''
    
    def __init__(self):
        '''
        Initialize the BurgerItemToppingDAO for the BURGER_ITEM_TOPPINGS table.
        '''
        # This is a join table - using TOPPING_ID as key, but queries will typically use both columns
        super().__init__(table_name="BURGER_ITEM_TOPPINGS", primary_key="TOPPING_ID")
    
    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a BURGER_ITEM_TOPPINGS table row to a dictionary.
        
        Args:
            row (tuple): A DB2 result row from the BURGER_ITEM_TOPPINGS table
            
        Returns:
            dict[str, Any]: Dictionary representation of the burger-topping association
        '''
        return {
            "TOPPING_ID": row[0],
            "BURGER_ORDER_ID": row[1]
        }
    
    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new burger-topping association.
        
        Args:
            entry (dict[str, Any]): The association data to insert
            
        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name} 
            (TOPPING_ID, BURGER_ORDER_ID) 
            VALUES (?, ?)
        """
        values = [
            entry.get("TOPPING_ID"),
            entry.get("BURGER_ORDER_ID")
        ]
        return (sql, values)
    
    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a burger-topping association.
        
        Args:
            updates (dict[str, Any]): The fields to update
            
        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)
