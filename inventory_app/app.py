from __future__ import annotations

from .crud import add_product, delete_product, get_all_products, get_product_by_id, search_products, update_product
from .models import Product


def print_products(products: list[Product]) -> None:
    if not products:
        print("No products found.")
        return

    print("\nID  Name                Category          Qty  Price   Supplier")
    print("-" * 72)
    for product in products:
        print(
            f"{product.id:<3} {product.name:<18} {product.category:<16} {product.quantity:<4} {product.price:>7.2f}  {product.supplier:<12}"
        )
    print()


def add_product_flow() -> None:
    print("\nAdd New Product")
    name = input("Name: ").strip()
    category = input("Category: ").strip()
    quantity = int(input("Quantity: "))
    price = float(input("Price: "))
    supplier = input("Supplier: ").strip()

    product = Product(name=name, category=category, quantity=quantity, price=price, supplier=supplier)
    new_id = add_product(product)
    print(f"Product added successfully with ID {new_id}.")


def list_products() -> None:
    print("\nInventory List")
    print_products(get_all_products())


def update_product_flow() -> None:
    product_id = int(input("Enter product ID to update: "))
    existing = get_product_by_id(product_id)
    if existing is None:
        print("Product not found.")
        return

    print(f"Updating product: {existing.name}")
    new_name = input(f"New name ({existing.name}): ").strip() or existing.name
    new_category = input(f"New category ({existing.category}): ").strip() or existing.category
    new_quantity = input(f"New quantity ({existing.quantity}): ").strip()
    new_price = input(f"New price ({existing.price}): ").strip()
    new_supplier = input(f"New supplier ({existing.supplier}): ").strip() or existing.supplier

    updates = {
        "name": new_name,
        "category": new_category,
        "quantity": int(new_quantity) if new_quantity else existing.quantity,
        "price": float(new_price) if new_price else existing.price,
        "supplier": new_supplier,
    }

    if update_product(product_id, **updates):
        print("Product updated successfully.")
    else:
        print("Update failed.")


def delete_product_flow() -> None:
    product_id = int(input("Enter product ID to delete: "))
    if delete_product(product_id):
        print("Product deleted successfully.")
    else:
        print("Product not found.")


def search_flow() -> None:
    keyword = input("Enter keyword to search: ").strip()
    print_products(search_products(keyword))


def show_menu() -> None:
    print("\nInventory Management System")
    print("1. Add Product")
    print("2. View All Products")
    print("3. Update Product")
    print("4. Delete Product")
    print("5. Search Products")
    print("6. Exit")


def run() -> None:
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_product_flow()
        elif choice == "2":
            list_products()
        elif choice == "3":
            update_product_flow()
        elif choice == "4":
            delete_product_flow()
        elif choice == "5":
            search_flow()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")
