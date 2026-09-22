from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from inventory_app.crud import add_product, delete_product, get_all_products, get_product_by_id, search_products, update_product
from inventory_app.database import init_db
from inventory_app.models import Product

app = FastAPI(title="Inventory Management API", version="1.0.0")


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=0)
    price: float = Field(..., ge=0)
    supplier: str = Field(..., min_length=1)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1)
    quantity: Optional[int] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    supplier: Optional[str] = Field(default=None, min_length=1)


class ProductResponse(BaseModel):
    id: int | None
    name: str
    category: str
    quantity: int
    price: float
    supplier: str
    total_value: float


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Inventory Management API is running"}


@app.get("/api/products", response_model=list[ProductResponse])
def list_products(q: str | None = Query(default=None, description="Search keyword")) -> list[ProductResponse]:
    products = search_products(q) if q else get_all_products()
    return [
        ProductResponse(
            id=product.id,
            name=product.name,
            category=product.category,
            quantity=product.quantity,
            price=product.price,
            supplier=product.supplier,
            total_value=product.total_value,
        )
        for product in products
    ]


@app.post("/api/products", response_model=ProductResponse, status_code=201)
def create_product(product_data: ProductCreate) -> ProductResponse:
    product = Product(
        name=product_data.name,
        category=product_data.category,
        quantity=product_data.quantity,
        price=product_data.price,
        supplier=product_data.supplier,
    )
    product_id = add_product(product)
    created = get_product_by_id(product_id)
    if created is None:
        raise HTTPException(status_code=500, detail="Product could not be created")
    return ProductResponse(
        id=created.id,
        name=created.name,
        category=created.category,
        quantity=created.quantity,
        price=created.price,
        supplier=created.supplier,
        total_value=created.total_value,
    )


@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int) -> ProductResponse:
    product = get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        quantity=product.quantity,
        price=product.price,
        supplier=product.supplier,
        total_value=product.total_value,
    )


@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product_by_id(product_id: int, product_data: ProductUpdate) -> ProductResponse:
    updates = {k: v for k, v in product_data.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    success = update_product(product_id, **updates)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")

    product = get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found after update")

    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        quantity=product.quantity,
        price=product.price,
        supplier=product.supplier,
        total_value=product.total_value,
    )


@app.delete("/api/products/{product_id}")
def delete_product_by_id(product_id: int) -> dict[str, str]:
    success = delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


if __name__ == "__main__":
    init_db()
    import uvicorn

    uvicorn.run("api_app:app", host="127.0.0.1", port=8000, reload=True)
