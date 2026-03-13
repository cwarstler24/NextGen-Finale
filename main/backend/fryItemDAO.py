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
from main.utilities.error_handler import ResponseCode


class FryItemDAO(DatabaseAccessObject):
    '''
    DAO for managing Fry Items in the database.
    Handles FRY_ITEMS table operations.
    '''

    def __init__(self):
        '''
        Initialize the FryItemDAO for the TBFRY_ITEMS table.
        '''
        super().__init__(table_name="TBFRY_ITEMS", primary_key="FRY_ID")

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

    def get_fry_with_details(self, fry_id: int) -> ResponseCode:
        '''
        Get a fry item with complete details including type, size, and seasoning names/prices.
        
        Args:
            fry_id (int): The fry item ID
            
        Returns:
            ResponseCode: Complete fry item information with joined ingredient details
        '''
        result = self.execute_join_query(
            select_clause="""
                f.FRY_ID, f.ORDER_ITEM_ID,
                ft.FRY_TYPE_ID, ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE, ft.STOCK_QUANTITY AS TYPE_STOCK,
                fs.FRY_SIZE_ID, fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE, fs.STOCK_QUANTITY AS SIZE_STOCK,
                fse.FRY_SEASONING_ID, fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE, fse.STOCK_QUANTITY AS SEASONING_STOCK
            """,
            join_clauses=[
                "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
                "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
                "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID"
            ],
            where_clause="f.FRY_ID = ?",
            parameters=[fry_id]
        )
  
        # Result is a ResponseCode - return it directly
        return result

    def get_all_fries_with_details(self, limit: int = None) -> ResponseCode:
        '''
        Get all fry items with complete ingredient details.
        
        Args:
            limit (int optional): Maximum number of records to return
            
        Returns:
            ResponseCode: List of fry items with joined ingredient details
        '''
        return self.execute_join_query(
            select_clause="""
                f.FRY_ID, f.ORDER_ITEM_ID,
                ft.FRY_TYPE_ID, ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE,
                fs.FRY_SIZE_ID, fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE,
                fse.FRY_SEASONING_ID, fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE
            """,
            join_clauses=[
                "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
                "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
                "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID"
            ],
            limit=limit
        )

    def get_fries_by_order_item(self, order_item_id: int) -> ResponseCode:
        '''
        Get all fries for a specific order item with complete ingredient details.
        
        Args:
            order_item_id (int): The order item ID
            
        Returns:
            ResponseCode: List of fry items with ingredient details for the order item
        '''
        return self.execute_join_query(
            select_clause="""
                f.FRY_ID, f.ORDER_ITEM_ID,
                ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE,
                fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE,
                fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE
            """,
            join_clauses=[
                "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
                "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
                "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID"
            ],
            where_clause="f.ORDER_ITEM_ID = ?",
            parameters=[order_item_id]
        )
