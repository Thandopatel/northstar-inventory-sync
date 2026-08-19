from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime, timezone
from database import Base

class ProductInventory(Base):
    __tablename__ = "inventory"

    sku = Column(String, primary_key=True, index=True)
    product_name = Column(String, nullable=True)
    quantity = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))