from fastapi import FastAPI, HTTPException
import logging
from .database import get_db_connection

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/api/v1/stock")
async def get_stock():
    """Query endpoint: get all current inventory"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sku, quantity, last_updated FROM inventory_cache ORDER BY sku")
    rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    inventory = []
    for row in rows:
        inventory.append({
            "sku": row[0],
            "quantity": row[1],
            "last_updated": row[2]
        })
    
    conn.close()
    return {"inventory": inventory}

@app.get("/api/v1/stock/{sku}")
async def get_stock_by_sku(sku: str):
    """Query endpoint: get inventory for a specific SKU"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sku, quantity, last_updated FROM inventory_cache WHERE sku = ?",
        (sku,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"SKU {sku} not found")
    
    return {
        "sku": row[0],
        "quantity": row[1],
        "last_updated": row[2]
    }

@app.post("/api/v1/webhooks/inventory")
async def webhook_inventory_update(request: dict):
    """Webhook endpoint: receive inventory updates from warehouse"""
    try:
        sku = request.get("sku")
        quantity = request.get("quantity")
        
        if not sku or quantity is None:
            raise HTTPException(status_code=400, detail="Missing sku or quantity")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Upsert: update if exists, insert if not
        cursor.execute("""
            INSERT INTO inventory_cache (sku, quantity, last_updated)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(sku) DO UPDATE SET
                quantity = excluded.quantity,
                last_updated = datetime('now')
        """, (sku, quantity))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Inventory updated via webhook: SKU={sku}, Quantity={quantity}")
        return {"status": "success", "sku": sku, "quantity": quantity}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint: service status"""
    return {
        "service": "northstar-inventory-sync",
        "status": "running",
        "version": "2.0.0",
        "model": "webhook-push"
    }