# Copyright (C) 2025 Team White
# Licensed under the MIT License
# See LICENSE for more details

"""
Test Data Population Utility
Populates the test database with predefined test data from database_setup.json
"""

import sys
from pathlib import Path
from typing import Dict, Any, cast

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main.backend.db_pool import db_pool
from main.utilities.logger import LoggerFactory

LOGGER = LoggerFactory.get_general_logger()


def main():
    """Main function to populate test data"""
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("TEST DATA POPULATION UTILITY", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    # Check environment
    environment = db_pool.get_environment()
    schema = db_pool.get_schema()

    LOGGER.info(f"Environment: {environment}", also_print=True)
    LOGGER.info(f"Schema: {schema}", also_print=True)
    LOGGER.info("", also_print=True)

    if not db_pool.is_test_environment():
        LOGGER.error(
            "ERROR: This utility can only be run in TEST environment!",
            also_print=True
        )
        LOGGER.error(
            "Please set 'environment' to 'TEST' in database_setup.json",
            also_print=True
        )
        return 1

    # Confirm action
    LOGGER.info(
        "WARNING: This will DELETE all existing data in test tables!",
        also_print=True
    )
    response = input("Do you want to continue? (yes/no): ")

    if response.lower() not in ["yes", "y"]:
        LOGGER.info("Operation cancelled.", also_print=True)
        return 0

    LOGGER.info("", also_print=True)
    LOGGER.info("Populating test data...", also_print=True)
    LOGGER.info("", also_print=True)

    # Populate test data
    results: Dict[str, Any] = db_pool.populate_test_data()

    # Check if operation was blocked (non-TEST environment)
    if "status" in results and results.get("status") == "blocked":
        LOGGER.error(
            f"[BLOCKED] {results.get('reason', 'Unknown reason')}",
            also_print=True
        )
        return 1

    # Display results
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info("RESULTS", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    total_inserted = 0
    total_errors = 0

    for table_name, result in results.items():
        # result should be a dict with status, inserted, etc.
        if not isinstance(result, dict):
            LOGGER.warning(f"[WARNING] {table_name}: Unexpected result type", also_print=True)
            continue

        # Explicitly cast to dict for type checker
        result_data = cast(Dict[str, Any], result)
        status = result_data.get("status", "unknown")  # pyright: ignore[reportAttributeAccessIssue]
        inserted = result_data.get("inserted", 0)  # pyright: ignore[reportAttributeAccessIssue]

        if status == "success":
            LOGGER.info(
                f"[SUCCESS] {table_name}: {inserted} rows inserted",
                also_print=True
            )
            total_inserted += inserted
        elif status == "empty":
            LOGGER.info(
                f"[SKIPPED] {table_name}: No test data defined",
                also_print=True
            )
        elif status == "error":
            error_msg = result_data.get("error", "Unknown error")  # pyright: ignore[reportAttributeAccessIssue]
            LOGGER.error(
                f"[ERROR] {table_name}: {error_msg}",
                also_print=True
            )
            total_errors += 1

    LOGGER.info("", also_print=True)
    LOGGER.info("=" * 60, also_print=True)
    LOGGER.info(f"Total rows inserted: {total_inserted}", also_print=True)
    LOGGER.info(f"Total errors: {total_errors}", also_print=True)
    LOGGER.info("=" * 60, also_print=True)

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
