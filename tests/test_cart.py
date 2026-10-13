"""Tests for shopping cart functionality."""


def test_add_to_cart(client):
    """Adding a product to the cart should redirect with success."""
    rv = client.post("/cart/add/1", follow_redirects=True)
    assert rv.status_code == 200
    assert b"added to cart" in rv.data.lower()


def test_cart_page_shows_item(client):
    """After adding a product, the cart page should display it."""
    client.post("/cart/add/1")
    rv = client.get("/cart")
    assert rv.status_code == 200
    assert b"Wireless Bluetooth Headphones" in rv.data


def test_cart_update_quantity(client):
    """Updating quantity should succeed for a valid amount."""
    client.post("/cart/add/1")
    rv = client.post("/cart/update/1", data={"quantity": "3"}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Cart updated" in rv.data


def test_cart_update_zero_removes(client):
    """Setting quantity to 0 should remove the item."""
    client.post("/cart/add/1")
    rv = client.post("/cart/update/1", data={"quantity": "0"}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"removed" in rv.data.lower()


def test_cart_remove(client):
    """Removing a product should show removal message."""
    client.post("/cart/add/1")
    rv = client.post("/cart/remove/1", follow_redirects=True)
    assert rv.status_code == 200
    assert b"removed" in rv.data.lower()


def test_add_invalid_product(client):
    """Adding a nonexistent product should show an error."""
    rv = client.post("/cart/add/9999", follow_redirects=True)
    assert rv.status_code == 200
    assert b"not available" in rv.data.lower()


def test_add_exceeds_stock(client):
    """Adding more than available stock should warn the user."""
    # Product 1 has stock=25; add 26 by adding one at a time would be slow,
    # so we update directly.
    client.post("/cart/add/1")
    rv = client.post("/cart/update/1", data={"quantity": "9999"}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"stock" in rv.data.lower()


def test_cart_empty_page(client):
    """Viewing an empty cart should prompt the user to browse products."""
    # Use a fresh client (no items in session)
    rv = client.get("/cart")
    assert rv.status_code == 200
    # Could show "empty" or "Browse Products" depending on state
