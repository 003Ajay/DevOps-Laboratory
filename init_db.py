"""Standalone script to initialise the database and seed sample data.

Usage:
    python init_db.py                   # uses default path (instance/shop.db)
    DB_PATH=/data/shop.db python init_db.py
    python init_db.py --create-admin     # also creates initial admin account
"""

import argparse
import getpass
import sys

from werkzeug.security import generate_password_hash

from db import get_connection, init_db, seed_products


def create_admin(username=None, password=None, db_path=None):
    """Create an admin user interactively or via arguments."""
    if not username:
        username = input("Admin username: ").strip()
    if not username:
        print("Username cannot be empty.")
        sys.exit(1)

    if not password:
        password = getpass.getpass("Admin password: ")
        if len(password) < 6:
            print("Password must be at least 6 characters.")
            sys.exit(1)
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.")
            sys.exit(1)
    elif len(password) < 6:
        print("Password must be at least 6 characters.")
        sys.exit(1)

    conn = get_connection(db_path)
    existing = conn.execute(
        "SELECT id FROM admin_users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        print(f"Admin '{username}' already exists.")
        conn.close()
        sys.exit(1)

    conn.execute(
        "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    conn.commit()
    conn.close()
    print(f"Admin '{username}' created successfully.")


def main():
    parser = argparse.ArgumentParser(description="Initialise ShopEase database")
    parser.add_argument(
        "--create-admin",
        action="store_true",
        help="Create an admin user after initialisation",
    )
    parser.add_argument(
        "--username",
        type=str,
        default=None,
        help="Admin username (optional, prompts if omitted)",
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Admin password (optional, prompts if omitted)",
    )
    args = parser.parse_args()

    print("Initialising database …")
    init_db()
    print("Seeding sample products …")
    seed_products()
    print("Database ready.")

    if args.create_admin:
        create_admin(username=args.username, password=args.password)


if __name__ == "__main__":
    main()
