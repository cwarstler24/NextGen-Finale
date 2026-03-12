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
    "INTERNAL_SERVER_ERROR": (500, "An unexpected error occurred on the server.")
}

class ResponseCode:
    '''
    This class wraps a detailed HTTP response code with a custom message and added data and automatically
    logs this result
    '''
    def __init__(self, error_tag: str = "", data: Optional[Any] = None):
        '''
        Args:
            error_tag (str): the name of error that will be passed to the RESPONSE_MAP to get the HTTP error code
            data (any optional): extra data from the operation or error to be sent with the response (defaults to None)
        '''
        self.__logger = LoggerFactory.get_general_logger()
        self.__error_tag = error_tag
        #Defualt to 500 error if it cannot be found in look-up table
        self.__error_code, self.__message = _RESPONSE_MAP.get(error_tag, (500, "An unexpected error occurred."))
        self.__success = (self.__error_code < 300)
        self.__data = data
        if(not self.__success):
            self.__logger.error(f"{self.__error_code}. {error_tag}: {self.__message}\n\t\t\tdata: {self.__data}")
        else:
            self.__logger.info(f"{self.__error_code}. {error_tag}: {self.__message}\n\t\t\tdata: {self.__data}")

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