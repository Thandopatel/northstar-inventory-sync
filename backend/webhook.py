from pydantic import BaseModel
from typing import Optional, Any


class InventoryWebhookPayload(BaseModel):
    sku: str
    product_name: Optional[str] = None
    quantity: int


class WebhookResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None


class StockCheckResponse(BaseModel):
    sku: str
    in_stock: bool
    quantity: int