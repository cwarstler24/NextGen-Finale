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

class PattyTypeDAO(DatabaseAccessObject):
    '''
    DAO for managing Patty Types (ingredient lookup) in the database.
    Handles PATTY_TYPES table operations.
    '''

    def __init__(self):
        '''
        Initialize the PattyTypeDAO for the TBPATTY_TYPES table.
        '''
        super().__init__(table_name="TBPATTY_TYPES", primary_key="PATTY_ID")

    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a PATTY_TYPES table row to a dictionary.

        Args:
            row (tuple): A DB2 result row from the PATTY_TYPES table

        Returns:
            dict[str, Any]: Dictionary representation of the patty type
        '''
        return {
            "PATTY_ID": row[0],
            "PATTY_NAME": row[1],
            "STOCK_QUANTITY": row[2],
            "PRICE": row[3]
        }

    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new patty type.

        Args:
            entry (dict[str, Any]): The patty type data to insert

        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name}
            (PATTY_ID, PATTY_NAME, STOCK_QUANTITY, PRICE)
            VALUES (?, ?, ?, ?)
        """
        values = [
            entry.get("PATTY_ID"),
            entry.get("PATTY_NAME"),
            entry.get("STOCK_QUANTITY"),
            entry.get("PRICE")
        ]
        return (sql, values)

    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a patty type.

        Args:
            updates (dict[str, Any]): The fields to update

        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)
