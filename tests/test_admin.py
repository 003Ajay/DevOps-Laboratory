"""Tests for admin login, dashboard, and order management."""


def test_admin_login_page(client):
    """Admin login page should load."""
    rv = client.get("/admin/login")
    assert rv.status_code == 200
    assert b"Admin Login" in rv.data


def test_admin_login_invalid(client):
    """Invalid credentials should show an error."""
    rv = client.post(
        "/admin/login",
        data={"username": "wrong", "password": "wrong"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Invalid" in rv.data


def test_admin_login_success(client):
    """Valid credentials should redirect to the dashboard."""
    rv = client.post(
        "/admin/login",
        data={"username": "testadmin", "password": "testpass123"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Dashboard" in rv.data


def test_admin_dashboard_requires_login(client):
    """Accessing dashboard without login should redirect."""
    rv = client.get("/admin")
    assert rv.status_code == 302


def test_admin_dashboard_loads(admin_client):
    """Authenticated admin should see the dashboard."""
    rv = admin_client.get("/admin")
    assert rv.status_code == 200
    assert b"Total Orders" in rv.data


def test_admin_order_status_update(admin_client):
    """Admin should be able to update order status."""
    # First create an order
    admin_client.post("/cart/add/5")
    admin_client.post(
        "/checkout",
        data={
            "customer_name": "Admin Test",
            "phone": "9876543210",
            "address": "Admin Test Address 12345",
        },
    )

    from db import get_connection

    conn = get_connection()
    order = conn.execute(
        "SELECT * FROM orders WHERE customer_name = ?", ("Admin Test",)
    ).fetchone()
    conn.close()

    assert order is not None

    rv = admin_client.post(
        f"/admin/order/{order['id']}/status",
        data={"status": "shipped"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"shipped" in rv.data.lower()


def test_admin_order_status_invalid(admin_client):
    """Invalid status value should be rejected."""
    from db import get_connection

    conn = get_connection()
    order = conn.execute("SELECT id FROM orders LIMIT 1").fetchone()
    conn.close()

    if order:
        rv = admin_client.post(
            f"/admin/order/{order['id']}/status",
            data={"status": "nonexistent"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"Invalid status" in rv.data


def test_admin_logout(admin_client):
    """Logging out should redirect to login page."""
    rv = admin_client.get("/admin/logout", follow_redirects=True)
    assert rv.status_code == 200
    assert b"Admin Login" in rv.data
