# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

from abc import ABC, abstractmethod
from typing import Any, Optional
from functools import wraps
import sys
import re
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.utilities.error_handler import ResponseCode
from main.backend.db_pool import get_db_cursor
from main.utilities.logger import LoggerFactory
from contextlib import contextmanager, nullcontext


def db2_safe(func):
    '''
    Wraps a function to ensure that a ResponseCode is always returned and that the result of a given
    function is added to data. Handles DB2-specific errors by extracting SQLSTATE and SQLCODE.

    Args:
        func (Any): base function to be wrapped

    Returns:
        wrapper (function): a wrapper that will return a ResponseCode with the error or result of the passed
        in function
    '''
    @wraps(func)
    def wrapper(*args, **kwargs) -> ResponseCode:
        try:
            result = func(*args, **kwargs)
            if isinstance(result, ResponseCode):
                return result  # Don't wrap again
            return ResponseCode("SUCCESS", result)
        except Exception as e:
            # Try to extract DB2 error information
            sqlstate = None
            sqlcode = None
            error_message = str(e)

            # Check if this is an ibm_db_dbi exception with SQLSTATE/SQLCODE
            if hasattr(e, 'args') and e.args:
                error_str = str(e.args[0]) if e.args else str(e)

                # Parse SQLSTATE from error message (format: "SQLSTATE=xxxxx")
                sqlstate_match = re.search(
                    r'SQLSTATE[=:\s]+([A-Z0-9]{5})', error_str, re.IGNORECASE)
                if sqlstate_match:
                    sqlstate = sqlstate_match.group(1)

                # Parse SQLCODE from error message (format: "SQLCODE=-xxxx" or
                # "SQLCODE=xxxx")
                sqlcode_match = re.search(
                    r'SQLCODE[=:\s]+(-?\d+)', error_str, re.IGNORECASE)
                if sqlcode_match:
                    sqlcode = int(sqlcode_match.group(1))

            # Create ResponseCode with DB2 error information if available
            if sqlstate or sqlcode is not None:
                return ResponseCode(
                    error_tag=e.__class__.__name__,
                    data=error_message,
                    sqlstate=sqlstate,
                    sqlcode=sqlcode
                )
            # Generic error handling for non-DB2 errors
            error_tag = e.__class__.__name__
            return ResponseCode(
                error_tag=error_tag,
                data=f"Error: {error_message}")
    return wrapper


