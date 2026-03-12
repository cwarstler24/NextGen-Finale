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

class OrderDAO(DatabaseAccessObject):
    '''
    DAO for managing Orders in the database.
    Handles ORDERS table operations.
    '''
    
    def __init__(self):
        '''
        Initialize the OrderDAO for the ORDERS table.
        The database connection is managed by the connection pool.
        '''
        super().__init__(table_name="ORDERS", primary_key="ORDER_ID")
    
    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert an ORDERS table row to a dictionary.
        
        Args:
            row (tuple): A DB2 result row from the ORDERS table
            
        Returns:
            dict[str, Any]: Dictionary representation of the order
        '''
        return {
            "ORDER_ID": row[0],
            "EMAIL": row[1],
            "PURCHASE_DATE": row[2],
            "ORDER_QTY": row[3],
            "TOTAL_PRICE": row[4]
        }
    
    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new order.
        
        Args:
            entry (dict[str, Any]): The order data to insert
            
        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name} 
            (ORDER_ID, EMAIL, PURCHASE_DATE, ORDER_QTY, TOTAL_PRICE) 
            VALUES (?, ?, ?, ?, ?)
        """
        values = [
            entry.get("ORDER_ID"),
            entry.get("EMAIL"),
            entry.get("PURCHASE_DATE"),
            entry.get("ORDER_QTY"),
            entry.get("TOTAL_PRICE")
        ]
        return (sql, values)
    
    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying an order.
        
        Args:
            updates (dict[str, Any]): The fields to update
            
        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)