from dataclasses import dataclass


@dataclass
class Product:
    name: str
    category: str
    quantity: int
    price: float
    supplier: str
    id: int | None = None

    @property
    def total_value(self) -> float:
        return self.quantity * self.price
