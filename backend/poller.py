import asyncio
import logging
import os
from .warehouse_client import WarehouseClient
from .inventory import sync_stock_item

logger = logging.getLogger(__name__)

class InventoryPoller:
    """Background poller that fetches inventory every 5 minutes"""
    
    def __init__(self):
        self.client = WarehouseClient()
        self.interval = int(os.getenv("POLL_INTERVAL_SECONDS", 300))  # 5 minutes default
        self.running = False
        self.task = None
    
    async def poll_once(self) -> None:
        """Fetch inventory once and update cache"""
        try:
            logger.info("Polling warehouse for inventory...")
            inventory = await self.client.fetch_inventory()
            
            for sku, quantity in inventory.items():
                await sync_stock_item(sku, quantity)
            
            logger.info(f"Successfully updated {len(inventory)} items")
        except Exception as e:
            logger.error(f"Poll failed: {e}")
            # Don't raise - we want the loop to continue
    
    async def _poll_loop(self) -> None:
        """Main polling loop"""
        logger.info(f"Starting poller with interval of {self.interval}s")
        
        # Poll immediately on startup
        await self.poll_once()
        
        while self.running:
            await asyncio.sleep(self.interval)
            if self.running:
                await self.poll_once()
    
    def start(self) -> None:
        """Start the poller in background"""
        if self.running:
            return
        
        self.running = True
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self._poll_loop())
        logger.info("Poller started")
    
    async def stop(self) -> None:
        """Stop the poller"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Poller stopped")