"""
Plan Model for Subscription and Recurring Payments Management System

This module defines the Plan model which represents a subscription plan
with details like price, duration, and features.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from main import Base


class Plan(Base):
    """
    Plan model represents a subscription plan with details like price, duration, and features.
    """
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # In days
    features = Column(String)  # JSON string of features
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plan {self.name}>"
