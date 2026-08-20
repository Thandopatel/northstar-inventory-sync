import random
import os
from typing import Dict, List, Optional
import httpx

class WarehouseClient:
    """Client to fetch inventory from warehouse system"""
    
    def __init__(self):
        self.api_url = os.getenv("WAREHOUSE_API_URL")
        self.use_mock = not self.api_url
        self.mock_inventory = self._init_mock_inventory()
    
    def _init_mock_inventory(self) -> Dict[str, int]:
        """Initialize mock inventory with some sample products"""
        return {
            "SKU-001": 100,
            "SKU-002": 50,
            "SKU-003": 75,
            "SKU-004": 200,
            "SKU-005": 30,
        }
    
    async def fetch_inventory(self) -> Dict[str, int]:
        """Fetch current inventory from warehouse or mock"""
        if self.use_mock:
            # Simulate small random changes for testing
            for sku in self.mock_inventory:
                change = random.randint(-5, 5)
                self.mock_inventory[sku] = max(0, self.mock_inventory[sku] + change)
            return self.mock_inventory.copy()
        else:
            # Real API call
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.api_url}/inventory")
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError as e:
                    raise Exception(f"Failed to fetch inventory: {e}")