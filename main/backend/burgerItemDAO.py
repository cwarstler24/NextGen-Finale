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

class BurgerItemDAO(DatabaseAccessObject):
    '''
    DAO for managing Burger Items in the database.
    Handles BURGER_ITEMS table operations.
    '''
    def __init__(self):
        '''
        Initialize the BurgerItemDAO for the TBBURGER_ITEMS table.
        '''
        super().__init__(table_name="TBBURGER_ITEMS", primary_key="BURGER_ID")

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
            (BURGER_ID, ORDER_ITEM_ID, BUN_TYPE, PATTY_TYPE, PATTY_COUNT) 
            VALUES (?, ?, ?, ?, ?)
        """
        values = [
            entry.get("BURGER_ID"),
            entry.get("ORDER_ITEM_ID"),
            entry.get("BUN_TYPE"),
            entry.get("PATTY_TYPE"),
            entry.get("PATTY_COUNT", 1)  # Default to 1 patty if not specified
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

    def get_burger_with_details(self, burger_id: int) -> ResponseCode:
        '''
        Get a burger item with complete details including bun, patty, and toppings.
        Note: Returns burger with base ingredients; use get_burger_toppings for topping list.
        
        Args:
            burger_id (int): The burger item ID
            
        Returns:
            ResponseCode: Complete burger item information with joined ingredient details
        '''
        result = self.execute_join_query(
            select_clause="""
                b.BURGER_ID, b.ORDER_ITEM_ID,
                bt.BUN_ID, bt.BUN_NAME, bt.PRICE AS BUN_PRICE, bt.STOCK_QUANTITY AS BUN_STOCK,
                pt.PATTY_ID, pt.PATTY_NAME, pt.PRICE AS PATTY_PRICE, pt.STOCK_QUANTITY AS PATTY_STOCK
            """,
            join_clauses=[
                "INNER JOIN TBBUN_TYPES bt ON b.BUN_TYPE = bt.BUN_ID",
                "INNER JOIN TBPATTY_TYPES pt ON b.PATTY_TYPE = pt.PATTY_ID"
            ],
            where_clause="b.BURGER_ID = ?",
            parameters=[burger_id]
        )

        # Result is a ResponseCode - return it directly
        return result

    def get_burger_toppings(self, burger_id: int) -> ResponseCode:
        '''
        Get all toppings for a specific burger.
        
        Args:
            burger_id (int): The burger item ID
            
        Returns:
            ResponseCode: List of toppings with details for the burger
        '''
        return self.execute_join_query(
            select_clause="""
                b.BURGER_ID, t.TOPPING_ID, t.TOPPING_NAME, t.PRICE, t.STOCK_QUANTITY, bit.TOPPING_COUNT
            """,
            join_clauses=[
                "INNER JOIN TBBURGER_TOPPINGS bit ON b.BURGER_ID = bit.BURGER_ORDER_ID",
                "INNER JOIN TBTOPPINGS t ON bit.TOPPING_ID = t.TOPPING_ID"
            ],
            where_clause="b.BURGER_ID = ?",
            parameters=[burger_id]
        )

    def get_toppings_for_burgers(self, burger_ids: list[int]) -> ResponseCode:
        '''
        Get all toppings for multiple burgers in a single query.

        Args:
            burger_ids (list[int]): List of burger item IDs

        Returns:
            ResponseCode: List of toppings with BURGER_ID for grouping
        '''
        if not burger_ids:
            return ResponseCode("SUCCESS", [])
        placeholders = ", ".join(["?"] * len(burger_ids))
        return self.execute_join_query(
            select_clause="""
                b.BURGER_ID, t.TOPPING_ID, t.TOPPING_NAME, t.PRICE, t.STOCK_QUANTITY, bit.TOPPING_COUNT
            """,
            join_clauses=[
                "INNER JOIN TBBURGER_TOPPINGS bit ON b.BURGER_ID = bit.BURGER_ORDER_ID",
                "INNER JOIN TBTOPPINGS t ON bit.TOPPING_ID = t.TOPPING_ID"
            ],
            where_clause=f"b.BURGER_ID IN ({placeholders})",
            parameters=burger_ids
        )

    def get_burger_complete(self, burger_id: int) -> ResponseCode:
        '''
        Get complete burger information including bun, patty, and all toppings.
        Returns a structured dictionary with all components.
        
        Args:
            burger_id (int): The burger item ID
            
        Returns:
            ResponseCode: Complete burger with all ingredient details
        '''
        # Get base burger details
        burger_result = self.get_burger_with_details(burger_id)
        if burger_result.error_tag:
            return burger_result

        # Get toppings
        toppings_result = self.get_burger_toppings(burger_id)

        # Combine results - burger_result.data is a list, get first item
        if burger_result.data and len(burger_result.data) > 0:
            burger_data = burger_result.data[0].copy()
            if not toppings_result.error_tag and toppings_result.data:
                burger_data["TOPPINGS"] = toppings_result.data
            else:
                burger_data["TOPPINGS"] = []
            return ResponseCode("SUCCESS", burger_data)
        else:
            return ResponseCode(error_tag="NOT_FOUND", data=f"Burger {burger_id} not found")

    def get_burgers_by_order_item(self, order_item_id: int) -> ResponseCode:
        '''
        Get all burgers for a specific order item with complete ingredient details.
        
        Args:
            order_item_id (int): The order item ID
            
        Returns:
            ResponseCode: List of burger items with ingredient details for the order item
        '''
        return self.execute_join_query(
            select_clause="""
                b.BURGER_ID, b.ORDER_ITEM_ID,
                bt.BUN_NAME, bt.PRICE AS BUN_PRICE,
                pt.PATTY_NAME, pt.PRICE AS PATTY_PRICE
            """,
            join_clauses=[
                "INNER JOIN TBBUN_TYPES bt ON b.BUN_TYPE = bt.BUN_ID",
                "INNER JOIN TBPATTY_TYPES pt ON b.PATTY_TYPE = pt.PATTY_ID"
            ],
            where_clause="b.ORDER_ITEM_ID = ?",
            parameters=[order_item_id]
        )