class DatabaseAccessObject(ABC):
    '''
    Abstract base class for DB2 Data Access Objects.
    Each DAO manages CRUD operations for a specific DB2 table using the connection pool.
    '''

    def __init__(self, table_name: str, primary_key: str = "ID"):
        '''
        Args:
            table_name (str): The name of the DB2 table this DAO accesses
            primary_key (str): The name of the primary key column (default: "ID")
        '''
        self._table_name = table_name
        self._primary_key = primary_key
        self._logger = LoggerFactory.get_general_logger()

    @contextmanager
    def _cursor_context(self, cursor=None):
        '''
        Context manager that either uses a provided cursor (for shared transactions)
        or creates a new one (for standalone operations).
        
        Args:
            cursor: Optional cursor to use. If None, creates a new cursor.
            
        Yields:
            tuple: (cursor, should_commit) where should_commit is True if we created the cursor
        '''
        if cursor is not None:
            # Use provided cursor, don't commit (caller will handle it)
            yield cursor, False
        else:
            # Create new cursor, commit after operation
            with get_db_cursor() as new_cursor:
                yield new_cursor, True

    def _prepare_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        '''
        Hook method to set default field values before insert.
        Override in subclasses to add default values.

        Args:
            entry (dict[str, Any]): The entry to be processed

        Returns:
            entry (dict[str, Any]): The entry after processing
        '''
        return entry  # Default: no changes

    @abstractmethod
    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        '''
        Convert a DB2 row tuple to a dictionary.
        Must be implemented by subclasses to define column mapping.

        Args:
            row (tuple): A DB2 result row

        Returns:
            dict[str, Any]: Dictionary representation of the row
        '''

    @abstractmethod
    def _build_insert_sql(self, entry: dict[str, Any]) -> tuple[str, list]:
        '''
        Build INSERT SQL statement and parameters.
        Must be implemented by subclasses.

        Args:
            entry (dict[str, Any]): The data to insert

        Returns:
            tuple[str, list]: SQL string and list of parameter values
        '''

    @abstractmethod
    def _build_update_sql(self, updates: dict[str, Any]) -> tuple[str, list]:
        '''
        Build UPDATE SQL SET clause and parameters.
        Must be implemented by subclasses.

        Args:
            updates (dict[str, Any]): The fields to update

        Returns:
            tuple[str, list]: SET clause string and list of parameter values
        '''

    @db2_safe
    def get_by_key(self, key_value: Any, cursor=None) -> ResponseCode:
        '''
        Return a DB2 record by primary key value

        Args:
            key_value (Any): The value of the primary key
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: ResponseCode with the record as a dictionary in data
        '''
        self._logger.debug( f"Getting {self.__class__.__name__} record by {self._primary_key}={key_value}.")

        with self._cursor_context(cursor) as (cur, should_commit):
            sql = f"SELECT * FROM {self._table_name} WHERE {self._primary_key} = ?"
            cur.execute(sql, (key_value,))
            row = cur.fetchone()
            if row is None:
                return ResponseCode(error_tag="NOT_FOUND", data=f"No record found with {self._primary_key}={key_value}")
            return self._row_to_dict(row)

    @db2_safe
    def get_by_keys(self, key_values: list[Any], cursor=None) -> ResponseCode:
        '''
        Return DB2 records matching any of the given primary key values in a
        single query. Much more efficient than calling get_by_key in a loop.

        Args:
            key_values (list[Any]): List of primary key values to fetch
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: ResponseCode with list of matching records as dictionaries
        '''
        if not key_values:
            return ResponseCode("SUCCESS", [])

        self._logger.debug(
            f"Batch fetching {self.__class__.__name__} records by "
            f"{self._primary_key} IN ({len(key_values)} keys).")

        unique_keys = list(set(key_values))
        placeholders = ", ".join(["?"] * len(unique_keys))

        with self._cursor_context(cursor) as (cur, should_commit):
            sql = f"SELECT * FROM {self._table_name} WHERE {self._primary_key} IN ({placeholders})"
            cur.execute(sql, unique_keys)
            rows = cur.fetchall()
            return [self._row_to_dict(row) for row in rows]

    @db2_safe
    def get_by_fields(self, filters: dict[str, Any]) -> ResponseCode:
        '''
        Return DB2 records matching the given field filters

        Args:
            filters (dict[str, Any]): Dictionary of field names and values to filter by

        Returns:
            ResponseCode: ResponseCode with list of matching records as dictionaries
        '''
        if not filters:
            return ResponseCode(
                error_tag="BAD_REQUEST",
                data="Filter cannot be empty")

        self._logger.debug(f"Getting {self.__class__.__name__} records by fields {filters}.")

        # Build WHERE clause
        where_clauses = [f"{field} = ?" for field in filters.keys()]
        where_sql = " AND ".join(where_clauses)
        values = list(filters.values())
        with get_db_cursor() as cursor:
            sql = f"SELECT * FROM {self._table_name} WHERE {where_sql}"
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    @db2_safe
    def get_all_records(self, limit: Optional[int] = None, cursor=None) -> ResponseCode:
        '''
        Return all (or limited) DB2 records from the table

        Args:
            limit (int optional): Maximum number of records to return
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: ResponseCode with list of records as dictionaries
        '''
        self._logger.debug(f"Getting all {self.__class__.__name__} records with limit {limit}.")

        with self._cursor_context(cursor) as (cur, should_commit):
            sql = f"SELECT * FROM {self._table_name}"
            if limit is not None:
                sql += f" FETCH FIRST {limit} ROWS ONLY"
            cur.execute(sql)
            rows = cur.fetchall()
            if not rows:
                return ResponseCode(
                    error_tag="NOT_FOUND",
                    data="No records found")
            return [self._row_to_dict(row) for row in rows]

    @db2_safe
    def get_random(self, num_returned: int = 1,
                   filters: Optional[dict[str, Any]] = None) -> ResponseCode:
        '''
        Return random records from the table

        Args:
            num_returned (int): Number of random records to return (default: 1)
            filters (dict[str, Any] optional): Optional field filters

        Returns:
            ResponseCode: ResponseCode with list of random records
        '''
        filters = filters or {}
        self._logger.debug(f"Getting {num_returned} random {self.__class__.__name__} records with filters {filters}.")

        with get_db_cursor() as cursor:
            if filters:
                where_clauses = [f"{field} = ?" for field in filters.keys()]
                where_sql = " AND ".join(where_clauses)
                values = list(filters.values())
                sql = f"SELECT * FROM {self._table_name} WHERE {where_sql} ORDER BY RAND() FETCH FIRST {num_returned} ROWS ONLY"
                cursor.execute(sql, values)
            else:
                sql = f"SELECT * FROM {self._table_name} ORDER BY RAND() FETCH FIRST {num_returned} ROWS ONLY"
                cursor.execute(sql)
            rows = cursor.fetchall()
            if len(rows) < num_returned:
                self._logger.warning(f"Requested {num_returned}, but only returned {len(rows)} records.")
            return [self._row_to_dict(row) for row in rows]

    @db2_safe
    def update_record(self,
                      key_value: Any,
                      updates: dict[str,
                                    Any],
                      cursor=None) -> ResponseCode:
        '''
        Update a record by primary key

        Args:
            key_value (Any): The value of the primary key
            updates (dict[str, Any]): Dictionary of fields to update
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: ResponseCode with the primary key value
        '''
        if not updates:
            return ResponseCode(
                "BAD_REQUEST",
                "Update payload must not be empty.")

        self._logger.debug(f"Updating {self.__class__.__name__} with {self._primary_key}={key_value}: {updates}.")

        # Build UPDATE SET clause using subclass implementation
        set_clause, values = self._build_update_sql(updates)
        values.append(key_value)  # Add primary key value for WHERE clause

        with self._cursor_context(cursor) as (cur, should_commit):
            sql = f"UPDATE {self._table_name} SET {set_clause} WHERE {self._primary_key} = ?"
            cur.execute(sql, values)
            # Check if any rows were updated
            if cur.rowcount == 0:
                return ResponseCode(error_tag="NOT_FOUND",data=f"No record found with {self._primary_key}={key_value}")
            return key_value

    @db2_safe
    def create_record(self, entry: dict[str, Any], cursor=None) -> ResponseCode:
        '''
        Create a new record in the table

        Args:
            entry (dict[str, Any]): Dictionary of field names and values
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: ResponseCode with the created record's primary key
        '''
        entry = self._prepare_entry(entry)
        self._logger.debug(f"Creating {self.__class__.__name__} record: {entry}.")

        # Build INSERT SQL using subclass implementation
        insert_sql, values = self._build_insert_sql(entry)

        with self._cursor_context(cursor) as (cur, should_commit):
            cur.execute(insert_sql, values)
            # Get the inserted primary key value
            inserted_id = entry.get(self._primary_key, "unknown")
            self._logger.debug(f"Created! New {self._primary_key}: {inserted_id}")
            return inserted_id

    @db2_safe
    def create_records_batch(self, entries: list[dict[str, Any]], cursor=None) -> ResponseCode:
        '''
        Create multiple records in a single executemany call.
        Much more efficient than calling create_record in a loop.

        Args:
            entries (list[dict[str, Any]]): List of dictionaries of field names and values
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: ResponseCode with the count of inserted records
        '''
        if not entries:
            return ResponseCode("SUCCESS", {"inserted_count": 0})

        prepared = [self._prepare_entry(entry) for entry in entries]
        self._logger.debug(
            f"Batch creating {len(prepared)} {self.__class__.__name__} records.")

        # Build SQL from the first entry (all entries must have the same structure)
        insert_sql, _ = self._build_insert_sql(prepared[0])

        # Build the values list for all entries
        all_values = [self._build_insert_sql(entry)[1] for entry in prepared]

        with self._cursor_context(cursor) as (cur, should_commit):
            cur.executemany(insert_sql, all_values)
            return {"inserted_count": len(prepared)}

    @db2_safe
    def batch_update_field_by_delta(self, deltas: dict[Any, int], field_name: str, cursor=None) -> ResponseCode:
        '''
        Update a numeric field by adding a delta value for multiple records.
        Issues one UPDATE per unique key (aggregated), instead of one per item.

        Args:
            deltas (dict[Any, int]): Mapping of primary key value -> total delta to apply
            field_name (str): Name of the field to update (e.g., "STOCK_QUANTITY")
            cursor: Optional cursor for shared transactions

        Returns:
            ResponseCode: ResponseCode with count of updated records
        '''
        if not deltas:
            return ResponseCode("SUCCESS", {"updated_count": 0})

        self._logger.debug(
            f"Batch updating {field_name} for {len(deltas)} {self.__class__.__name__} records.")

        with self._cursor_context(cursor) as (cur, should_commit):
            updated = 0
            for key_value, delta in deltas.items():
                sql = f"UPDATE {self._table_name} SET {field_name} = {field_name} + ? WHERE {self._primary_key} = ?"
                cur.execute(sql, (delta, key_value))
                updated += cur.rowcount
            return {"updated_count": updated}

    @db2_safe
    def delete_record(self, key_value: Any) -> ResponseCode:
        '''
        Delete a record by primary key

        Args:
            key_value (Any): The value of the primary key

        Returns:
            ResponseCode: ResponseCode with deleted count
        '''
        self._logger.debug(f"Deleting {self.__class__.__name__} record with {self._primary_key}={key_value}.")

        with get_db_cursor() as cursor:
            sql = f"DELETE FROM {self._table_name} WHERE {self._primary_key} = ?"
            cursor.execute(sql, (key_value,))
            if cursor.rowcount == 0:
                return ResponseCode(error_tag="NOT_FOUND",data=f"No record found with {self._primary_key}={key_value}")
            return {"deleted_count": cursor.rowcount}

    @db2_safe
    def delete_record_by_field(self, filters: dict[str, Any]) -> ResponseCode:
        '''
        Delete records matching the given field filters

        Args:
            filters (dict[str, Any]): Dictionary of field names and values to filter by

        Returns:
            ResponseCode: ResponseCode with deleted count
        '''
        if not filters:
            return ResponseCode(
                "BAD_REQUEST",
                "Delete filter must not be empty.")
        if len(filters) > 1:
            return ResponseCode("BAD_REQUEST",
                                "Delete filter must contain only one field.")

        self._logger.debug(f"Deleting {self.__class__.__name__} records by filter {filters}.")

        field = list(filters.keys())[0]
        value = filters[field]

        with get_db_cursor() as cursor:
            sql = f"DELETE FROM {self._table_name} WHERE {field} = ?"
            cursor.execute(sql, (value,))
            return {"deleted_count": cursor.rowcount}

    @db2_safe
    def get_max_id(self, cursor=None) -> ResponseCode:
        '''
        Get the maximum value of the primary key. Much faster than get_all_records().
        
        Args:
            cursor: Optional cursor for shared transactions
            
        Returns:
            ResponseCode: ResponseCode with the max ID value, or 0 if table is empty
        '''
        self._logger.debug(f"Getting max {self._primary_key} from {self.__class__.__name__}.")
        
        with self._cursor_context(cursor) as (cur, should_commit):
            sql = f"SELECT MAX({self._primary_key}) as MAX_ID FROM {self._table_name}"
            cur.execute(sql)
            row = cur.fetchone()
            max_id = row[0] if row and row[0] is not None else 0
            return max_id

    @db2_safe
    def update_field_by_delta(self, key_value: Any, field_name: str, delta: int, cursor=None) -> ResponseCode:
        '''
        Update a numeric field by adding a delta value. Useful for stock decrements.
        Uses a single atomic UPDATE instead of SELECT + UPDATE.
        
        Args:
            key_value (Any): The value of the primary key
            field_name (str): Name of the field to update (e.g., "STOCK_QUANTITY")
            delta (int): Amount to add (use negative for decrement)
            cursor: Optional cursor for shared transactions
            
        Returns:
            ResponseCode: ResponseCode with success status
        '''
        self._logger.debug(f"Updating {field_name} by {delta} for {self.__class__.__name__} with {self._primary_key}={key_value}.")
        
        with self._cursor_context(cursor) as (cur, should_commit):
            sql = f"UPDATE {self._table_name} SET {field_name} = {field_name} + ? WHERE {self._primary_key} = ?"
            cur.execute(sql, (delta, key_value))
            if cur.rowcount == 0:
                return ResponseCode(error_tag="NOT_FOUND", data=f"No record found with {self._primary_key}={key_value}")
            return {"updated_count": cur.rowcount}

    def execute_join_query(
        self,
        select_clause: str,
        join_clauses: list[str],
        where_clause: str = "",
        parameters: list = None,
        limit: Optional[int] = None
    ) -> ResponseCode:
        '''
        Execute a JOIN query and return raw results wrapped in ResponseCode.
        Helper method for subclasses to implement complex joins.
        
        Args:
            select_clause (str): SELECT clause (e.g., "t1.*, t2.name")
            join_clauses (list[str]): List of JOIN statements
            where_clause (str): Optional WHERE clause (without "WHERE" keyword)
            parameters (list): Optional parameters for WHERE clause
            limit (int optional): Maximum number of records to return
            
        Returns:
            ResponseCode: ResponseCode with list of result dictionaries in .data
            
        Example:
            result = self.execute_join_query(
                select_clause="f.*, ft.name as type_name",
                join_clauses=["INNER JOIN TBFRY_TYPES ft ON f.FRY_TYPE = ft.FRY_TYPE_ID"],
                where_clause="f.FRY_ID = ?",
                parameters=[fry_id]
            )
            if result.error_tag:
                # handle error
            else:
                # use result.data
        '''
        parameters = parameters or []

        try:
            # Build the query - extract table alias from first column reference in select_clause
            # The select_clause should use aliases like "f.FRY_ID" so extract the alias
            # Fallback to first letter of table name if no alias found
            alias_match = re.search(r'(\w+)\.', select_clause)
            table_alias = alias_match.group(1) if alias_match else self._table_name[0].lower()

            sql = f"SELECT {select_clause} FROM {self._table_name} {table_alias}"

            # Add joins
            for join in join_clauses:
                sql += f" {join}"

            # Add WHERE clause
            if where_clause:
                sql += f" WHERE {where_clause}"

            # Add limit
            if limit is not None:
                sql += f" FETCH FIRST {limit} ROWS ONLY"

            self._logger.debug(f"Executing join query: {sql}")

            with get_db_cursor() as cursor:
                cursor.execute(sql, parameters)
                rows = cursor.fetchall()

                if not rows:
                    return ResponseCode("SUCCESS", [])

                # Get column names from cursor description
                columns = [desc[0] for desc in cursor.description]

                # Convert rows to dictionaries
                results = []
                for row in rows:
                    row_dict = {columns[i]: row[i] for i in range(len(columns))}
                    results.append(row_dict)

                return ResponseCode("SUCCESS", results)

        except Exception as e:
            self._logger.error(f"Join query failed: {str(e)}")
            return ResponseCode(error_tag="DATABASE_ERROR", data=str(e))
