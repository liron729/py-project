# Inventory Management System

A Python inventory management system with SQLite persistence and CRUD functionality.

## Features

- Add a product
- View all products
- Update product details
- Delete a product
- Search products by name, category, or supplier
- Local SQLite database persistence
- CLI, Streamlit web app, and Tkinter GUI versions
- FastAPI with Uvicorn for API

## Project Structure

- `main.py` - command-line version
- `flask_app.py` - Streamlit web application
- `gui_app.py` - Tkinter desktop application
- `inventory_app/database.py` - database setup and connection
- `inventory_app/models.py` - product model
- `inventory_app/crud.py` - CRUD logic
- `inventory_app/app.py` - CLI menu interface
- `api_app.py` - FastAPI application

## Run the applications

### Command-line app

```bash
python main.py
```

### Streamlit web app

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run flask_app.py
```

Then open:

```text
http://localhost:8501
```

### Tkinter GUI app

```bash
python gui_app.py
```

### API (FastAPI + Uvicorn)

Run the API:

```bash
pip install -r requirements.txt
uvicorn api_app:app --host 127.0.0.1 --port 8000 --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Database file

The app creates a SQLite database named `inventory.db` in the project root.

## Example usage

1. Add a product with product name, category, quantity, price, and supplier.
2. Search or view records from the list.
3. Select an item in the GUI or web app to edit or delete it.

## API endpoints

The FastAPI app exposes a REST API.

- `GET /api/products` — list all products or search with `?q=keyword`
- `POST /api/products` — add a product with JSON body
- `GET /api/products/<id>` — get one product by ID
- `PUT /api/products/<id>` — update a product by ID
- `DELETE /api/products/<id>` — delete one product by ID

Example JSON body for creating a product:

```json
{
  "name": "Laptop",
  "category": "Electronics",
  "quantity": 5,
  "price": 899.99,
  "supplier": "Tech Source"
}
```

### API routes

- `GET /` — API health check
- `GET /api/products` — list all products, optional search query: `?q=keyboard`
- `POST /api/products` — add a product
- `GET /api/products/{id}` — get one product
- `PUT /api/products/{id}` — update one product
- `DELETE /api/products/{id}` — delete one product

Example JSON for creating a product:

```json
{
  "name": "Laptop",
  "category": "Electronics",
  "quantity": 5,
  "price": 899.99,
  "supplier": "Tech Source"
}
```
