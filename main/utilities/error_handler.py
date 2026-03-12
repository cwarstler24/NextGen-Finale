# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

from typing import Optional, Any
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.utilities.logger import LoggerFactory

_RESPONSE_MAP = {
    "SUCCESS": (200, "Operation completed successfully."),
    "BAD_REQUEST": (400, "The request was invalid or cannot be processed."),
    "UNAUTHORIZED": (401, "Authentication is required and has failed or has not been provided."),
    "FORBIDDEN": (403, "You do not have permission to access this resource."),
    "NOT_FOUND": (404, "The requested resource could not be found."),
    "METHOD_NOT_ALLOWED": (405, "The HTTP method is not allowed for this endpoint."),
    "CONFLICT": (409, "A conflict occurred with the current state of the resource."),
    "INTERNAL_SERVER_ERROR": (500, "An unexpected error occurred on the server."),
    "DB_CONNECTION_POOL_EXHAUSTED": (503, "Database connection pool is exhausted. All connections currently in use."),
    "DB_CONNECTION_FAILED": (503, "Failed to establish database connection.")
}

# DB2 SQLSTATE to HTTP status code mapping
# Reference: https://www.ibm.com/docs/en/db2/11.5?topic=messages-sqlstate
_DB2_SQLSTATE_MAP = {
    # 2xxxx - Success/Warning (not errors, but we map them)
    "01xxx": (200, "Success with warning."),
    "02000": (404, "No data found."),

    # 08xxx - Connection exceptions
    "08001": (503, "Unable to establish SQL connection."),
    "08002": (503, "Connection already exists."),
    "08003": (503, "Connection does not exist."),
    "08004": (503, "SQL server rejected connection."),
    "08007": (503, "Transaction resolution unknown."),

    # 22xxx - Data exceptions
    "22001": (400, "String data right truncation."),
    "22003": (400, "Numeric value out of range."),
    "22007": (400, "Invalid datetime format."),
    "22008": (400, "Datetime field overflow."),
    "22012": (400, "Division by zero."),
    "22018": (400, "Invalid character value for cast."),
    "22023": (400, "Invalid parameter value."),

    # 23xxx - Integrity constraint violations
    "23000": (409, "Integrity constraint violation."),
    "23001": (409, "Restrict violation (referenced key still exists)."),
    "23502": (400, "NOT NULL constraint violation."),
    "23503": (409, "Foreign key constraint violation."),
    "23505": (409, "Duplicate key value violates unique constraint."),
    "23513": (400, "Check constraint violation."),

    # 24xxx - Invalid cursor state
    "24000": (400, "Invalid cursor state."),
    "24501": (400, "Cursor not open."),
    "24502": (400, "Cursor already open."),

    # 25xxx - Invalid transaction state
    "25000": (400, "Invalid transaction state."),
    "25001": (400, "Active SQL transaction."),

    # 40xxx - Transaction rollback
    "40001": (409, "Serialization failure (deadlock)."),
    "40003": (409, "Statement completion unknown."),

    # 42xxx - Syntax error or access rule violation
    "42000": (400, "Syntax error or access violation."),
    "42601": (400, "SQL syntax error."),
    "42703": (400, "Undefined column."),
    "42704": (404, "Undefined object (table, view, etc.)."),
    "42710": (409, "Object already exists."),
    "42723": (409, "Function already exists."),
    "42803": (400, "Invalid column reference in GROUP BY."),
    "42804": (400, "Datatype mismatch."),
    "42818": (400, "Operands of an operation are not compatible."),
    "42884": (400, "No routine found with matching signature."),
    "42939": (400, "Reserved name."),

    # 51xxx - Invalid application state
    "51002": (400, "Procedure returned too many result sets."),
    "51003": (400, "Procedure must return result sets."),

    # 53xxx - Insufficient resources
    "53000": (503, "Insufficient resources."),
    "53200": (507, "Insufficient storage."),
    "53400": (503, "Table space or index is full."),

    # 54xxx - SQL or product limit exceeded
    "54000": (400, "SQL statement too long or complex."),
    "54001": (400, "Statement too complex."),
    "54011": (400, "Too many columns."),
    "54023": (400, "Too many sort keys."),

    # 55xxx - Object not in prerequisite state
    "55000": (409, "Object not in prerequisite state."),
    "55006": (409, "Object is in use."),
    "55019": (409, "Package or authorization not active."),

    # 56xxx - Miscellaneous SQL or product error
    "56038": (500, "File I/O error during DMS operation."),
    "56084": (500, "Unsupported SQLTYPE."),

    # 57xxx - Resource not available or operator intervention
    "57001": (503, "Out of memory or disk space."),
    "57011": (503, "Virtual storage or database resource not available."),
    "57012": (503, "Non-database resource not available."),
    "57013": (503, "Insufficient memory."),
    "57014": (503, "Processing canceled."),
    "57033": (503, "Deadlock or timeout."),

    # 58xxx - System error
    "58004": (500, "System error (internal DB2 error)."),
    "58005": (500, "System error (unrecoverable)."),
    "58008": (500, "Execution failed due to distribution protocol error."),
    "58009": (500, "Execution failed due to break in connection."),
    "58030": (500, "System error (I/O error)."),

    # Common SQLCODE mappings (negative values indicate errors)
    "-1": (500, "General SQL error."),
    "-204": (404, "Undefined name (table, view, or column)."),
    "-206": (400, "Column does not exist."),
    "-407": (400, "NULL value not allowed."),
    "-530": (409, "Foreign key constraint violation."),
    "-532": (409, "Delete restricted by foreign key constraint."),
    "-601": (409, "Object already exists."),
    "-803": (409, "Duplicate key violation."),
    "-904": (503, "Resource unavailable."),
    "-911": (409, "Deadlock or timeout occurred."),
    "-913": (503, "Unsuccessful execution due to deadlock or timeout."),
    "-1001": (503, "Connection failed."),
    "-1042": (500, "Internal error in DB2 database."),
}


