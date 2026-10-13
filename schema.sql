-- ShopEase Database Schema
-- All monetary amounts are stored as integer paise (1 INR = 100 paise).

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    price       INTEGER NOT NULL CHECK (price > 0),          -- paise
    category    TEXT    NOT NULL DEFAULT 'general',
    image       TEXT    NOT NULL DEFAULT 'default.png',
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    available   INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0, 1)),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name   TEXT    NOT NULL,
    phone           TEXT    NOT NULL,
    address         TEXT    NOT NULL,
    total           INTEGER NOT NULL CHECK (total >= 0),      -- paise
    status          TEXT    NOT NULL DEFAULT 'pending',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  INTEGER NOT NULL CHECK (unit_price > 0),      -- paise at purchase time
    FOREIGN KEY (order_id)   REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

CREATE TABLE IF NOT EXISTS admin_users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);
