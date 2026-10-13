"""Tests for checkout and order creation."""

from db import get_connection


def test_checkout_page_requires_cart(client):
    """Accessing checkout with an empty cart should redirect."""
    rv = client.get("/checkout", follow_redirects=True)
    assert rv.status_code == 200
    assert b"empty" in rv.data.lower()


def test_checkout_page_loads_with_cart(client):
    """Checkout page should load when the cart has items."""
    client.post("/cart/add/1")
    rv = client.get("/checkout")
    assert rv.status_code == 200
    assert b"Checkout" in rv.data


def test_checkout_validation_empty_name(client):
    """Submitting without a name should fail validation."""
    client.post("/cart/add/1")
    rv = client.post(
        "/checkout",
        data={"customer_name": "", "phone": "9876543210", "address": "123 Main St"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"valid name" in rv.data.lower()


def test_checkout_validation_bad_phone(client):
    """Submitting a bad phone number should fail validation."""
    client.post("/cart/add/1")
    rv = client.post(
        "/checkout",
        data={"customer_name": "Test User", "phone": "abc", "address": "123 Main St"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"valid phone" in rv.data.lower()


def test_checkout_validation_short_address(client):
    """Submitting a very short address should fail validation."""
    client.post("/cart/add/1")
    rv = client.post(
        "/checkout",
        data={"customer_name": "Test User", "phone": "9876543210", "address": "Ab"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"address" in rv.data.lower()


def test_successful_order_creation(client):
    """A valid checkout should create an order and redirect to confirmation."""
    client.post("/cart/add/2")
    rv = client.post(
        "/checkout",
        data={
            "customer_name": "Jane Doe",
            "phone": "9876543210",
            "address": "456 Park Avenue, City",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Order Confirmed" in rv.data


def test_order_total_correct(client):
    """Order total should be calculated server-side from DB prices."""
    client.post("/cart/add/3")  # product 3: price 59900 paise
    client.post("/cart/update/3", data={"quantity": "2"})
    rv = client.post(
        "/checkout",
        data={
            "customer_name": "Total Test",
            "phone": "1234567890",
            "address": "789 Test Road, Town",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    # Verify in database
    conn = get_connection()
    order = conn.execute(
        "SELECT * FROM orders WHERE customer_name = ?", ("Total Test",)
    ).fetchone()
    assert order is not None
    assert order["total"] == 59900 * 2  # 2 units at 59900 paise each
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (order["id"],)
    ).fetchall()
    conn.close()
    assert len(items) == 1
    assert items[0]["quantity"] == 2
    assert items[0]["unit_price"] == 59900


def test_stock_decreases_after_order(client):
    """Stock should decrease after a successful order."""
    conn = get_connection()
    before = conn.execute("SELECT stock FROM products WHERE id = 4").fetchone()["stock"]
    conn.close()

    client.post("/cart/add/4")
    client.post(
        "/checkout",
        data={
            "customer_name": "Stock Test",
            "phone": "1234567890",
            "address": "Stock Test Avenue",
        },
    )

    conn = get_connection()
    after = conn.execute("SELECT stock FROM products WHERE id = 4").fetchone()["stock"]
    conn.close()
    assert after == before - 1