def get_db2_error_response(sqlstate: str = None,
                           sqlcode: int = None,
                           default_message: str = None) -> tuple[int,
                                                                 str]:
    """
    Map DB2 SQLSTATE or SQLCODE to HTTP status code and message.

    Args:
        sqlstate (str): The DB2 SQLSTATE code (e.g., "42704", "23505")
        sqlcode (int): The DB2 SQLCODE (negative for errors, e.g., -204, -803)
        default_message (str): Optional default message if no mapping found

    Returns:
        tuple[int, str]: HTTP status code and error message
    """
    # Try exact SQLSTATE match first
    if sqlstate:
        if sqlstate in _DB2_SQLSTATE_MAP:
            return _DB2_SQLSTATE_MAP[sqlstate]

        # Try wildcard match (e.g., "42xxx" for any 42xxx error)
        sqlstate_class = sqlstate[:2] + "xxx"
        if sqlstate_class in _DB2_SQLSTATE_MAP:
            return _DB2_SQLSTATE_MAP[sqlstate_class]

    # Try SQLCODE match
    if sqlcode is not None:
        sqlcode_str = str(sqlcode)
        if sqlcode_str in _DB2_SQLSTATE_MAP:
            return _DB2_SQLSTATE_MAP[sqlcode_str]

    # Default to internal server error
    message = default_message or "Database error occurred."
    return (500, message)


class ResponseCode:
    '''
    This class wraps a detailed HTTP response code with a custom message and added data and automatically
    logs this result
    '''

    def __init__(
            self,
            error_tag: str = "",
            data: Optional[Any] = None,
            sqlstate: str = None,
            sqlcode: int = None):
        '''
        Args:
            error_tag (str): the name of error that will be passed to the RESPONSE_MAP to get the HTTP error code
            data (any optional): extra data from the operation or error to be sent with the response (defaults to None)
            sqlstate (str optional): DB2 SQLSTATE code for database errors
            sqlcode (int optional): DB2 SQLCODE for database errors
        '''
        self.__logger = LoggerFactory.get_general_logger()
        self.__error_tag = error_tag

        # Check if this is a DB2 error (sqlstate or sqlcode provided)
        if sqlstate or sqlcode is not None:
            self.__error_code, self.__message = get_db2_error_response(
                sqlstate, sqlcode)
            # Add DB2 error details to the error tag
            db2_info = []
            if sqlstate:
                db2_info.append(f"SQLSTATE={sqlstate}")
            if sqlcode is not None:
                db2_info.append(f"SQLCODE={sqlcode}")
            self.__error_tag = f"DB2Error_{error_tag}" if error_tag else "DB2Error"
            if db2_info:
                self.__error_tag += f" ({', '.join(db2_info)})"
        else:
            # Default to 500 error if it cannot be found in look-up table
            self.__error_code, self.__message = _RESPONSE_MAP.get(
                error_tag, (500, "An unexpected error occurred."))

        self.__success = (self.__error_code < 300)
        self.__data = data

        if (not self.__success):
            self.__logger.error(
                f"{
                    self.__error_code}. {
                    self.__error_tag}: {
                    self.__message}\n\t\t\tdata: {
                    self.__data}")
        else:
            self.__logger.info(
                f"{
                    self.__error_code}. {
                    self.__error_tag}: {
                    self.__message}\n\t\t\tdata: {
                    self.__data}")

    def get_success(self) -> bool:
        return self.__success

    def get_error_code(self) -> int:
        return self.__error_code

    def get_error_tag(self) -> str:
        return self.__error_tag

    def get_message(self) -> str:
        return self.__message

    def get_data(self) -> Optional[Any]:
        return self.__data

    # Properties for convenient attribute-style access
    @property
    def success(self) -> bool:
        """Whether the operation was successful (HTTP code < 300)"""
        return self.__success

    @property
    def error_code(self) -> int:
        """The HTTP error code"""
        return self.__error_code

    @property
    def error_tag(self) -> str:
        """The error tag/identifier"""
        return self.__error_tag

    @property
    def message(self) -> str:
        """The error/success message"""
        return self.__message

    @property
    def data(self) -> Optional[Any]:
        """The data payload"""
        return self.__data

    def to_http_response(self) -> tuple[int, dict]:
        '''
        Creates an HTTP response to send back to the user

        Returns:
            response (tuple[int, dict]): a coupled a tuple of the response code and a JSONified version
            of the information stored in ResponseCode
        '''
        response_body = {
            "status": "success" if self.__success else "error",
            "code_tag": self.__error_tag,
            "message": self.__message
        }
        if self.__data is not None:
            response_body["data"] = self.__data

        return self.__error_code, response_body
