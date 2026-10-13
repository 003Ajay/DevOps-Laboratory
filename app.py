"""ShopEase – a simple e-commerce application built with Flask and SQLite.

Run locally:
    flask run --debug

Production (inside Docker):
    gunicorn -b 0.0.0.0:5000 app:app
"""

import os
import re
import functools

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from werkzeug.security import check_password_hash

from db import get_connection, init_db, seed_products

# ---------------------------------------------------------------------------
# App factory-ish setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Initialise database & seed products on first import / startup
init_db()
seed_products()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paise_to_rupees(paise):
    """Convert integer paise to display string like '₹1,299.00'."""
    rupees = paise / 100
    return f"₹{rupees:,.2f}"


# Register as Jinja filter so templates can use {{ price|rupees }}
app.jinja_env.filters["rupees"] = _paise_to_rupees


def _get_cart():
    """Return the shopping cart dict from the session. Keys are product-id strings."""
    return session.get("cart", {})


def _save_cart(cart):
    session["cart"] = cart
    session.modified = True


def _cart_count():
    """Total number of items across all products in the cart."""
    return sum(_get_cart().values())


@app.context_processor
def inject_cart_count():
    """Make cart_count available in every template."""
    return {"cart_count": _cart_count()}


def admin_required(f):
    """Decorator that protects admin routes."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin dashboard.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Health endpoint (used by Docker HEALTHCHECK and Jenkins verification)
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    """Return a simple JSON health-check response."""
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "healthy"}), 200
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Product routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Homepage – show featured products."""
    conn = get_connection()
    products = conn.execute(
        "SELECT * FROM products WHERE available = 1 ORDER BY id LIMIT 10"
    ).fetchall()
    categories = conn.execute(
        "SELECT DISTINCT category FROM products ORDER BY category"
    ).fetchall()
    conn.close()
    return render_template("index.html", products=products, categories=categories)


@app.route("/products")
def products():
    """Product listing with optional search & category filter."""
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    conn = get_connection()
    query = "SELECT * FROM products WHERE available = 1"
    params = []

    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like])

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id"
    products_list = conn.execute(query, params).fetchall()
    categories = conn.execute(
        "SELECT DISTINCT category FROM products ORDER BY category"
    ).fetchall()
    conn.close()
    return render_template(
        "products.html",
        products=products_list,
        categories=categories,
        search=search,
        selected_category=category,
    )


@app.route("/product/<int:product_id>")
def product_details(product_id):
    """Single product detail page."""
    conn = get_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if product is None:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))
    return render_template("product_details.html", product=product)


# ---------------------------------------------------------------------------
# Cart routes
# ---------------------------------------------------------------------------

@app.route("/cart")
def cart():
    """Display the shopping cart."""
    cart_data = _get_cart()
    if not cart_data:
        return render_template("cart.html", items=[], subtotal=0, total=0)

    conn = get_connection()
    items = []
    subtotal = 0
    for pid_str, qty in cart_data.items():
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (int(pid_str),)
        ).fetchone()
        if product:
            line_total = product["price"] * qty
            subtotal += line_total
            items.append({"product": product, "quantity": qty, "line_total": line_total})
    conn.close()
    return render_template("cart.html", items=items, subtotal=subtotal, total=subtotal)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id):
    """Add one unit of a product to the cart."""
    conn = get_connection()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ? AND available = 1", (product_id,)
    ).fetchone()
    conn.close()

    if product is None:
        flash("Product not available.", "danger")
        return redirect(url_for("products"))

    cart_data = _get_cart()
    pid = str(product_id)
    current_qty = cart_data.get(pid, 0)

    if current_qty + 1 > product["stock"]:
        flash("Not enough stock available.", "warning")
        return redirect(request.referrer or url_for("products"))

    cart_data[pid] = current_qty + 1
    _save_cart(cart_data)
    flash(f"'{product['name']}' added to cart.", "success")
    return redirect(request.referrer or url_for("products"))


@app.route("/cart/update/<int:product_id>", methods=["POST"])
def cart_update(product_id):
    """Update the quantity of a product in the cart."""
    try:
        qty = int(request.form.get("quantity", 0))
    except (ValueError, TypeError):
        flash("Invalid quantity.", "danger")
        return redirect(url_for("cart"))

    cart_data = _get_cart()
    pid = str(product_id)

    if qty <= 0:
        cart_data.pop(pid, None)
        _save_cart(cart_data)
        flash("Item removed from cart.", "info")
        return redirect(url_for("cart"))

    conn = get_connection()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ? AND available = 1", (product_id,)
    ).fetchone()
    conn.close()

    if product is None:
        cart_data.pop(pid, None)
        _save_cart(cart_data)
        flash("Product no longer available.", "danger")
        return redirect(url_for("cart"))

    if qty > product["stock"]:
        flash(f"Only {product['stock']} units in stock.", "warning")
        return redirect(url_for("cart"))

    cart_data[pid] = qty
    _save_cart(cart_data)
    flash("Cart updated.", "success")
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def cart_remove(product_id):
    """Remove a product from the cart entirely."""
    cart_data = _get_cart()
    cart_data.pop(str(product_id), None)
    _save_cart(cart_data)
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))


