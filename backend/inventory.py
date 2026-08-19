from sqlalchemy.orm import Session
import models
import webhook

def update_or_create_stock(db: Session, payload: webhook.InventoryWebhookPayload):
    item = db.query(models.ProductInventory).filter(models.ProductInventory.sku == payload.sku).first()
    if not item:
        item = models.ProductInventory(
            sku=payload.sku,
            product_name=payload.product_name,
            quantity=payload.quantity
        )
        db.add(item)
    else:
        item.quantity = payload.quantity
        if payload.product_name:
            item.product_name = payload.product_name
            
    db.commit()
    db.refresh(item)
    return item

def check_stock(db: Session, sku: str) -> webhook.StockCheckResponse:
    item = db.query(models.ProductInventory).filter(models.ProductInventory.sku == sku).first()
    if not item or item.quantity <= 0:
        return webhook.StockCheckResponse(sku=sku, in_stock=False, quantity=0 if not item else item.quantity)
    
    return webhook.StockCheckResponse(sku=sku, in_stock=True, quantity=item.quantity)