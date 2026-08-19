from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend import models, webhook, inventory
from backend.database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Northstar Live Inventory Sync API")

# Allow web browsers to connect to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/webhooks/inventory", response_model=webhook.WebhookResponse)
def handle_inventory_webhook(
    payload: webhook.InventoryWebhookPayload, 
    db: Session = Depends(get_db)
):
    updated_item = inventory.update_or_create_stock(db, payload)
    return webhook.WebhookResponse(
        status="success",
        message="Inventory updated successfully",
        data={"sku": updated_item.sku, "quantity": updated_item.quantity}
    )

@app.get("/api/v1/stock/{sku}", response_model=webhook.StockCheckResponse)
def check_stock_level(sku: str, db: Session = Depends(get_db)):
    return inventory.check_stock(db, sku)