"""Tests for product listing, search, and detail pages."""


def test_homepage_loads(client):
    """Homepage should return 200 and contain the store name."""
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"ShopEase" in rv.data


def test_homepage_shows_products(client):
    """Homepage should display at least one product card."""
    rv = client.get("/")
    assert b"Add to Cart" in rv.data


def test_products_page(client):
    """Products page should list all available products."""
    rv = client.get("/products")
    assert rv.status_code == 200
    assert b"Products" in rv.data


def test_product_search(client):
    """Searching for 'headphones' should return matching products."""
    rv = client.get("/products?q=headphones")
    assert rv.status_code == 200
    assert b"Headphones" in rv.data


def test_product_search_no_results(client):
    """Searching for a nonsense term should show empty results message."""
    rv = client.get("/products?q=xyznonexistent")
    assert rv.status_code == 200
    assert b"No products found" in rv.data


def test_product_filter_by_category(client):
    """Filtering by category should show only matching products."""
    rv = client.get("/products?category=electronics")
    assert rv.status_code == 200
    assert b"electronics" in rv.data.lower()


def test_product_details_page(client):
    """Product detail page for id=1 should load correctly."""
    rv = client.get("/product/1")
    assert rv.status_code == 200
    assert b"Add to Cart" in rv.data


def test_product_details_not_found(client):
    """Requesting a nonexistent product should redirect."""
    rv = client.get("/product/9999")
    assert rv.status_code == 302  # redirect to products
