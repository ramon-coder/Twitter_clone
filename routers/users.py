"""
Users Router for Subscription and Recurring Payments Management System

This module provides endpoints for managing users. It includes operations for
retrieving, updating, and deleting users.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from main import get_db, get_current_active_user
from models import User

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_users(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all users.
    
    Args:
        active_only: Whether to include only active users (default: True)
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of users
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can list all users"
        )
    
    if active_only:
        users = db.query(User).filter(User.is_active == True).all()
    else:
        users = db.query(User).all()
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
        for user in users
    ]

@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user.
    
    Args:
        user_id: ID of the user to retrieve
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        User details
    """
    # Only admin or user themselves can view user details
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's details"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "is_active": user.is_active,
        "is_admin": user.is_admin
    }

@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user details.
    
    Args:
        user_id: ID of the user to update
        full_name: Optional new full name for the user
        phone_number: Optional new phone number for the user
        is_active: Optional new active status for the user
        is_admin: Optional new admin status for the user
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated user details
    """
    # Only admin or user themselves can update user details
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's details"
        )
    
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    if full_name:
        user.full_name = full_name
    if phone_number:
        user.phone_number = phone_number
    if is_active is not None and current_user.is_admin:
        user.is_active = is_active
    if is_admin is not None and current_user.is_admin:
        user.is_admin = is_admin
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
    }

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a user.
    
    Args:
        user_id: ID of the user to delete
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Success message
    """
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/{user_id}/subscriptions", response_model=List[dict])
async def get_user_subscriptions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all subscriptions for a specific user.
    
    Args:
        user_id: ID of the user
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of user subscriptions
    """
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's subscriptions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return [
        {
            "id": subscription.id,
            "plan_id": subscription.plan_id,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "status": subscription.status,
            "auto_renew": subscription.auto_renew
        }
        for subscription in user.subscriptions
    ]

@router.get("/{user_id}/payments", response_model=List[dict])
async def get_user_payments(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all payments for a specific user.
    
    Args:
        user_id: ID of the user
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of user payments
    """
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's payments"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return [
        {
            "id": payment.id,
            "subscription_id": payment.subscription_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "transaction_id": payment.transaction_id,
            "created_at": payment.created_at.isoformat()
        }
        for payment in user.payments
    ]