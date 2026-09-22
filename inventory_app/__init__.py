"""Inventory management package."""

from .crud import add_product, delete_product, get_all_products, get_product_by_id, search_products, update_product

__all__ = [
    "add_product",
    "delete_product",
    "get_all_products",
    "get_product_by_id",
    "search_products",
    "update_product",
]
