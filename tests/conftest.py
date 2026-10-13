"""Shared pytest fixtures for ShopEase tests.

A fresh temporary SQLite database is created for every test session so that
tests never touch the development/production database.
"""

import os
import tempfile

import pytest

# Point db module at a temporary database BEFORE importing app
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DB_PATH"] = _tmp.name

from app import app as flask_app  # noqa: E402
from db import init_db, seed_products, get_connection  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables and seed products once per test session."""
    init_db()
    seed_products()
    # Create a test admin user
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO admin_users (username, password_hash) VALUES (?, ?)",
        ("testadmin", generate_password_hash("testpass123")),
    )
    conn.commit()
    conn.close()
    yield
    # Cleanup temp database after all tests
    try:
        os.unlink(os.environ["DB_PATH"])
    except OSError:
        pass


@pytest.fixture()
def client():
    """Provide a Flask test client."""
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def admin_client(client):
    """Provide a test client that is already logged in as admin."""
    client.post(
        "/admin/login",
        data={"username": "testadmin", "password": "testpass123"},
        follow_redirects=True,
    )
    return client
