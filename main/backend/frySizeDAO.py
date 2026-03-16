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

class FrySizeDAO(DatabaseAccessObject):
    '''
    DAO for managing Fry Sizes (ingredient lookup) in the database.
    Handles FRY_SIZES table operations.
    '''

    def __init__(self):
        '''
        Initialize the FrySizeDAO for the TBFRY_SIZES table.
        '''
        super().__init__(table_name="TBFRY_SIZES", primary_key="FRY_SIZE_ID")

    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a FRY_SIZES table row to a dictionary.

        Args:
            row (tuple): A DB2 result row from the FRY_SIZES table

        Returns:
            dict[str, Any]: Dictionary representation of the fry size
        '''
        return {
            "FRY_SIZE_ID": row[0],
            "FRY_SIZE": row[1],
            "PRICE": row[2]
        }

    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL for creating a new fry size.

        Args:
            entry (dict[str, Any]): The fry size data to insert

        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''
        sql = f"""
            INSERT INTO {self._table_name}
            (FRY_SIZE_ID, FRY_SIZE, PRICE)
            VALUES (?, ?, ?)
        """
        values = [
            entry.get("FRY_SIZE_ID"),
            entry.get("FRY_SIZE"),
            entry.get("PRICE")
        ]
        return (sql, values)

    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause for modifying a fry size.

        Args:
            updates (dict[str, Any]): The fields to update

        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''
        set_clauses = [f"{field} = ?" for field in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values())
        return (set_clause, values)
