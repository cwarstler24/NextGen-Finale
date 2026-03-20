---
description: Local REST API for The Frying Saucer ordering system. TFS API supports menu browsing, customer lookup, and order creation.
---

# Getting Started with The Frying Saucer API

The Frying Saucer API is a **local REST API** used to support menu browsing, customer lookup, and order creation.

The TFS API is designed for:

- Local development and testing
- Demonstrating RESTful API design
- Supporting frontend and integration testing
- CI/CD validation using GitHub Actions

!!! note "note"
    This API runs locally and does not require authentication or API keys.

## Running the API Locally

You must be on Rocket's VPN to access the TFS API. The API is built using **FastAPI** and can be started with a single command. The TFS API is ran on `http://localhost:8000` by default.

**Prerequisites**  

- Fast API
- Python
- Git

**Start the API**  

- Run `uvicorn main.backend.server:app --reload`

## TFS API Error Codes

| Status Code | Description |
| ----------- | ----------- |
| 200 OK | Successful request |
| 400 Bad Request | Invalid input or missing required fields |
| 403 Forbidden | Access denied to the resource |
| 404 Not Found | Resource not found |
| 405 Method Not Allowed | HTTP method not supported for the endpoint |
| 409 Conflict | Resource conflict (e.g., duplicate order) |
| 500 Internal Server Error | Unexpected error on the server |
| 503 Database Connection Failed | Unable to connect to the database |

## Endpoints

**GET /Items/Fries**  

| Route | | Endpoint | | Description | | Variables |
| ------ | -- | ---------- | -- | ------------- | -- | ----------- |
| GET | | /Items/Fries | | Returns all available fries configuration options | - | Size, Type, Seasoning |

| Variable | | Fields |
| --------- | -- | -------- |
| Size | | Id, Name, Price, Quantity |
| Type | | Id, Name, Price, Quantity |
| Seasoning | | Id, Name, Price, Quantity |

**GET /Items/Burger**  

| Route | | Endpoint | | Description | | Variables |
| ------ | -- | ---------- | -- | ------------- | -- | ----------- |
| GET | | /Items/Burger | | Returns all available burger components | | Bun, Patty, Topping |

| Variable | | Fields |
| --------- | -- | -------- |
| Bun | | Id, Name, Price, Quantity |
| Patty | | Id, Name, Price, Quantity |
| Topping | | Id, Name, Price, Quantity |

**GET /Customer/{email}**  

| Route | | Endpoint | | Description | | Variables |
| ------ | -- | ---------- | -- | ------------- | -- | ----------- |
| GET | | /Customer/{email} | | Retrieves customer details and order history by email | | Name, Email, ShippingAddress, BillingAddress, Order |

| Variable | | Fields |
| --------- | -- | -------- |
| Order | | Date, Price |

**POST /Order**  

| Route | | Endpoint | | Description | | Variables |
| ------ | -- | ---------- | -- | ------------- | -- | ----------- |
| POST | | /Order | | Creates a new order for a customer | | Customer, Burger, Fries, Date |

| Variable | | Fields |
| --------- | -- | -------- |
| Customer | | Name, Email, ShippingAddress, BillingAddress |
| Burger | | Bun_id, Patty_id, Patty_Count, Topping |
| Topping | | Id, Quantity |
| Fries | | Size_id, Type_id, Seasoning_id |
