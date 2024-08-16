from pydantic import BaseModel


class CartItem(BaseModel):
    id: int
    sku: str
    quantity: int
