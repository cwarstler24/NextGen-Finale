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

class OrderItemDAO(DatabaseAccessObject):
    '''
    DAO for managing Order Items in the database.
    Handles ORDER_ITEMS table operations.
    '''

    def __init__(self):
        '''
        Initialize the OrderItemDAO for the TBORDER_ITEMS table.
        '''
        super().__init__(table_name="TBORDER_ITEMS", primary_key="ORDER_ITEM_ID")

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
            (ORDER_ID, ORDER_ITEM_ID, ITEM_TYPE, UNIT_PRICE)
            VALUES (?, ?, ?, ?)
        """
        values = [
            entry.get("ORDER_ID"),
            entry.get("ORDER_ITEM_ID"),
            entry.get("ITEM_TYPE"),
            entry.get("UNIT_PRICE"),
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

    def get_order_items_with_burgers(self, order_id: int) -> ResponseCode:
        '''
        Get all burger order items for a specific order with complete burger details.
        
        Args:
            order_id (int): The order ID
            
        Returns:
            ResponseCode: List of burger order items with ingredient details
        '''
        return self.execute_join_query(
            select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, oi.UNIT_PRICE,
                b.BURGER_ID, b.PATTY_COUNT,
                bt.BUN_NAME, bt.PRICE AS BUN_PRICE,
                pt.PATTY_NAME, pt.PRICE AS PATTY_PRICE
            """,
            join_clauses=[
                "INNER JOIN TBBURGER_ITEMS b ON oi.ORDER_ITEM_ID = b.ORDER_ITEM_ID",
                "INNER JOIN TBBUN_TYPES bt ON b.BUN_TYPE = bt.BUN_ID",
                "INNER JOIN TBPATTY_TYPES pt ON b.PATTY_TYPE = pt.PATTY_ID"
            ],
            where_clause="oi.ORDER_ID = ? AND oi.ITEM_TYPE = 'BURGER'",
            parameters=[order_id]
        )

    def get_order_items_with_fries(self, order_id: int) -> ResponseCode:
        '''
        Get all fry order items for a specific order with complete fry details.
        
        Args:
            order_id (int): The order ID
            
        Returns:
            ResponseCode: List of fry order items with ingredient details
        '''
        return self.execute_join_query(
            select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, oi.UNIT_PRICE,
                f.FRY_ID,
                ft.FRY_TYPE_NAME AS TYPE_NAME, ft.PRICE AS TYPE_PRICE,
                fs.FRY_SIZE AS SIZE_VALUE, fs.PRICE AS SIZE_PRICE,
                fse.FRY_SEASONING_NAME AS SEASONING_NAME, fse.PRICE AS SEASONING_PRICE
            """,
            join_clauses=[
                "INNER JOIN TBFRY_ITEMS f ON oi.ORDER_ITEM_ID = f.ORDER_ITEM_ID",
                "INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID",
                "INNER JOIN TBFRY_SIZES fs ON f.FRY_SIZE = fs.FRY_SIZE_ID",
                "INNER JOIN TBFRY_SEASONINGS fse ON f.FRY_SEASONING = fse.FRY_SEASONING_ID"
            ],
            where_clause="oi.ORDER_ID = ? AND oi.ITEM_TYPE = 'FRIES'",
            parameters=[order_id]
        )

    def get_all_order_items_with_details(self, order_id: int) -> ResponseCode:
        '''
        Get all order items for an order (both burgers and fries) with complete details.
        
        Args:
            order_id (int): The order ID
            
        Returns:
            ResponseCode: Dictionary with 'burgers' and 'fries' lists
        '''
        burgers_result = self.get_order_items_with_burgers(order_id)
        fries_result = self.get_order_items_with_fries(order_id)

        combined_data = {
            "burgers": burgers_result.data if burgers_result.success else [],
            "fries": fries_result.data if fries_result.success else []
        }

        return ResponseCode("SUCCESS", combined_data)
