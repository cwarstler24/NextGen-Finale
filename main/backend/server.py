from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.backend.DAOfactory import DAOFactory
from main.utilities.sanitizer import sanitize_and_unmarshal
from main.backend.entities import Customer
from main.utilities.logger import LoggerFactory
from main.utilities.sanitizer import sanitize_email

# Initialize logger
LOGGER = LoggerFactory.get_general_logger()

from fastapi.middleware.cors import CORSMiddleware

# ==================== Lifespan Event Handler ====================


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # Startup
    LOGGER.info("FastAPI server starting up...", also_print=True)
    LOGGER.info("Connection pool initialized and ready", also_print=True)

    yield  # Server is running

    # Shutdown
    LOGGER.info("FastAPI server shutting down...", also_print=True)
    # Connection pool cleanup if needed
    # from main.backend.db_pool import db_pool
    # db_pool.close_all()

# Create FastAPI app instance with lifespan handler
app = FastAPI(
    title="Restaurant Order API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Pydantic Models ====================

# --- Fries Models ---


class FrySizeItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class FryTypeItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class FrySeasoningItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class FriesResponse(BaseModel):
    sizes: List[FrySizeItem]
    types: List[FryTypeItem]
    seasonings: List[FrySeasoningItem]

# --- Burger Models ---


class BunItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class PattyItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class ToppingItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class BurgerResponse(BaseModel):
    buns: List[BunItem]
    patties: List[PattyItem]
    toppings: List[ToppingItem]

# --- Customer Models ---


class OrderSummary(BaseModel):
    date: datetime
    price: float


class CustomerResponse(BaseModel):
    name: str
    email: EmailStr
    shipping_address: str
    billing_address: str
    orders: List[OrderSummary]

# --- Order Models (POST) ---


class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    shipping_address: str
    billing_address: str


class BurgerOrder(BaseModel):
    bun_id: int
    patty_id: int
    patty_count: int = 1
    topping_ids: List[int]


class FriesOrder(BaseModel):
    size_id: int
    type_id: int
    seasoning_id: int


class OrderRequest(BaseModel):
    customer: CustomerInfo
    burgers: List[BurgerOrder]
    fries: List[FriesOrder]
    date: Optional[datetime] = None


class OrderResponse(BaseModel):
    order_id: int
    message: str
    total_price: float

# ==================== API Endpoints ====================


@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    return {
        "message": "Restaurant Order API",
        "version": "1.0.0",
        "status": "operational"
    }

# --- GET /Items/Fries ---


@app.get("/Items/Fries", response_model=FriesResponse)
async def get_fries_items():
    """
    Get all available fry sizes, types, and seasonings with pricing and stock.
    Thread-safe operation using connection pool.
    """
    try:
        LOGGER.info("GET /Items/Fries - Fetching fry items", also_print=True)

        # Get DAOs from factory
        size_dao = DAOFactory.get_or_create_dao("FrySizeDAO")
        type_dao = DAOFactory.get_or_create_dao("FryTypeDAO")
        seasoning_dao = DAOFactory.get_or_create_dao("FrySeasoningDAO")

        # Fetch all records
        sizes_result = size_dao.get_all_records()
        types_result = type_dao.get_all_records()
        seasonings_result = seasoning_dao.get_all_records()

        # Check for errors
        if not sizes_result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch fry sizes")
        if not types_result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch fry types")
        if not seasonings_result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch fry seasonings")

        # Marshall data into response format
        sizes = [
            {
                "id": item["FRY_SIZE_ID"],
                "name": f"{item['FRY_SIZE']} oz",
                "price": float(item["PRICE"]),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in sizes_result.data
        ]

        types = [
            {
                "id": item["FRY_TYPE_ID"],
                "name": item["FRY_TYPE_NAME"],
                "price": float(item["PRICE"]),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in types_result.data
        ]

        seasonings = [
            {
                "id": item["FRY_SEASONING_ID"],
                "name": item["FRY_SEASONING_NAME"],
                "price": float(item["PRICE"]),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in seasonings_result.data
        ]

        return {
            "sizes": sizes,
            "types": types,
            "seasonings": seasonings
        }

    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error fetching fry items: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch fry items: {str(e)}") from e

# --- GET /Items/Burger ---


@app.get("/Items/Burger", response_model=BurgerResponse)
async def get_burger_items():
    """
    Get all available buns, patties, and toppings with pricing and stock.
    Thread-safe operation using connection pool.
    """
    try:
        LOGGER.info(
            "GET /Items/Burger - Fetching burger items",
            also_print=True)

        # Get DAOs from factory
        bun_dao = DAOFactory.get_or_create_dao("BunTypeDAO")
        patty_dao = DAOFactory.get_or_create_dao("PattyTypeDAO")
        topping_dao = DAOFactory.get_or_create_dao("ToppingDAO")

        # Fetch all records
        buns_result = bun_dao.get_all_records()
        patties_result = patty_dao.get_all_records()
        toppings_result = topping_dao.get_all_records()

        # Check for errors
        if not buns_result.success:
            raise HTTPException(status_code=500, detail="Failed to fetch buns")
        if not patties_result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch patties")
        if not toppings_result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch toppings")

        # Marshall data into response format
        buns = [
            {
                "id": item["BUN_ID"],
                "name": item["BUN_NAME"],
                "price": float(item["PRICE"]),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in buns_result.data
        ]

        patties = [
            {
                "id": item["PATTY_ID"],
                "name": item["PATTY_NAME"],
                "price": float(item["PRICE"]),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in patties_result.data
        ]

        toppings = [
            {
                "id": item["TOPPING_ID"],
                "name": item["TOPPING_NAME"],
                "price": float(item["PRICE"]),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in toppings_result.data
        ]

        return {
            "buns": buns,
            "patties": patties,
            "toppings": toppings
        }

    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error fetching burger items: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch burger items: {str(e)}") from e

# --- GET /Customer/{email} ---


@app.get("/Customer/{email}", response_model=CustomerResponse)
async def get_customer(email: str):
    """
    Get customer information and order history by email.
    Thread-safe operation using connection pool.

    Args:
        email (str): Customer email address
    """
    try:
        # Sanitize email input
        sanitized_email = sanitize_email(email)

        LOGGER.info(
            f"GET /Customer/{sanitized_email} - Fetching customer data",
            also_print=True)

        # Get DAOs from factory
        customer_dao = DAOFactory.get_or_create_dao("CustomerDAO")

        # Fetch customer with orders using the join method
        customer_result = customer_dao.get_customer_with_orders(
            sanitized_email)

        # Check if customer exists
        if not customer_result.success:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with email '{sanitized_email}' not found")

        # The join query returns a list of rows (one per order, or one if no
        # orders)
        if not customer_result.data or len(customer_result.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with email '{sanitized_email}' not found")

        # Get customer info from first row
        first_row = customer_result.data[0]
        customer_info = {
            "name": first_row["NAME"],
            "email": first_row["EMAIL"],
            "shipping_address": first_row["SHIP_ADDR"],
            "billing_address": first_row["BILL_ADDR"]
        }

        # Marshall orders (filter out rows with no order - LEFT JOIN can have
        # NULL ORDER_ID)
        orders = []
        for row in customer_result.data:
            if row.get("ORDER_ID") is not None:
                orders.append({
                    "date": row["PURCHASE_DATE"],
                    "price": float(row["TOTAL_PRICE"])
                })

        return {
            **customer_info,
            "orders": orders
        }

    except HTTPException:
        raise
    except ValueError as e:
        LOGGER.error(f"Validation error for email {email}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid email format: {str(e)}") from e
    except Exception as e:
        LOGGER.error(f"Error fetching customer {email}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch customer: {str(e)}") from e

# --- POST /Order/ ---


@app.post("/Order/", response_model=OrderResponse)
async def create_order(order: OrderRequest):
    """
    Create a new order with customer info, burgers, and fries.
    Thread-safe operation using connection pool.
    Handles transactions across multiple tables.

    Args:
        order (OrderRequest): Complete order information including customer, items, and date
    """
    try:
        LOGGER.info(
            f"POST /Order/ - Creating order for {order.customer.email}", also_print=True)

        # Sanitize and unmarshal customer data
        customer_data = order.customer.model_dump()
        customer_entity = sanitize_and_unmarshal(customer_data, Customer)

        LOGGER.debug(f"Sanitized customer: {customer_entity}")

        # Sanitize burger orders
        sanitized_burgers = []
        for burger_data in order.burgers:
            burger_dict = burger_data.model_dump()
            # Validate burger components exist (would query DAOs here)
            sanitized_burgers.append(burger_dict)

        # Sanitize fry orders
        sanitized_fries = []
        for fry_data in order.fries:
            fry_dict = fry_data.model_dump()
            # Validate fry components exist (would query DAOs here)
            sanitized_fries.append(fry_dict)

        LOGGER.debug(
            f"Sanitized {len(sanitized_burgers)} burgers and {len(sanitized_fries)} fries")

        # Get all DAOs
        customer_dao = DAOFactory.get_or_create_dao("CustomerDAO")
        order_dao = DAOFactory.get_or_create_dao("OrderDAO")
        order_item_dao = DAOFactory.get_or_create_dao("OrderItemDAO")
        burger_item_dao = DAOFactory.get_or_create_dao("BurgerItemDAO")
        burger_topping_dao = DAOFactory.get_or_create_dao(
            "BurgerItemToppingDAO")
        fry_item_dao = DAOFactory.get_or_create_dao("FryItemDAO")

        # Ingredient DAOs for price calculation
        bun_dao = DAOFactory.get_or_create_dao("BunTypeDAO")
        patty_dao = DAOFactory.get_or_create_dao("PattyTypeDAO")
        topping_dao = DAOFactory.get_or_create_dao("ToppingDAO")
        fry_type_dao = DAOFactory.get_or_create_dao("FryTypeDAO")
        fry_size_dao = DAOFactory.get_or_create_dao("FrySizeDAO")
        fry_seasoning_dao = DAOFactory.get_or_create_dao("FrySeasoningDAO")

        # 1. Check/Create customer
        existing_customer = customer_dao.get_by_key(
            customer_entity.get_primary_key())
        if not existing_customer.success or not existing_customer.data:
            LOGGER.info(f"Creating new customer: {customer_entity.email}")
            customer_create_result = customer_dao.create_record(
                customer_entity.to_dict())
            if not customer_create_result.success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create customer")

        # 2. Generate IDs - get max IDs and increment
        all_orders = order_dao.get_all_records()
        next_order_id = 1 if (not all_orders.success or not all_orders.data) else max(
            [o["ORDER_ID"] for o in all_orders.data]) + 1

        all_order_items = order_item_dao.get_all_records()
        next_order_item_id = 1 if (not all_order_items.success or not all_order_items.data) else max(
            [oi["ORDER_ITEM_ID"] for oi in all_order_items.data]) + 1

        all_burger_items = burger_item_dao.get_all_records()
        next_burger_id = 1 if (not all_burger_items.success or not all_burger_items.data) else max(
            [b["BURGER_ID"] for b in all_burger_items.data]) + 1

        all_fry_items = fry_item_dao.get_all_records()
        next_fry_id = 1 if (not all_fry_items.success or not all_fry_items.data) else max(
            [f["FRY_ID"] for f in all_fry_items.data]) + 1

        # 3. Validate ingredients and calculate prices (but don't create items
        # yet)
        total_price = 0.0
        order_qty = len(sanitized_burgers) + len(sanitized_fries)

        # Prepare burger data
        burger_items_to_create = []
        for burger in sanitized_burgers:
            # Get ingredient prices
            bun_result = bun_dao.get_by_key(burger["bun_id"])
            patty_result = patty_dao.get_by_key(burger["patty_id"])

            if not bun_result.success or not bun_result.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid bun ID: {burger['bun_id']}")
            if not patty_result.success or not patty_result.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid patty ID: {burger['patty_id']}")

            bun_price = float(bun_result.data["PRICE"])
            patty_price = float(patty_result.data["PRICE"])
            burger_price = bun_price + patty_price

            # Validate and add topping prices
            for topping_id in burger["topping_ids"]:
                topping_result = topping_dao.get_by_key(topping_id)
                if not topping_result.success or not topping_result.data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid topping ID: {topping_id}")
                burger_price += float(topping_result.data["PRICE"])

            # Store burger data for later creation
            burger_items_to_create.append({
                "burger_data": burger,
                "price": burger_price
            })
            total_price += burger_price

        # Prepare fry data
        fry_items_to_create = []
        for fry in sanitized_fries:
            # Get ingredient prices
            fry_type_result = fry_type_dao.get_by_key(fry["type_id"])
            fry_size_result = fry_size_dao.get_by_key(fry["size_id"])
            fry_seasoning_result = fry_seasoning_dao.get_by_key(
                fry["seasoning_id"])

            if not fry_type_result.success or not fry_type_result.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid fry type ID: {fry['type_id']}")
            if not fry_size_result.success or not fry_size_result.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid fry size ID: {fry['size_id']}")
            if not fry_seasoning_result.success or not fry_seasoning_result.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid fry seasoning ID: {fry['seasoning_id']}")

            fry_price = (float(fry_type_result.data["PRICE"]) +
                         float(fry_size_result.data["PRICE"]) +
                         float(fry_seasoning_result.data["PRICE"]))

            # Store fry data for later creation
            fry_items_to_create.append({
                "fry_data": fry,
                "price": fry_price
            })
            total_price += fry_price

        # 4. Create ORDER record FIRST (so foreign key constraint is satisfied)
        order_date = order.date if order.date else datetime.now()
        order_record = {
            "ORDER_ID": next_order_id,
            "EMAIL": customer_entity.email,
            "PURCHASE_DATE": order_date,
            "ORDER_QTY": order_qty,
            "TOTAL_PRICE": total_price
        }
        order_create_result = order_dao.create_record(order_record)
        if not order_create_result.success:
            raise HTTPException(
                status_code=500,
                detail="Failed to create order")

        # 5. Now create ORDER_ITEMS and associated items (order exists now)
        # Process burgers
        for burger_item_data in burger_items_to_create:
            burger = burger_item_data["burger_data"]
            burger_price = burger_item_data["price"]

            # Create order item
            order_item = {
                "ORDER_ITEM_ID": next_order_item_id,
                "ORDER_ID": next_order_id,
                "ITEM_TYPE": "BURGER",
                "UNIT_PRICE": burger_price
            }
            order_item_result = order_item_dao.create_record(order_item)
            if not order_item_result.success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create order item")

            # Create burger item
            burger_item = {
                "BURGER_ID": next_burger_id,
                "ORDER_ITEM_ID": next_order_item_id,
                "BUN_TYPE": burger["bun_id"],
                "PATTY_TYPE": burger["patty_id"],
                "PATTY_COUNT": burger.get("patty_count", 1)
            }
            burger_create_result = burger_item_dao.create_record(burger_item)
            if not burger_create_result.success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create burger item")

            # Create burger toppings
            for topping_id in burger["topping_ids"]:
                burger_topping = {
                    "BURGER_ORDER_ID": next_burger_id,
                    "TOPPING_ID": topping_id
                }
                topping_create_result = burger_topping_dao.create_record(
                    burger_topping)
                if not topping_create_result.success:
                    raise HTTPException(
                        status_code=500, detail="Failed to create burger topping")

            next_order_item_id += 1
            next_burger_id += 1

        # Process fries
        for fry_item_data in fry_items_to_create:
            fry = fry_item_data["fry_data"]
            fry_price = fry_item_data["price"]

            # Create order item
            order_item = {
                "ORDER_ITEM_ID": next_order_item_id,
                "ORDER_ID": next_order_id,
                "ITEM_TYPE": "FRIES",
                "UNIT_PRICE": fry_price
            }
            order_item_result = order_item_dao.create_record(order_item)
            if not order_item_result.success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create order item")

            # Create fry item
            fry_item = {
                "FRY_ID": next_fry_id,
                "ORDER_ITEM_ID": next_order_item_id,
                "FRY_TYPE": fry["type_id"],
                "FRY_SIZE": fry["size_id"],
                "FRY_SEASONING": fry["seasoning_id"]
            }
            fry_create_result = fry_item_dao.create_record(fry_item)
            if not fry_create_result.success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create fry item")

            next_order_item_id += 1
            next_fry_id += 1

        LOGGER.info(
            f"Order {next_order_id} created successfully with total ${total_price:.2f}")

        return {
            "order_id": next_order_id,
            "message": "Order created successfully",
            "total_price": total_price
        }

    except HTTPException:
        raise
    except ValueError as e:
        LOGGER.error(f"Validation error creating order: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order data: {str(e)}") from e
    except Exception as e:
        LOGGER.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create order: {str(e)}") from e

# ==================== Error Handlers ====================


@app.exception_handler(Exception)
async def global_exception_handler(_request, exc):
    """Global exception handler for uncaught errors"""
    LOGGER.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
