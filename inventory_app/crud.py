from __future__ import annotations

from typing import Sequence

from .database import get_connection
from .models import Product


def add_product(product: Product) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO products (name, category, quantity, price, supplier)
            VALUES (?, ?, ?, ?, ?)
            """,
            (product.name, product.category, product.quantity, product.price, product.supplier),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_all_products() -> list[Product]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, category, quantity, price, supplier FROM products ORDER BY id"
        ).fetchall()
    return [Product(id=row["id"], name=row["name"], category=row["category"], quantity=row["quantity"], price=row["price"], supplier=row["supplier"]) for row in rows]


def get_product_by_id(product_id: int) -> Product | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, category, quantity, price, supplier FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        return None
    return Product(id=row["id"], name=row["name"], category=row["category"], quantity=row["quantity"], price=row["price"], supplier=row["supplier"])


def search_products(keyword: str) -> list[Product]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, category, quantity, price, supplier
            FROM products
            WHERE name LIKE ? OR category LIKE ? OR supplier LIKE ?
            ORDER BY id
            """,
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
        ).fetchall()
    return [Product(id=row["id"], name=row["name"], category=row["category"], quantity=row["quantity"], price=row["price"], supplier=row["supplier"]) for row in rows]


def update_product(product_id: int, **updates: object) -> bool:
    if not updates:
        return False

    allowed_fields = {"name", "category", "quantity", "price", "supplier"}
    invalid_fields = set(updates) - allowed_fields
    if invalid_fields:
        raise ValueError(f"Invalid fields: {sorted(invalid_fields)}")

    columns = ", ".join(f"{field} = ?" for field in updates)
    values = tuple(updates[field] for field in updates)

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE products SET {columns} WHERE id = ?",
            (*values, product_id),
        )
        conn.commit()

    return cursor.rowcount > 0


def delete_product(product_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    return cursor.rowcount > 0
