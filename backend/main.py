from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, webhook, inventory
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Northstar Live Inventory Sync API")

@app.get("/")
def root():
    return {"status": "ok", "service": "Northstar Inventory Sync"}

@app.post("/api/v1/webhooks/inventory", status_code=200)
def handle_inventory_webhook(payload: webhook.InventoryWebhookPayload, db: Session = Depends(get_db)):
    updated_item = inventory.update_or_create_stock(db, payload)
    return {"status": "success", "message": "Inventory updated", "data": {"sku": updated_item.sku, "quantity": updated_item.quantity}}

@app.get("/api/v1/stock/{sku}", response_model=webhook.StockCheckResponse)
def get_stock_status(sku: str, db: Session = Depends(get_db)):
    return inventory.check_stock(db, sku)
# TODO: implement
