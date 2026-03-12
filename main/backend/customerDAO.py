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

class CustomerDAO(DatabaseAccessObject):
    '''
    DAO for managing Customer records in the database.
    Handles CUSTOMER table operations.
    '''
    
    def __init__(self):
        '''
        Initialize the CustomerDAO for the CUSTOMER table.
        Primary key is email address.
        '''
        super().__init__(table_name="CUSTOMER", primary_key="EMAIL")
    
    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a CUSTOMER table row to a dictionary.
        
        Args:
            row (tuple): A DB2 result row from the CUSTOMER table
            
        Returns:
            dict[str, Any]: Dictionary representation of the customer
        '''
        return {
            "EMAIL": row[0],
            "NAME": row[1],
            "BILL_ADDR": row[2],
            "SHIP_ADDR": row[3]
        }
    
    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new customer.
        
        Args:
            entry (dict[str, Any]): The customer data to insert
            
        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name} 
            (EMAIL, NAME, BILL_ADDR, SHIP_ADDR) 
            VALUES (?, ?, ?, ?)
        """
        values = [
            entry.get("EMAIL"),
            entry.get("NAME"),
            entry.get("BILL_ADDR"),
            entry.get("SHIP_ADDR")
        ]
        return (sql, values)
    
    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a customer.
        
        Args:
            updates (dict[str, Any]): The fields to update
            
        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)
