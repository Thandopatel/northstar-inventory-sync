# webhook.py
# TODO: implement
from pydantic import BaseModel
from typing import Optional

class InventoryWebhookPayload(BaseModel):
    sku: str
    product_name: Optional[str] = None
    quantity: int

class StockCheckResponse(BaseModel):
    sku: str
    in_stock: bool
    quantity: int