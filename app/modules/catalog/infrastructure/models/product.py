from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    category = relationship("Category")
    inventory = relationship("Inventory", uselist=False, back_populates="product")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


    