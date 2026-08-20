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

@pytest.mark.asyncio
async def test_mock_inventory_has_correct_skus():
    """Test that mock inventory has the expected SKUs"""
    client = WarehouseClient()
    inventory = await client.fetch_inventory()
    
    expected_skus = ["SKU-001", "SKU-002", "SKU-003", "SKU-004", "SKU-005"]
    for sku in expected_skus:
        assert sku in inventory

@pytest.mark.asyncio
async def test_mock_inventory_values_are_integers():
    """Test that all inventory values are integers"""
    client = WarehouseClient()
    inventory = await client.fetch_inventory()
    
    for quantity in inventory.values():
        assert isinstance(quantity, int)

@pytest.mark.asyncio
async def test_api_client_initialization():
    """Test that the API client initializes correctly"""
    client = WarehouseClient()
    assert client is not None
    assert hasattr(client, 'fetch_inventory')
    assert hasattr(client, 'mock_inventory')

@pytest.mark.asyncio
async def test_mock_inventory_structure():
    """Test that mock inventory returns a dictionary"""
    client = WarehouseClient()
    inventory = await client.fetch_inventory()
    
    # Should be a dictionary
    assert isinstance(inventory, dict)
    
    # Keys should be strings (SKUs)
    for sku in inventory.keys():
        assert isinstance(sku, str)

@pytest.mark.asyncio
async def test_mock_inventory_consistency():
    """Test that mock inventory values stay within a reasonable range"""
    client = WarehouseClient()
    
    # Run multiple polls and collect all values
    all_values = []
    for _ in range(10):
        inventory = await client.fetch_inventory()
        all_values.extend(inventory.values())
    
    # Values should never be negative
    assert all(v >= 0 for v in all_values)
    
    # Values should be reasonable (not huge numbers)
    assert all(v < 10000 for v in all_values)