"""Database helper module for ShopEase.

Provides connection management, schema initialisation, and product seeding.
The database path is read from the DB_PATH environment variable or defaults
to ``instance/shop.db`` relative to the application root.
"""

import os
import sqlite3

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = (
    "/tmp/shop.db"
    if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
    else os.path.join(os.path.dirname(__file__), "instance", "shop.db")
)
DB_PATH = os.environ.get("DB_PATH", DEFAULT_DB_PATH)


def get_db_path():
    """Return the resolved database path."""
    return DB_PATH


def get_connection(db_path=None):
    """Return a new sqlite3 connection with foreign keys enabled."""
    path = db_path or get_db_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    """Create tables from schema.sql if they do not already exist."""
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_connection(db_path)
    with open(schema_file, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()


# ---------------------------------------------------------------------------
# Sample product data  (prices in paise – 100 paise = ₹1)
# ---------------------------------------------------------------------------

SAMPLE_PRODUCTS = [
    {
        "name": "Wireless Bluetooth Headphones",
        "description": "Premium over-ear wireless headphones with active noise cancellation and 30-hour battery life.",
        "price": 249900,       # ₹2,499.00
        "category": "electronics",
        "image": "headphones.jpg",
        "stock": 25,
        "available": 1,
    },
    {
        "name": "Smartphone Stand",
        "description": "Adjustable aluminium desk stand compatible with all smartphones and small tablets.",
        "price": 79900,        # ₹799.00
        "category": "accessories",
        "image": "phone_stand.jpg",
        "stock": 50,
        "available": 1,
    },
    {
        "name": "Cotton Crew-Neck T-Shirt",
        "description": "Classic-fit 100% cotton t-shirt available in multiple colours. Comfortable everyday wear.",
        "price": 59900,        # ₹599.00
        "category": "clothing",
        "image": "tshirt.jpg",
        "stock": 100,
        "available": 1,
    },
    {
        "name": "LED Desk Lamp",
        "description": "Touch-controlled LED desk lamp with 5 brightness levels and USB charging port.",
        "price": 149900,       # ₹1,499.00
        "category": "home",
        "image": "desk_lamp.jpg",
        "stock": 30,
        "available": 1,
    },
    {
        "name": "Portable Power Bank 10000 mAh",
        "description": "Slim 10 000 mAh power bank with dual USB-A and USB-C output. Fast-charge supported.",
        "price": 129900,       # ₹1,299.00
        "category": "electronics",
        "image": "power_bank.jpg",
        "stock": 40,
        "available": 1,
    },
    {
        "name": "Stainless Steel Water Bottle",
        "description": "Double-wall vacuum-insulated 750 ml water bottle. Keeps drinks cold 24 h / hot 12 h.",
        "price": 89900,        # ₹899.00
        "category": "home",
        "image": "water_bottle.jpg",
        "stock": 60,
        "available": 1,
    },
    {
        "name": "Leather Wallet",
        "description": "Genuine leather bi-fold wallet with RFID-blocking technology and multiple card slots.",
        "price": 119900,       # ₹1,199.00
        "category": "accessories",
        "image": "wallet.jpg",
        "stock": 35,
        "available": 1,
    },
    {
        "name": "Running Shoes",
        "description": "Lightweight mesh running shoes with cushioned sole. Ideal for daily jogs and gym workouts.",
        "price": 199900,       # ₹1,999.00
        "category": "clothing",
        "image": "running_shoes.jpg",
        "stock": 20,
        "available": 1,
    },
    {
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless optical mouse with adjustable DPI and silent click buttons.",
        "price": 69900,        # ₹699.00
        "category": "electronics",
        "image": "wireless_mouse.jpg",
        "stock": 45,
        "available": 1,
    },
    {
        "name": "Scented Candle Set",
        "description": "Set of 3 soy-wax scented candles – lavender, vanilla, and sandalwood. Burns 40 h each.",
        "price": 99900,        # ₹999.00
        "category": "home",
        "image": "candle_set.jpg",
        "stock": 55,
        "available": 1,
    },
]


def seed_products(db_path=None):
    """Insert sample products only when the table is empty (avoids duplicates)."""
    conn = get_connection(db_path)
    cursor = conn.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        conn.executemany(
            """INSERT INTO products (name, description, price, category, image, stock, available)
               VALUES (:name, :description, :price, :category, :image, :stock, :available)""",
            SAMPLE_PRODUCTS,
        )
        conn.commit()

    # Also seed initial admin account if none exists
    admin_count = conn.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0]
    if admin_count == 0:
        from werkzeug.security import generate_password_hash
        conn.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("adminpass123")),
        )
        conn.commit()

    conn.close()
