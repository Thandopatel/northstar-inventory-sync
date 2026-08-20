import pytest
from backend.warehouse_client import WarehouseClient

@pytest.mark.asyncio
async def test_mock_inventory_changes():
    """Test that mock inventory changes on each poll"""
    client = WarehouseClient()
    first = await client.fetch_inventory()
    second = await client.fetch_inventory()
    
    # The mock should change slightly
    assert first != second

@pytest.mark.asyncio
async def test_inventory_never_negative():
    """Test that mock inventory never goes below zero"""
    client = WarehouseClient()
    
    for _ in range(100):
        inventory = await client.fetch_inventory()
        for quantity in inventory.values():
            assert quantity >= 0