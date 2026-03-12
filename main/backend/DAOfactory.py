# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.backend.AbstractDAO import DatabaseAccessObject
from main.backend.customerDAO import CustomerDAO
from main.backend.orderDAO import OrderDAO
from main.backend.orderItemDAO import OrderItemDAO
from main.backend.burgerItemDAO import BurgerItemDAO
from main.backend.burgerItemToppingDAO import BurgerItemToppingDAO
from main.backend.fryItemDAO import FryItemDAO
from main.backend.bunTypeDAO import BunTypeDAO
from main.backend.pattyTypeDAO import PattyTypeDAO
from main.backend.toppingDAO import ToppingDAO
from main.backend.fryTypeDAO import FryTypeDAO
from main.backend.frySizeDAO import FrySizeDAO
from main.backend.frySeasoningDAO import FrySeasoningDAO

'''
dao_factory.py

This module allows a singular instance of each DAO to be made without accidentally creating more.
The DB2 connection pool is managed separately in db_pool.py and shared across all DAOs.

Functions:
    -create_dao <classmethod>: creates a DAO for the specified type and returns it; it will raise an
    error if one exists
    -get_dao <classmethod>: returns the DAO of a given type if it exists
    -reset <classmethod>: if (for whatever unknown reason???) you need to reset the DAOs, you can clarify
    which one or reset all
'''

_DAO_REGISTRY = {
    "CustomerDAO": CustomerDAO,
    "OrderDAO": OrderDAO,
    "OrderItemDAO": OrderItemDAO,
    "BurgerItemDAO": BurgerItemDAO,
    "BurgerItemToppingDAO": BurgerItemToppingDAO,
    "FryItemDAO": FryItemDAO,
    "BunTypeDAO": BunTypeDAO,
    "PattyTypeDAO": PattyTypeDAO,
    "ToppingDAO": ToppingDAO,
    "FryTypeDAO": FryTypeDAO,
    "FrySizeDAO": FrySizeDAO,
    "FrySeasoningDAO": FrySeasoningDAO,
}

class DAOFactory:
    '''
    Factory for DB2 DAOs to ensure only one instance per sub-class exists.
    This allows for dependency injection without the drawbacks of a global Singleton object.
    The DB2 connection pool is initialized automatically when db_pool.py is imported.
    
    List of acceptable DAO tables:
    "CustomerDAO"
    "OrderDAO"
    "OrderItemDAO"
    "BurgerItemDAO"
    "BurgerItemToppingDAO"
    "FryItemDAO"
    "BunTypeDAO"
    "PattyTypeDAO"
    "ToppingDAO"
    "FryTypeDAO"
    "FrySizeDAO"
    "FrySeasoningDAO"
    '''

    _instances: dict[str, DatabaseAccessObject] = {}

    @classmethod
    def list_active(cls) -> list[str]:
        '''
        Returns a list of all currently instantiated DAO names.
        
        Returns:
            list[str]: List of active DAO class names
        '''
        return list(cls._instances.keys())

    @classmethod
    def create_dao(cls, dao_class_name: str) -> DatabaseAccessObject:
        '''
        Creates a DAO of the given class. If one exists, it raises an error.
        The DAO will automatically use the DB2 connection pool.

        Args:
            dao_class_name (str): a string that represents the DAO class name; must be in the _DAO_REGISTRY

        Returns:
            instance (DatabaseAccessObject): a DatabaseAccessObject of the given dao_class_name string
        '''
        # If the given type has not been registered, throw an error
        dao_class = _DAO_REGISTRY.get(dao_class_name)
        if not dao_class:
            raise RuntimeError(f"DAO type '{dao_class_name}' has not been registered. Try a valid identifier.")
        if dao_class_name in cls._instances:
            raise RuntimeError(f"{dao_class_name} instance already created. Use get_dao() to access it.")
        
        # Create the DAO instance (it will use the connection pool automatically)
        instance = dao_class()
        cls._instances[dao_class_name] = instance
        return instance

    @classmethod
    def get_dao(cls, dao_class_name: str) -> DatabaseAccessObject:
        '''
        Returns a DAO if it exists; otherwise, raises an error.

        Args:
            dao_class_name (str): a string that represents the DAO class name; must be in the _DAO_REGISTRY

        Returns:
            instance (DatabaseAccessObject): a DatabaseAccessObject of the given dao_class_name string
        '''
        if dao_class_name not in cls._instances:
            raise RuntimeError(f"{dao_class_name} instance not yet created. Use create_dao() first.")
        return cls._instances[dao_class_name]

    @classmethod
    def get_or_create_dao(cls, dao_class_name: str) -> DatabaseAccessObject:
        '''
        Returns an existing DAO or creates it if it doesn't exist.
        Convenience method to avoid checking existence.

        Args:
            dao_class_name (str): a string that represents the DAO class name; must be in the _DAO_REGISTRY

        Returns:
            instance (DatabaseAccessObject): a DatabaseAccessObject of the given dao_class_name string
        '''
        if dao_class_name in cls._instances:
            return cls._instances[dao_class_name]
        return cls.create_dao(dao_class_name)

    @classmethod
    def reset(cls, dao_class_name: Optional[str] = None):
        '''
        Resets either a specific DAO (if given a dao_class_name) or all of them.
        Note: This does not close the DB2 connection pool.

        Args:
            dao_class_name (str optional): a string that represents the DAO class name; must be in the _DAO_REGISTRY
        '''
        if dao_class_name:
            cls._instances.pop(dao_class_name, None)
        else:
            cls._instances.clear()