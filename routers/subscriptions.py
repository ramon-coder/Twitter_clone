"""
Subscriptions Router for Subscription and Recurring Payments Management System

This module provides endpoints for managing subscriptions. It includes
operations for creating, retrieving, updating, and cancelling subscriptions.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from main import get_db, get_current_active_user
from models import Subscription, Plan, User
from services.payment_service import PaymentService

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_subscriptions(
    user_id: Optional[int] = None,
    plan_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all subscriptions.
    
    Args:
        user_id: Optional user ID to filter subscriptions by user
        plan_id: Optional plan ID to filter subscriptions by plan
        status: Optional status to filter subscriptions by status
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of subscriptions
    """
    # Only admin can list all subscriptions without user filter
    if user_id is None and not current_user.is_admin:
        user_id = current_user.id
    
    # Build query
    query = db.query(Subscription)
    
    if user_id:
        query = query.filter(Subscription.user_id == user_id)
    
    if plan_id:
        query = query.filter(Subscription.plan_id == plan_id)
    
    if status:
        query = query.filter(Subscription.status == status)
    
    subscriptions = query.all()
    
    return [
        {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "status": subscription.status,
            "auto_renew": subscription.auto_renew
        }
        for subscription in subscriptions
    ]

@router.get("/{subscription_id}", response_model=dict)
async def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific subscription.
    
    Args:
        subscription_id: ID of the subscription to retrieve
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Subscription details
    """
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Only admin or subscription owner can view details
    if not current_user.is_admin and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this subscription"
        )
    
    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan_id": subscription.plan_id,
        "start_date": subscription.start_date.isoformat(),
        "end_date": subscription.end_date.isoformat(),
        "status": subscription.status,
        "auto_renew": subscription.auto_renew
    }

@router.post("/", response_model=dict)
async def create_subscription(
    plan_id: int,
    auto_renew: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new subscription.
    
    Args:
        plan_id: ID of the plan to subscribe to
        auto_renew: Whether the subscription should auto-renew (default: True)
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Newly created subscription details
    """
    # Find the plan
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_active == True).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or is inactive"
        )
    
    # Check if user already has an active subscription to this plan
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.plan_id == plan_id,
        Subscription.status == "active"
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active subscription to this plan"
        )
    
    # Calculate subscription dates
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan.duration)
    
    # Create new subscription
    new_subscription = Subscription(
        user_id=current_user.id,
        plan_id=plan_id,
        start_date=start_date,
        end_date=end_date,
        status="active",
        auto_renew=auto_renew
    )
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    
    return {
        "message": "Subscription created successfully",
        "subscription": {
            "id": new_subscription.id,
            "user_id": new_subscription.user_id,
            "plan_id": new_subscription.plan_id,
            "start_date": new_subscription.start_date.isoformat(),
            "end_date": new_subscription.end_date.isoformat(),
            "status": new_subscription.status,
            "auto_renew": new_subscription.auto_renew
        }
    }

@router.put("/{subscription_id}", response_model=dict)
async def update_subscription(
    subscription_id: int,
    plan_id: Optional[int] = None,
    auto_renew: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing subscription.
    
    Args:
        subscription_id: ID of the subscription to update
        plan_id: Optional new plan ID for the subscription
        auto_renew: Optional new auto-renew status
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated subscription details
    """
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Only admin or subscription owner can update subscription
    if not current_user.is_admin and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this subscription"
        )
    
    # Update subscription fields
    if plan_id:
        # Check if plan exists and is active
        plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_active == True).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found or is inactive"
            )
        subscription.plan_id = plan_id
        # Recalculate end date if plan is changed
        subscription.end_date = datetime.utcnow() + timedelta(days=plan.duration)
    
    if auto_renew is not None:
        subscription.auto_renew = auto_renew
    
    db.commit()
    db.refresh(subscription)
    
    return {
        "message": "Subscription updated successfully",
        "subscription": {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "status": subscription.status,
            "auto_renew": subscription.auto_renew
        }
    }

@router.put("/{subscription_id}/cancel", response_model=dict)
async def cancel_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel a subscription.
    
    Args:
        subscription_id: ID of the subscription to cancel
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Success message and cancelled subscription details
    """
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Only admin or subscription owner can cancel subscription
    if not current_user.is_admin and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this subscription"
        )
    
    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is not active"
        )
    
    subscription.status = "cancelled"
    subscription.auto_renew = False
    db.commit()
    db.refresh(subscription)
    
    return {
        "message": "Subscription cancelled successfully",
        "subscription": {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "status": subscription.status,
            "auto_renew": subscription.auto_renew
        }
    }

@router.put("/{subscription_id}/renew", response_model=dict)
async def renew_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Renew a subscription.
    
    Args:
        subscription_id: ID of the subscription to renew
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Success message and renewed subscription details
    """
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Only admin or subscription owner can renew subscription
    if not current_user.is_admin and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to renew this subscription"
        )
    
    # Get the plan details to calculate renewal date
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id, Plan.is_active == True).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or is inactive"
        )
    
    # Renew the subscription
    subscription.end_date += timedelta(days=plan.duration)
    subscription.status = "active"
    db.commit()
    db.refresh(subscription)
    
    return {
        "message": "Subscription renewed successfully",
        "subscription": {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "status": subscription.status,
            "auto_renew": subscription.auto_renew
        }
    }