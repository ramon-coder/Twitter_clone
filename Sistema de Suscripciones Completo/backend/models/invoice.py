"""
Invoice Model for Subscription and Recurring Payments Management System

This module defines the Invoice model which represents an invoice
for a subscription payment.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from main import Base


class Invoice(Base):
    """
    Invoice model represents an invoice for a subscription payment.
    """
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    due_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # pending, paid, overdue, cancelled
    invoice_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    payment = relationship("Payment", back_populates="invoice")

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"
