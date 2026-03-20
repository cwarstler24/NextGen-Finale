---
description: You must have a virtual environment established and packages installed to test The Frying Saucer application.
---

# Development Environment Configuration Guide

**Prerequisites**  

- `credentials.json` file
- `requirements.txt` file
- `uvicorn`, `pytest`, and `npm` installed
- `package.json` file

## Setting up the virtual environment

To set up the virtual environment, you must have a requirements.txt file. In the requirements.txt file, you must have all of the pip packages such as `pylint`, `uvicorn`, and `pytest` integrated into the file.

1. Create a Python Virtual Environment
`python -m venv venv`

1. Activate the virtual environment
`.\venv\Scripts\activate`

1. Run `pip install -r .\requirements.txt`.

1. You should get a **successfully installed** message your terminal.

## Testing the frontend

1. Run `npm i`. This installs the front end packages.

    !!! note "note"
        `npm i` installs everything in the package.json file.

1. Run `npm run <script>`. A response from Vite will appear and you will see the frontend running locally on your server. You can find a list of scripts in `package.json`.

## Configuring credentials.json file

You must have a DB2 license before creating a `credentials.json` file. Request a DB2 license from your supervisor if you do not have one. The `credentials.json` file will originally be named `credentials_template.json`. You must change the name to `credentials.json` and fill in the appropriate values for your database connection. You can find the `credentials_template.json` file in the main directory of the repository.

1. Create a `credentials.json` file. This file makes a connection with the DB2 database.

1. Insert appropriate values into this file regarding your specific database values and configuration.

        a. Use the following template:

        ```json
        {
            "database": "[database]",
            "hostname": "192.168.54.250",
            "port": "3600",
            "protocol": "TCPIP",
            "authentication": "SERVER",
            "uid": "[username]",
            "pwd": "[password]"
        }
        ```

1. Install the DB2 license, `db2consv_ee.lic`. This file will go inside the directory of `/clidriver/license`.

## Testing the database connection

1. In the `database_setup.json` file, you can change the environment to **PRODUCTION** to test the database connection. You can change the environment to **TEST** to use the test database connection.

    !!! note "note"
        The `database_setup.json` file is located in the main directory of the repository. You **must** have the `credentials.json` file set up and configured correctly to test the database connection.

1. This is an example of what the `database_setup.json` file should look like:

        ```json
        {
            "environment": "PRODUCTION",
            "schemas": {
                "PRODUCTION": "[production_schema]",
                "TEST": "[test_schema]"
            }
        }
        ```

## Testing the backend

1. Run `uvicorn main.backend.server:app`

1. Run `python .\main\backend\daotest.py`

    !!! note "note"
        This command displays what is in the database.
