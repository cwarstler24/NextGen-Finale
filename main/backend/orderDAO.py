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

class OrderDAO(DatabaseAccessObject):
    '''
    DAO for managing Orders in the database.
    Handles ORDERS table operations.
    '''

    def __init__(self):
        '''
        Initialize the OrderDAO for the TBORDERS table.
        The database connection is managed by the connection pool.
        '''
        super().__init__(table_name="TBORDERS", primary_key="ORDER_ID")

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

    def get_order_with_customer(self, order_id: int) -> ResponseCode:
        '''
        Get an order with complete customer information.
        
        Args:
            order_id (int): The order ID
            
        Returns:
            ResponseCode: Order with joined customer details
        '''
        result = self.execute_join_query(
            select_clause="""
                o.ORDER_ID, o.EMAIL, o.PURCHASE_DATE, o.ORDER_QTY, o.TOTAL_PRICE,
                c.NAME AS CUSTOMER_NAME, c.BILL_ADDR, c.SHIP_ADDR
            """,
            join_clauses=[
                "INNER JOIN TBCUSTOMER c ON o.EMAIL = c.EMAIL"
            ],
            where_clause="o.ORDER_ID = ?",
            parameters=[order_id]
        )

        # Result is a ResponseCode - return it directly
        return result

    def get_orders_by_customer(self, email: str, limit: int = None) -> ResponseCode:
        '''
        Get all orders for a specific customer.
        
        Args:
            email (str): The customer email
            limit (int optional): Maximum number of orders to return
            
        Returns:
            ResponseCode: List of orders for the customer
        '''
        return self.execute_join_query(
            select_clause="""
                o.ORDER_ID, o.EMAIL, o.PURCHASE_DATE, o.ORDER_QTY, o.TOTAL_PRICE,
                c.NAME AS CUSTOMER_NAME
            """,
            join_clauses=[
                "INNER JOIN TBCUSTOMER c ON o.EMAIL = c.EMAIL"
            ],
            where_clause="o.EMAIL = ?",
            parameters=[email],
            limit=limit
        )

    def get_order_items(self, order_id: int) -> ResponseCode:
        '''
        Get all items for a specific order.
        
        Args:
            order_id (int): The order ID
            
        Returns:
            ResponseCode: List of order items
        '''
        return self.execute_join_query(
            select_clause="""
                oi.ORDER_ITEM_ID, oi.ORDER_ID, oi.ITEM_TYPE, 
                oi.UNIT_PRICE,
            """,
            join_clauses=[
                "INNER JOIN TBORDER_ITEMS oi ON o.ORDER_ID = oi.ORDER_ID"
            ],
            where_clause="o.ORDER_ID = ?",
            parameters=[order_id]
        )
