from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template_string, request, url_for

from inventory_app.crud import add_product, delete_product, get_all_products, get_product_by_id, search_products, update_product
from inventory_app.database import init_db
from inventory_app.models import Product

app = Flask(__name__)


def serialize_product(product: Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "quantity": product.quantity,
        "price": product.price,
        "supplier": product.supplier,
        "total_value": product.total_value,
    }


@app.route("/api/products", methods=["GET"])
def api_list_products():
    query = request.args.get("q", "").strip()
    products = search_products(query) if query else get_all_products()
    return jsonify([serialize_product(product) for product in products])


@app.route("/api/products", methods=["POST"])
def api_add_product():
    data = request.get_json(silent=True) or {}
    try:
        product = Product(
            name=str(data.get("name", "")).strip(),
            category=str(data.get("category", "")).strip(),
            quantity=int(data.get("quantity", 0)),
            price=float(data.get("price", 0.0)),
            supplier=str(data.get("supplier", "")).strip(),
        )
        if not (product.name and product.category and product.supplier):
            return jsonify({"error": "Name, category, and supplier are required."}), 400
        product_id = add_product(product)
        created = get_product_by_id(product_id)
        return jsonify({"message": "Product created", "product": serialize_product(created) if created else None}), 201
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid product data: {exc}"}), 400


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_get_product(product_id: int):
    product = get_product_by_id(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(serialize_product(product))


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def api_update_product(product_id: int):
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    updates = {}
    for field in ("name", "category", "quantity", "price", "supplier"):
        if field in data:
            if field in {"quantity"}:
                updates[field] = int(data[field])
            elif field in {"price"}:
                updates[field] = float(data[field])
            else:
                updates[field] = str(data[field]).strip()
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    try:
        updated = update_product(product_id, **updates)
        if not updated:
            return jsonify({"error": "Product not found"}), 404
        product = get_product_by_id(product_id)
        return jsonify({"message": "Product updated", "product": serialize_product(product) if product else None})
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid update data: {exc}"}), 400


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id: int):
    success = delete_product(product_id)
    if not success:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product deleted"})


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Management</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background: #f4f7fb; color: #1f2937; }
        .container { max-width: 1100px; margin: auto; }
        h1, h2 { color: #111827; }
        .topbar { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 20px; }
        form { margin-bottom: 20px; }
        .search-form, .product-form { background: #fff; padding: 18px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        input, button { padding: 10px 12px; border-radius: 6px; border: 1px solid #d1d5db; }
        button { background: #2563eb; color: white; border: none; cursor: pointer; }
        button.danger { background: #dc2626; }
        table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #e5e7eb; }
        .actions a, .actions form { display: inline; }
        .actions a { text-decoration: none; color: #2563eb; margin-right: 12px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .error { color: #b91c1c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="topbar">
            <h1>Inventory Management System</h1>
            <form method="get" action="/" class="search-form">
                <input type="text" name="q" value="{{ query }}" placeholder="Search products..." size="30">
                <button type="submit">Search</button>
                <a href="/" style="margin-left:10px; color:#2563eb; text-decoration:none;">Clear</a>
            </form>
        </div>

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        <div class="grid">
            <div>
                <h2>Add Product</h2>
                <form method="post" action="/products/add" class="product-form">
                    <p><input type="text" name="name" placeholder="Name" required></p>
                    <p><input type="text" name="category" placeholder="Category" required></p>
                    <p><input type="number" name="quantity" min="0" placeholder="Quantity" required></p>
                    <p><input type="number" step="0.01" min="0" name="price" placeholder="Price" required></p>
                    <p><input type="text" name="supplier" placeholder="Supplier" required></p>
                    <button type="submit">Add Product</button>
                </form>
            </div>
            <div>
                <h2>Products</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Category</th>
                            <th>Qty</th>
                            <th>Price</th>
                            <th>Supplier</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for product in products %}
                        <tr>
                            <td>{{ product.id }}</td>
                            <td>{{ product.name }}</td>
                            <td>{{ product.category }}</td>
                            <td>{{ product.quantity }}</td>
                            <td>${{ '%.2f' % product.price }}</td>
                            <td>{{ product.supplier }}</td>
                            <td class="actions">
                                <a href="/products/{{ product.id }}/edit">Edit</a>
                                <form method="post" action="/products/{{ product.id }}/delete" style="display:inline;">
                                    <button type="submit" class="danger" onclick="return confirm('Delete this product?')">Delete</button>
                                </form>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="7">No products found.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    products = search_products(query) if query else get_all_products()
    return render_template_string(HTML_TEMPLATE, products=products, query=query, error="")


@app.route("/products/add", methods=["POST"])
def add_product_route():
    try:
        product = Product(
            name=request.form["name"].strip(),
            category=request.form["category"].strip(),
            quantity=int(request.form["quantity"]),
            price=float(request.form["price"]),
            supplier=request.form["supplier"].strip(),
        )
        add_product(product)
    except ValueError as exc:
        return render_template_string(HTML_TEMPLATE, products=get_all_products(), query="", error=f"Invalid input: {exc}")
    return redirect(url_for("index"))


@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product_route(product_id: int):
    delete_product(product_id)
    return redirect(url_for("index"))


@app.route("/products/<int:product_id>/edit")
def edit_product_route(product_id: int):
    product = get_product_by_id(product_id)
    if product is None:
        return redirect(url_for("index"))

    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <title>Edit Product</title>
            <style>body { font-family: Arial, sans-serif; margin: 30px; } form { max-width: 420px; } input { display:block; width:100%; margin:10px 0; padding:10px; }</style>
        </head>
        <body>
            <h1>Edit Product</h1>
            <form method="post" action="/products/{{ product.id }}/update">
                <input type="text" name="name" value="{{ product.name }}" required>
                <input type="text" name="category" value="{{ product.category }}" required>
                <input type="number" name="quantity" min="0" value="{{ product.quantity }}" required>
                <input type="number" step="0.01" min="0" name="price" value="{{ product.price }}" required>
                <input type="text" name="supplier" value="{{ product.supplier }}" required>
                <button type="submit">Update Product</button>
                <a href="/">Cancel</a>
            </form>
        </body>
        </html>
        """,
        product=product,
    )


@app.route("/products/<int:product_id>/update", methods=["POST"])
def update_product_route(product_id: int):
    updates = {
        "name": request.form["name"].strip(),
        "category": request.form["category"].strip(),
        "quantity": int(request.form["quantity"]),
        "price": float(request.form["price"]),
        "supplier": request.form["supplier"].strip(),
    }
    update_product(product_id, **updates)
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
