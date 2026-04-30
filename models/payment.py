"""
Payment Model for Subscription and Recurring Payments Management System

This module defines the Payment model which represents a payment
transaction for a subscription.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from main import Base


class Payment(Base):
    """
    Payment model represents a payment transaction for a subscription.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False)  # pending, succeeded, failed, refunded
    payment_method = Column(String)  # stripe, paypal, mercado_pago
    transaction_id = Column(String, unique=True, index=True)
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payment", uselist=False)

    def __repr__(self):
        return f"<Payment {self.id}>"
