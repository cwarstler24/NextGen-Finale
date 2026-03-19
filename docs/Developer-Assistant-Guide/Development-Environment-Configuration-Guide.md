---
description: To test The Frying Saucer application, you must have a virtual environment established and packages installed.
---

# Development Environment Configuration Guide

To test The Frying Saucer application, you must have a virtual environment established and packages installed.

**Prerequisites**  

- `credentials.json` file
- `requirements.txt` file
- `uvicorn`, `pytest`, and `npm` installed
- `package.json` file

## Setting up the virtual environment

Follow these steps to set up your local development environment.

1. Create a Python Virtual Environment
`python -m venv venv`

1. Activate the virtual environment
`.\venv\Scripts\activate`

1. Run `pip install -r .\requirements.txt`.

    !!! note "note"
        You must have a requirements.txt file. In the requirements.txt file, you must have all of the pip packages such as `pylint`, `uvicorn`, and `pytest` integrated into the file.

1. You should get a **successfully installed** message your terminal.

## Testing the frontend

1. Run `npm i`. This installs the front end packages.

    !!! note "note"
        `npm i` installs everything in the package.json file.

1. Run `npm run <script>`. A response from Vite will appear and you will see the frontend running locally on your server. You can find a list of scripts in `package.json`.

## Configuring credentials.json file

!!! note "note"
    You must have a DB2 license before creating a credentials.json file. Request a DB2 license from your supervisor if you do not have one.

1. Create a `credentials.json` file. This file makes a connection with the DB2 database.

1. Insert appropriate values into this file regarding your specific database values and configuration.

1. Install the DB2 license, `db2consv_ee.lic`. This file will go inside the directory of `/clidriver`.

## Testing the backend

1. Run `uvicorn main.backend.server:app`

1. Run `python .\main\backend\daotest.py`

    !!! note "note"
        This command displays what is in your database.
