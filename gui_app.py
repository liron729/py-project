from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from inventory_app.crud import add_product, delete_product, get_all_products, get_product_by_id, search_products, update_product
from inventory_app.database import init_db
from inventory_app.models import Product


class InventoryApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("980x620")
        self.minsize(900, 520)

        self.product_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self.build_ui()
        self.load_products()

    def build_ui(self) -> None:
        top = ttk.Frame(self, padding=(10, 10, 10, 10))
        top.pack(fill="x")

        ttk.Label(top, text="Search:").pack(side="left")
        ttk.Entry(top, textvariable=self.search_var, width=40).pack(side="left", padx=(5, 10))
        ttk.Button(top, text="Search", command=self.search_products).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.load_products).pack(side="left", padx=(5, 0))

        form = ttk.LabelFrame(self, text="Product Details", padding=(10, 10, 10, 10))
        form.pack(fill="x", padx=10, pady=(0, 10))

        fields = [
            ("Name", self.name_var),
            ("Category", self.category_var),
            ("Quantity", self.quantity_var),
            ("Price", self.price_var),
            ("Supplier", self.supplier_var),
        ]

        for label, variable in fields:
            row = ttk.Frame(form)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=f"{label}:", width=12).pack(side="left")
            ttk.Entry(row, textvariable=variable, width=60).pack(side="left", fill="x", expand=True)

        actions = ttk.Frame(form)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Add Product", command=self.add_product).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Update Product", command=self.update_product).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Delete Product", command=self.delete_product).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Clear", command=self.clear_form).pack(side="left")

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("ID", "Name", "Category", "Qty", "Price", "Supplier")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

    def load_products(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for product in get_all_products():
            self.tree.insert(
                "",
                "end",
                values=(product.id, product.name, product.category, product.quantity, f"{product.price:.2f}", product.supplier),
            )

    def search_products(self) -> None:
        keyword = self.search_var.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        products = search_products(keyword) if keyword else get_all_products()
        for product in products:
            self.tree.insert(
                "",
                "end",
                values=(product.id, product.name, product.category, product.quantity, f"{product.price:.2f}", product.supplier),
            )

    def on_select(self, event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if not values:
            return
        product = get_product_by_id(int(values[0]))
        if product is None:
            return

        self.product_id_var.set(str(product.id))
        self.name_var.set(product.name)
        self.category_var.set(product.category)
        self.quantity_var.set(str(product.quantity))
        self.price_var.set(str(product.price))
        self.supplier_var.set(product.supplier)

    def add_product(self) -> None:
        try:
            product = Product(
                name=self.name_var.get().strip(),
                category=self.category_var.get().strip(),
                quantity=int(self.quantity_var.get()),
                price=float(self.price_var.get()),
                supplier=self.supplier_var.get().strip(),
            )
            add_product(product)
            self.clear_form()
            self.load_products()
            messagebox.showinfo("Success", "Product added successfully.")
        except ValueError as exc:
            messagebox.showerror("Input Error", f"Invalid value: {exc}")

    def update_product(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to update.")
            return

        product_id = int(self.tree.item(selected[0], "values")[0])
        try:
            update_product(
                product_id,
                name=self.name_var.get().strip(),
                category=self.category_var.get().strip(),
                quantity=int(self.quantity_var.get()),
                price=float(self.price_var.get()),
                supplier=self.supplier_var.get().strip(),
            )
            self.clear_form()
            self.load_products()
            messagebox.showinfo("Success", "Product updated successfully.")
        except ValueError as exc:
            messagebox.showerror("Input Error", f"Invalid value: {exc}")

    def delete_product(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to delete.")
            return

        product_id = int(self.tree.item(selected[0], "values")[0])
        if messagebox.askyesno("Confirm Delete", "Delete this product?"):
            delete_product(product_id)
            self.clear_form()
            self.load_products()
            messagebox.showinfo("Success", "Product deleted successfully.")

    def clear_form(self) -> None:
        self.product_id_var.set("")
        self.name_var.set("")
        self.category_var.set("")
        self.quantity_var.set("")
        self.price_var.set("")
        self.supplier_var.set("")
        self.tree.selection_remove(self.tree.selection())


if __name__ == "__main__":
    init_db()
    app = InventoryApp()
    app.mainloop()