# ---------------------------------------------------------------------------
# Checkout / Order routes
# ---------------------------------------------------------------------------

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    """Checkout page – collect customer info, validate, create order."""
    cart_data = _get_cart()
    if not cart_data:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products"))

    if request.method == "GET":
        return render_template("checkout.html")

    # --- POST: process order ---
    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    errors = []
    if not name or len(name) < 2:
        errors.append("Please enter a valid name (at least 2 characters).")
    if not phone or not re.match(r"^\+?\d{7,15}$", phone):
        errors.append("Please enter a valid phone number (7-15 digits).")
    if not address or len(address) < 5:
        errors.append("Please enter a delivery address (at least 5 characters).")

    if errors:
        for e in errors:
            flash(e, "danger")
        return render_template("checkout.html")

    # Re-validate cart against database (stock + price)
    conn = get_connection()
    order_items = []
    total = 0

    for pid_str, qty in cart_data.items():
        product = conn.execute(
            "SELECT * FROM products WHERE id = ? AND available = 1", (int(pid_str),)
        ).fetchone()
        if product is None:
            conn.close()
            flash("A product in your cart is no longer available. Please review your cart.", "danger")
            return redirect(url_for("cart"))
        if qty > product["stock"]:
            conn.close()
            flash(f"Not enough stock for '{product['name']}'. Available: {product['stock']}.", "warning")
            return redirect(url_for("cart"))
        line_total = product["price"] * qty
        total += line_total
        order_items.append(
            {"product_id": product["id"], "quantity": qty, "unit_price": product["price"]}
        )

    # Create order inside a transaction
    try:
        cursor = conn.execute(
            "INSERT INTO orders (customer_name, phone, address, total) VALUES (?, ?, ?, ?)",
            (name, phone, address, total),
        )
        order_id = cursor.lastrowid
        for item in order_items:
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, item["product_id"], item["quantity"], item["unit_price"]),
            )
            # Decrease stock
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item["quantity"], item["product_id"]),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        flash("Something went wrong while placing your order. Please try again.", "danger")
        return redirect(url_for("checkout"))

    conn.close()

    # Clear cart
    _save_cart({})
    return redirect(url_for("order_confirmation", order_id=order_id))


@app.route("/order/<int:order_id>")
def order_confirmation(order_id):
    """Display the order confirmation page."""
    conn = get_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        conn.close()
        flash("Order not found.", "danger")
        return redirect(url_for("index"))
    items = conn.execute(
        """SELECT oi.*, p.name, p.image
           FROM order_items oi
           JOIN products p ON p.id = oi.product_id
           WHERE oi.order_id = ?""",
        (order_id,),
    ).fetchall()
    conn.close()
    return render_template("order_confirmation.html", order=order, items=items)


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page."""
    if request.method == "GET":
        return render_template("admin_login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM admin_users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        session["admin_logged_in"] = True
        session["admin_username"] = username
        flash("Welcome back!", "success")
        return redirect(url_for("admin_dashboard"))

    flash("Invalid username or password.", "danger")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    """Log out the current admin."""
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    """Admin dashboard – order list and statistics."""
    conn = get_connection()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()

    stats = {
        "total_orders": len(orders),
        "pending": sum(1 for o in orders if o["status"] == "pending"),
        "shipped": sum(1 for o in orders if o["status"] == "shipped"),
        "delivered": sum(1 for o in orders if o["status"] == "delivered"),
        "revenue": sum(o["total"] for o in orders),
    }
    conn.close()
    return render_template("admin_dashboard.html", orders=orders, stats=stats)


@app.route("/admin/order/<int:order_id>")
@admin_required
def admin_order_details(order_id):
    """View details of a single order."""
    conn = get_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        conn.close()
        flash("Order not found.", "danger")
        return redirect(url_for("admin_dashboard"))
    items = conn.execute(
        """SELECT oi.*, p.name, p.image
           FROM order_items oi
           JOIN products p ON p.id = oi.product_id
           WHERE oi.order_id = ?""",
        (order_id,),
    ).fetchall()
    conn.close()
    return render_template("order_details.html", order=order, items=items)


@app.route("/admin/order/<int:order_id>/status", methods=["POST"])
@admin_required
def admin_update_status(order_id):
    """Update an order's status."""
    new_status = request.form.get("status", "").strip().lower()
    allowed = {"pending", "confirmed", "shipped", "delivered", "cancelled"}
    if new_status not in allowed:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin_order_details", order_id=order_id))

    conn = get_connection()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    flash(f"Order #{order_id} status updated to '{new_status}'.", "success")
    return redirect(url_for("admin_order_details", order_id=order_id))


# ---------------------------------------------------------------------------
# Run (development only – production uses gunicorn)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
