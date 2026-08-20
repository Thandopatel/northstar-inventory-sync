from fastapi import FastAPI, HTTPException
import logging
from .poller import InventoryPoller
from .database import get_db_connection

app = FastAPI()
poller = InventoryPoller()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Start the poller when the app starts"""
    logger.info("Application starting up...")
    poller.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the poller when the app shuts down"""
    logger.info("Application shutting down...")
    await poller.stop()

@app.get("/api/v1/stock")
async def get_stock():
    """Query endpoint: get all current inventory"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sku, quantity, last_updated FROM inventory_cache ORDER BY sku")
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "items": [
            {"sku": row[0], "quantity": row[1], "last_updated": row[2]}
            for row in rows
        ],
        "count": len(rows)
    }

@app.post("/api/v1/poll-now")
async def poll_now():
    """Manual trigger to poll warehouse immediately"""
    await poller.poll_once()
    return {"message": "Poll triggered successfully"}

# Keep your existing webhook endpoint if you have one
# Your existing webhook code can remain here...