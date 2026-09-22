from inventory_app.app import run
from inventory_app.database import init_db


if __name__ == "__main__":
    init_db()
    run()
