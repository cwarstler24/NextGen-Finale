from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import sys
import time
import random
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main.backend.DAOfactory import DAOFactory
from main.utilities.sanitizer import sanitize_and_unmarshal
from main.backend.entities import Customer
from main.utilities.logger import LoggerFactory
from main.utilities.sanitizer import sanitize_email
from main.backend.db_pool import get_db_cursor

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
    # Note: No quantity field - sizes are multipliers, not inventory


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


class OrderItemSummary(BaseModel):
    item_type: str
    name: str
    price: float


class OrderSummary(BaseModel):
    order_id: int
    date: datetime
    price: float
    items: List[OrderItemSummary]


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


class ToppingSelection(BaseModel):
    topping_id: int
    count: int = 1


class BurgerOrder(BaseModel):
    bun_id: Optional[int] = None
    patty_id: Optional[int] = None
    patty_count: int = 1
    toppings: List[ToppingSelection] = Field(default_factory=list)
    topping_ids: Optional[List[int]] = None


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
                "price": round(float(item["PRICE"]), 2)
                # Note: Fry sizes don't have stock_quantity - they're just size multipliers
            }
            for item in sizes_result.data
        ]

        types = [
            {
                "id": item["FRY_TYPE_ID"],
                "name": item["FRY_TYPE_NAME"],
                "price": round(float(item["PRICE"]), 2),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in types_result.data
        ]

        seasonings = [
            {
                "id": item["FRY_SEASONING_ID"],
                "name": item["FRY_SEASONING_NAME"],
                "price": round(float(item["PRICE"]), 2),
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
                "price": round(float(item["PRICE"]), 2),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in buns_result.data
        ]

        patties = [
            {
                "id": item["PATTY_ID"],
                "name": item["PATTY_NAME"],
                "price": round(float(item["PRICE"]), 2),
                "quantity": item["STOCK_QUANTITY"]
            }
            for item in patties_result.data
        ]

        toppings = [
            {
                "id": item["TOPPING_ID"],
                "name": item["TOPPING_NAME"],
                "price": round(float(item["PRICE"]), 2),
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

        # Get customer DAO from factory
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

        order_item_dao = DAOFactory.get_or_create_dao("OrderItemDAO")
        burger_item_dao = DAOFactory.get_or_create_dao("BurgerItemDAO")

        # Marshall orders (filter out rows with no order - LEFT JOIN can have
        # NULL ORDER_ID)
        order_ids = [
            row["ORDER_ID"] for row in customer_result.data
            if row.get("ORDER_ID") is not None
        ]

        # Batch-fetch all burgers and fries for all orders in 2 queries
        all_burgers = []
        all_fries = []
        if order_ids:
            burgers_result = order_item_dao.get_burgers_for_orders(order_ids)
            if burgers_result.success and burgers_result.data:
                all_burgers = burgers_result.data

            fries_result = order_item_dao.get_fries_for_orders(order_ids)
            if fries_result.success and fries_result.data:
                all_fries = fries_result.data

        # Batch-fetch all toppings for all burgers in 1 query
        burger_ids = [b["BURGER_ID"] for b in all_burgers]
        all_toppings = []
        if burger_ids:
            toppings_result = burger_item_dao.get_toppings_for_burgers(burger_ids)
            if toppings_result.success and toppings_result.data:
                all_toppings = toppings_result.data

        # Group toppings by burger ID for fast lookup
        toppings_by_burger = {}
        for topping in all_toppings:
            bid = topping["BURGER_ID"]
            if bid not in toppings_by_burger:
                toppings_by_burger[bid] = []
            toppings_by_burger[bid].append(topping)

        # Group burgers and fries by order ID
        burgers_by_order = {}
        for burger in all_burgers:
            oid = burger["ORDER_ID"]
            if oid not in burgers_by_order:
                burgers_by_order[oid] = []
            burgers_by_order[oid].append(burger)

        fries_by_order = {}
        for fry in all_fries:
            oid = fry["ORDER_ID"]
            if oid not in fries_by_order:
                fries_by_order[oid] = []
            fries_by_order[oid].append(fry)

        # Assemble the response
        orders = []
        for row in customer_result.data:
            if row.get("ORDER_ID") is not None:
                order_id = row["ORDER_ID"]
                items = []

                # Process burgers for this order
                for burger in burgers_by_order.get(order_id, []):
                    patty_count = burger.get("PATTY_COUNT", 1)
                    patty_text = f"{patty_count} {
                        burger['PATTY_NAME']}" if patty_count > 1 else burger['PATTY_NAME']

                    # Look up toppings from pre-fetched data
                    topping_names = [
                        t["TOPPING_NAME"]
                        for t in toppings_by_burger.get(burger["BURGER_ID"], [])
                    ]

                    burger_name = f"{burger['BUN_NAME']} with {patty_text}"
                    if topping_names:
                        burger_name += f" and {', '.join(topping_names)}"

                    items.append({
                        "item_type": "Burger",
                        "name": burger_name,
                        "price": round(float(burger["UNIT_PRICE"]), 2)
                    })

                # Process fries for this order
                for fry in fries_by_order.get(order_id, []):
                    items.append({
                        "item_type": "Fries",
                        "name": f"{fry['SIZE_VALUE']}oz {fry['TYPE_NAME']} with {fry['SEASONING_NAME']}",
                        "price": round(float(fry["UNIT_PRICE"]), 2)
                    })

                orders.append({
                    "order_id": order_id,
                    "date": row["PURCHASE_DATE"],
                    "price": round(float(row["TOTAL_PRICE"]), 2),
                    "items": items
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


def _execute_order_creation(order: OrderRequest, max_retries: int = 3):
    """
    Execute order creation with retry logic for duplicate key errors (race conditions).
    
    Args:
        order: The order request data
        max_retries: Maximum number of retry attempts
        
    Returns:
        dict: Order creation response
        
    Raises:
        HTTPException: If order creation fails after all retries
    """
    for attempt in range(max_retries):
        try:
            return _create_order_internal(order)
        except HTTPException as e:
            # Check if this is a duplicate key error (SQL0803N)
            if e.status_code == 500 and "SQL0803N" in str(e.detail):
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) * 0.1 + random.uniform(0, 0.1)
                    LOGGER.warning(
                        f"Duplicate key error on attempt {attempt + 1}/{max_retries}, "
                        f"retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    LOGGER.error(f"Order creation failed after {max_retries} attempts")
                    raise HTTPException(
                        status_code=500,
                        detail="Order creation failed due to high concurrent load. Please try again."
                    )
            # Re-raise if not a duplicate key error
            raise


def _create_order_internal(order: OrderRequest):
    """
    Internal function that performs the actual order creation logic.
    Separated to allow retry wrapper to handle duplicate key errors.
    
    Args:
        order (OrderRequest): Complete order information including customer, items, and date
        
    Returns:
        dict: Order response with order_id, message, and total_price
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
            if burger_dict.get("topping_ids") and not burger_dict.get("toppings"):
                burger_dict["toppings"] = [
                    {"topping_id": topping_id, "count": 1}
                    for topping_id in burger_dict["topping_ids"]
                ]
            burger_dict.pop("topping_ids", None)
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

        # Use a single database cursor for the entire order creation transaction
        # This dramatically improves performance by avoiding 30-40 separate connections
        with get_db_cursor() as cursor:
            # 1. Check/Create customer
            existing_customer = customer_dao.get_by_key(
                customer_entity.get_primary_key(), cursor=cursor)
            if not existing_customer.success or not existing_customer.data:
                LOGGER.info(f"Creating new customer: {customer_entity.email}")
                customer_create_result = customer_dao.create_record(
                    customer_entity.to_dict(), cursor=cursor)
                if not customer_create_result.success:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to create customer")

            # 2. Generate IDs - prefer MAX() helper, fallback to legacy get_all_records mocks
            def _next_id(dao, key_name: str) -> int:
                max_id_result = None
                if hasattr(dao, "get_max_id"):
                    max_id_result = dao.get_max_id(cursor=cursor)
                if max_id_result and getattr(max_id_result, "success", False) and isinstance(getattr(max_id_result, "data", None), int):
                    return max_id_result.data + 1

                all_rows_result = dao.get_all_records(cursor=cursor)
                if all_rows_result and getattr(all_rows_result, "success", False) and all_rows_result.data:
                    return max(row.get(key_name, 0) for row in all_rows_result.data) + 1
                return 1

            next_order_id = _next_id(order_dao, "ORDER_ID")
            next_order_item_id = _next_id(order_item_dao, "ORDER_ITEM_ID")
            next_burger_id = _next_id(burger_item_dao, "BURGER_ID")
            next_fry_id = _next_id(fry_item_dao, "FRY_ID")

            # 3. Validate ingredients and calculate prices (but don't create items
            # yet)
            total_price = 0.0
            order_qty = len(sanitized_burgers) + len(sanitized_fries)

            # Prepare burger data
            burger_items_to_create = []

            # Batch-fetch all unique buns, patties, and toppings in 3 queries
            # Filter out None and 0 (sentinel for None) since buns and patties are now optional
            bun_ids = list(set(b["bun_id"] for b in sanitized_burgers if b.get("bun_id") not in (None, 0)))
            patty_ids = list(set(b["patty_id"] for b in sanitized_burgers if b.get("patty_id") not in (None, 0)))
            topping_ids = list(set(
                t["topping_id"]
                for b in sanitized_burgers
                for t in b["toppings"]
            ))

            def _build_lookup(dao, ids: list[int], key_name: str) -> dict[int, dict]:
                if not ids:
                    return {}

                lookup: dict[int, dict] = {}
                if hasattr(dao, "get_by_keys"):
                    batch_result = dao.get_by_keys(ids, cursor=cursor)
                    if batch_result and getattr(batch_result, "success", False):
                        if isinstance(batch_result.data, list):
                            lookup.update({item[key_name]: item for item in batch_result.data})
                        elif isinstance(batch_result.data, dict):
                            lookup[batch_result.data[key_name]] = batch_result.data

                if hasattr(dao, "get_by_key"):
                    for item_id in ids:
                        if item_id in lookup:
                            continue
                        single_result = dao.get_by_key(item_id, cursor=cursor)
                        if single_result and getattr(single_result, "success", False) and isinstance(single_result.data, dict):
                            lookup[item_id] = single_result.data

                return lookup

            bun_lookup = _build_lookup(bun_dao, bun_ids, "BUN_ID")
            patty_lookup = _build_lookup(patty_dao, patty_ids, "PATTY_ID")
            topping_lookup = _build_lookup(topping_dao, topping_ids, "TOPPING_ID")

            for burger in sanitized_burgers:
                burger_price = 0.0
                
                # Handle optional bun (0 = None sentinel value)
                bun_id = burger.get("bun_id")
                if bun_id is not None and bun_id != 0:
                    bun_data = bun_lookup.get(bun_id)
                    if not bun_data:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid bun ID: {bun_id}")
                    bun_stock = bun_data.get("STOCK_QUANTITY", float("inf"))
                    if bun_stock < 1:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Insufficient stock for bun ID {bun_id}")
                    burger_price += float(bun_data["PRICE"])
                
                # Handle optional patty (0 = None sentinel value)
                patty_id = burger.get("patty_id")
                patty_count = burger.get("patty_count", 1)
                if patty_id is not None and patty_id != 0:
                    patty_data = patty_lookup.get(patty_id)
                    if not patty_data:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid patty ID: {patty_id}")
                    patty_stock = patty_data.get("STOCK_QUANTITY", float("inf"))
                    if patty_stock < patty_count:
                        raise HTTPException(
                            status_code=400, detail=f"Insufficient stock for patty ID {
                                patty_id} (need {patty_count}, have {
                                patty_stock})")
                    burger_price += float(patty_data["PRICE"]) * patty_count

                # Validate and add topping prices
                for topping in burger["toppings"]:
                    topping_id = topping["topping_id"]
                    topping_count = topping.get("count", 1)
                    topping_data = topping_lookup.get(topping_id)
                    if not topping_data:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid topping ID: {topping_id}")
                    # Check topping inventory
                    topping_stock = topping_data.get("STOCK_QUANTITY", float("inf"))
                    if topping_stock < topping_count:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Insufficient stock for topping ID {topping_id} (need {topping_count}, have {topping_stock})")
                    burger_price += float(topping_data["PRICE"]) * topping_count

                # Store burger data for later creation
                burger_items_to_create.append({
                    "burger_data": burger,
                    "price": burger_price
                })
                total_price += burger_price

            # Prepare fry data
            fry_items_to_create = []

            # Batch-fetch all unique fry types, sizes, and seasonings
            fry_type_ids = list(set(f["type_id"] for f in sanitized_fries))
            fry_size_ids = list(set(f["size_id"] for f in sanitized_fries))
            fry_seasoning_ids = list(set(f["seasoning_id"] for f in sanitized_fries))

            fry_type_lookup = _build_lookup(fry_type_dao, fry_type_ids, "FRY_TYPE_ID")
            fry_size_lookup = _build_lookup(fry_size_dao, fry_size_ids, "FRY_SIZE_ID")
            fry_seasoning_lookup = _build_lookup(
                fry_seasoning_dao,
                fry_seasoning_ids,
                "FRY_SEASONING_ID",
            )

            for fry in sanitized_fries:
                fry_type_data = fry_type_lookup.get(fry["type_id"])
                fry_size_data = fry_size_lookup.get(fry["size_id"])
                fry_seasoning_data = fry_seasoning_lookup.get(fry["seasoning_id"])

                if not fry_type_data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid fry type ID: {fry['type_id']}")
                if not fry_size_data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid fry size ID: {fry['size_id']}")
                if not fry_seasoning_data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid fry seasoning ID: {fry['seasoning_id']}")

                # Check inventory availability (fry_size is the multiplier for
                # stock usage)
                fry_size_value = fry_size_data.get("FRY_SIZE", 1)
                fry_type_stock = fry_type_data.get("STOCK_QUANTITY", float("inf"))
                fry_seasoning_stock = fry_seasoning_data.get("STOCK_QUANTITY", float("inf"))
                if fry_type_stock < fry_size_value:
                    raise HTTPException(
                        status_code=400, detail=f"Insufficient stock for fry type ID {
                            fry['type_id']} (need {fry_size_value}, have {
                            fry_type_stock})")
                if fry_seasoning_stock < fry_size_value:
                    raise HTTPException(
                        status_code=400, detail=f"Insufficient stock for fry seasoning ID {
                            fry['seasoning_id']} (need {fry_size_value}, have {
                            fry_seasoning_stock})")

                fry_price = (float(fry_type_data["PRICE"]) +
                             float(fry_size_data["PRICE"]) +
                             float(fry_seasoning_data["PRICE"]))

                # Store fry data for later creation
                fry_items_to_create.append({
                    "fry_data": fry,
                    "price": fry_price,
                    "fry_size_value": fry_size_value
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
            order_create_result = order_dao.create_record(order_record, cursor=cursor)
            if not order_create_result.success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create order")

            # 5. Now create ORDER_ITEMS and associated items (order exists now)
            # Build all insert records in memory, then batch-insert each table
            all_order_items = []
            all_burger_items = []
            all_burger_toppings = []
            all_fry_items = []

            # Collect burger insert records
            for burger_item_data in burger_items_to_create:
                burger = burger_item_data["burger_data"]
                burger_price = burger_item_data["price"]

                all_order_items.append({
                    "ORDER_ITEM_ID": next_order_item_id,
                    "ORDER_ID": next_order_id,
                    "ITEM_TYPE": "BURGER",
                    "UNIT_PRICE": burger_price
                })

                all_burger_items.append({
                    "BURGER_ID": next_burger_id,
                    "ORDER_ITEM_ID": next_order_item_id,
                    "BUN_TYPE": burger.get("bun_id") or 0,  # Use 0 for None to avoid DB NULL constraint
                    "PATTY_TYPE": burger.get("patty_id") or 0,  # Use 0 for None to avoid DB NULL constraint
                    "PATTY_COUNT": burger.get("patty_count", 1)
                })

                for topping in burger["toppings"]:
                    all_burger_toppings.append({
                        "BURGER_ORDER_ID": next_burger_id,
                        "TOPPING_ID": topping["topping_id"],
                        "TOPPING_COUNT": topping.get("count", 1)
                    })

                next_order_item_id += 1
                next_burger_id += 1

            # Collect fry insert records
            for fry_item_data in fry_items_to_create:
                fry = fry_item_data["fry_data"]
                fry_price = fry_item_data["price"]

                all_order_items.append({
                    "ORDER_ITEM_ID": next_order_item_id,
                    "ORDER_ID": next_order_id,
                    "ITEM_TYPE": "FRIES",
                    "UNIT_PRICE": fry_price
                })

                all_fry_items.append({
                    "FRY_ID": next_fry_id,
                    "ORDER_ITEM_ID": next_order_item_id,
                    "FRY_TYPE": fry["type_id"],
                    "FRY_SIZE": fry["size_id"],
                    "FRY_SEASONING": fry["seasoning_id"]
                })

                next_order_item_id += 1
                next_fry_id += 1

            # Batch insert all records (one executemany per table)
            if all_order_items:
                result = order_item_dao.create_records_batch(all_order_items, cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to create order items")
            if all_burger_items:
                result = burger_item_dao.create_records_batch(all_burger_items, cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to create burger items")
            if all_burger_toppings:
                result = burger_topping_dao.create_records_batch(all_burger_toppings, cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to create burger toppings")
            if all_fry_items:
                result = fry_item_dao.create_records_batch(all_fry_items, cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to create fry items")

            # 6. Decrement inventory for all ingredients used (aggregated by ID)
            LOGGER.debug("Decrementing inventory for order items")

            # Aggregate burger ingredient decrements by ID
            bun_decrements = {}    # bun_id -> total to decrement
            patty_decrements = {}  # patty_id -> total to decrement
            topping_decrements = {}  # topping_id -> total to decrement

            for burger_item_data in burger_items_to_create:
                burger = burger_item_data["burger_data"]
                
                # Only decrement if bun is present (buns are optional, 0 = None sentinel)
                bun_id = burger.get("bun_id")
                if bun_id is not None and bun_id != 0:
                    bun_decrements[bun_id] = bun_decrements.get(bun_id, 0) - 1

                # Only decrement if patty is present (patties are optional, 0 = None sentinel)
                patty_id = burger.get("patty_id")
                if patty_id is not None and patty_id != 0:
                    patty_count = burger.get("patty_count", 1)
                    patty_decrements[patty_id] = patty_decrements.get(patty_id, 0) - patty_count

                for topping in burger["toppings"]:
                    tid = topping["topping_id"]
                    tc = topping.get("count", 1)
                    topping_decrements[tid] = topping_decrements.get(tid, 0) - tc

            # Aggregate fry ingredient decrements by ID
            fry_type_decrements = {}
            fry_seasoning_decrements = {}

            for fry_item_data in fry_items_to_create:
                fry = fry_item_data["fry_data"]
                fry_size_value = fry_item_data["fry_size_value"]

                type_id = fry["type_id"]
                fry_type_decrements[type_id] = fry_type_decrements.get(type_id, 0) - fry_size_value

                seasoning_id = fry["seasoning_id"]
                fry_seasoning_decrements[seasoning_id] = fry_seasoning_decrements.get(seasoning_id, 0) - fry_size_value

            # Execute aggregated decrements (one UPDATE per unique ingredient ID)
            if bun_decrements:
                result = bun_dao.batch_update_field_by_delta(bun_decrements, "STOCK_QUANTITY", cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to update bun inventory")
            if patty_decrements:
                result = patty_dao.batch_update_field_by_delta(patty_decrements, "STOCK_QUANTITY", cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to update patty inventory")
            if topping_decrements:
                result = topping_dao.batch_update_field_by_delta(topping_decrements, "STOCK_QUANTITY", cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to update topping inventory")
            if fry_type_decrements:
                result = fry_type_dao.batch_update_field_by_delta(fry_type_decrements, "STOCK_QUANTITY", cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to update fry type inventory")
            if fry_seasoning_decrements:
                result = fry_seasoning_dao.batch_update_field_by_delta(fry_seasoning_decrements, "STOCK_QUANTITY", cursor=cursor)
                if not result.success:
                    raise HTTPException(status_code=500, detail="Failed to update fry seasoning inventory")

            # All operations completed successfully - commit happens automatically
            # when exiting the cursor context

        LOGGER.info(
            f"Order {next_order_id} created successfully with total ${total_price:.2f}")

        return {
            "order_id": next_order_id,
            "message": "Order created successfully",
            "total_price": round(total_price, 2)
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


@app.post("/Order/", response_model=OrderResponse)
async def create_order(order: OrderRequest):
    """
    Create a new order with customer info, burgers, and fries.
    Thread-safe operation using connection pool with automatic retry on race conditions.
    Handles transactions across multiple tables.

    Args:
        order (OrderRequest): Complete order information including customer, items, and date
        
    Returns:
        OrderResponse: Created order with ID and total price
    """
    return _execute_order_creation(order)


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
