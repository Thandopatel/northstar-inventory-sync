from sqlalchemy.orm import Session
from backend import models, webhook


def update_or_create_stock(db: Session, payload: webhook.InventoryWebhookPayload):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.sku == payload.sku).first()
    if not item:
        item = models.InventoryItem(
            sku=payload.sku,
            product_name=payload.product_name,
            quantity=payload.quantity,
            in_stock=payload.quantity > 0
        )
        db.add(item)
    else:
        item.quantity = payload.quantity
        item.in_stock = payload.quantity > 0
        if payload.product_name:
            item.product_name = payload.product_name
            
    db.commit()
    db.refresh(item)
    return item


def check_stock(db: Session, sku: str):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.sku == sku).first()
    if not item:
        return webhook.StockCheckResponse(sku=sku, in_stock=False, quantity=0)
    return webhook.StockCheckResponse(
        sku=item.sku,
        in_stock=item.in_stock,
        quantity=item.quantity
    )