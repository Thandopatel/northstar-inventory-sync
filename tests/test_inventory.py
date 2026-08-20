# test_inventory.py
# TODO: write tests
import pytest
import sqlite3
from backend.inventory import sync_stock_item
from backend.database import get_db_connection

@pytest.mark.asyncio
async def test_sync_stock_item_creates():
    """Test that sync_stock_item creates a new record"""
    # Clean up any existing test data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory_cache WHERE sku = 'TEST-001'")
    conn.commit()
    conn.close()
    
    await sync_stock_item("TEST-001", 42)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM inventory_cache WHERE sku = 'TEST-001'")
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == 42