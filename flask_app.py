from __future__ import annotations

import pandas as pd
import streamlit as st

from inventory_app.crud import add_product, delete_product, get_all_products, get_product_by_id, search_products, update_product
from inventory_app.database import init_db
from inventory_app.models import Product

init_db()


def product_to_row(product: Product) -> dict[str, object]:
    return {
        "ID": product.id,
        "Name": product.name,
        "Category": product.category,
        "Quantity": product.quantity,
        "Price": product.price,
        "Supplier": product.supplier,
        "Total Value": product.total_value,
    }


def add_product_form() -> None:
    with st.form("add-product-form", clear_on_submit=True):
        st.subheader("Add Product")
        name = st.text_input("Name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f")
        supplier = st.text_input("Supplier")

        submitted = st.form_submit_button("Add Product")
        if submitted:
            if not name.strip() or not category.strip() or not supplier.strip():
                st.warning("Name, category, and supplier are required.")
                return

            product = Product(
                name=name.strip(),
                category=category.strip(),
                quantity=quantity,
                price=price,
                supplier=supplier.strip(),
            )
            new_id = add_product(product)
            st.success(f"Product added successfully with ID {new_id}.")
            st.rerun()


def update_product_form(products: list[Product]) -> None:
    if not products:
        st.info("No products available to update.")
        return

    st.subheader("Update Product")
    product_map = {f"#{product.id} - {product.name}": product.id for product in products}
    selected_label = st.selectbox("Select a product", list(product_map.keys()))
    product_id = product_map[selected_label]
    product = get_product_by_id(product_id)
    if product is None:
        st.error("Selected product could not be found.")
        return

    with st.form("update-product-form"):
        name = st.text_input("Name", value=product.name)
        category = st.text_input("Category", value=product.category)
        quantity = st.number_input("Quantity", min_value=0, value=product.quantity, step=1)
        price = st.number_input("Price", min_value=0.0, value=product.price, step=0.01, format="%.2f")
        supplier = st.text_input("Supplier", value=product.supplier)

        if st.form_submit_button("Save Changes"):
            if not name.strip() or not category.strip() or not supplier.strip():
                st.warning("Name, category, and supplier are required.")
                return

            updates = {
                "name": name.strip(),
                "category": category.strip(),
                "quantity": quantity,
                "price": price,
                "supplier": supplier.strip(),
            }

            if update_product(product_id, **updates):
                st.success("Product updated successfully.")
                st.rerun()
            else:
                st.error("Failed to update product.")


def delete_product_form(products: list[Product]) -> None:
    if not products:
        st.info("No products available to delete.")
        return

    st.subheader("Delete Product")
    product_map = {f"#{product.id} - {product.name}": product.id for product in products}
    selected_label = st.selectbox("Select a product", list(product_map.keys()), key="delete-product-select")
    delete_id = product_map[selected_label]

    if st.button("Delete Selected Product"):
        if delete_product(delete_id):
            st.success(f"Product #{delete_id} deleted.")
            st.rerun()
        else:
            st.error("Could not delete the selected product.")


def get_category_options(products: list[Product]) -> list[str]:
    categories = sorted({product.category for product in products if product.category})
    return categories


def filter_products(products: list[Product], query: str, selected_categories: list[str], max_price: float) -> list[Product]:
    filtered = products

    if query.strip():
        filtered = [
            product
            for product in filtered
            if query.lower() in product.name.lower()
            or query.lower() in product.category.lower()
            or query.lower() in product.supplier.lower()
        ]

    if selected_categories:
        filtered = [product for product in filtered if product.category in selected_categories]

    return [product for product in filtered if product.price <= max_price]


def inventory_table(products: list[Product]) -> None:
    if not products:
        st.info("No products match your search.")
        return

    df = pd.DataFrame([product_to_row(product) for product in products])
    st.dataframe(df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Inventory Management", layout="wide")
    st.title("Inventory Management System")

    all_products = get_all_products()
    categories = get_category_options(all_products)
    max_price_value = max((product.price for product in all_products), default=0.0)

    with st.sidebar:
        st.header("Filters")
        selected_categories = st.multiselect("Categories", options=categories, default=categories)
        max_price = st.slider("Max Price", min_value=0.0, max_value=10000.0, value=10000.0, step=100.0)
        query = st.text_input("Search products", placeholder="Search by name, category, or supplier")

    filtered_products = filter_products(all_products, query, selected_categories, max_price)

    left_column, right_column = st.columns([1, 2])

    with left_column:
        add_product_form()
        st.divider()
        delete_product_form(filtered_products)

    with right_column:
        inventory_table(filtered_products)
        st.divider()
        update_product_form(filtered_products)


main()
