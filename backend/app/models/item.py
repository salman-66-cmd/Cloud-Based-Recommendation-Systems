from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    tags = Column(String(500), default="", nullable=False)  # Comma-separated tags
    price = Column(Float, default=0.0)
    cloud_provider = Column(String(100), default="Multi-Cloud")  # AWS, GCP, Azure, Multi-Cloud, etc.
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    image_url = Column(String(500), nullable=True)
    features = Column(Text, default="[]")  # JSON encoded list of key feature strings
    tier = Column(String(50), default="Free Tier Available")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="items")
    ratings = relationship("Rating", back_populates="item", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="item", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="item", cascade="all, delete-orphan")
