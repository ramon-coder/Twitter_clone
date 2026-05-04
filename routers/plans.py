"""
Plans Router for Subscription and Recurring Payments Management System

This module provides endpoints for managing subscription plans. It includes
operations for creating, retrieving, updating, and deleting plans.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from main import get_db, get_current_active_user
from models import Plan, User

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_plans(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all subscription plans.
    
    Args:
        active_only: Whether to include only active plans (default: True)
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of subscription plans
    """
    if active_only:
        plans = db.query(Plan).filter(Plan.is_active == True).all()
    else:
        plans = db.query(Plan).all()
    
    return [
        {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "price": plan.price,
            "duration": plan.duration,
            "features": plan.features,
            "is_active": plan.is_active
        }
        for plan in plans
    ]

@router.get("/{plan_id}", response_model=dict)
async def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific subscription plan.
    
    Args:
        plan_id: ID of the plan to retrieve
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Subscription plan details
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "price": plan.price,
        "duration": plan.duration,
        "features": plan.features,
        "is_active": plan.is_active
    }

@router.post("/", response_model=dict)
async def create_plan(
    name: str,
    description: Optional[str] = None,
    price: float = 0.0,
    duration: int = 30,
    features: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new subscription plan.
    
    Args:
        name: Name of the new plan
        description: Optional description of the plan
        price: Price of the plan (default: 0.0)
        duration: Duration of the plan in days (default: 30)
        features: Optional JSON string of plan features
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Newly created plan details
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create plans"
        )
    
    # Check if plan name already exists
    existing_plan = db.query(Plan).filter(Plan.name == name).first()
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan name already exists"
        )
    
    # Create new plan
    new_plan = Plan(
        name=name,
        description=description,
        price=price,
        duration=duration,
        features=features,
        is_active=True
    )
    
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return {
        "message": "Plan created successfully",
        "plan": {
            "id": new_plan.id,
            "name": new_plan.name,
            "description": new_plan.description,
            "price": new_plan.price,
            "duration": new_plan.duration,
            "features": new_plan.features,
            "is_active": new_plan.is_active
        }
    }

@router.put("/{plan_id}", response_model=dict)
async def update_plan(
    plan_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    duration: Optional[int] = None,
    features: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing subscription plan.
    
    Args:
        plan_id: ID of the plan to update
        name: Optional new name for the plan
        description: Optional new description for the plan
        price: Optional new price for the plan
        duration: Optional new duration for the plan in days
        features: Optional new JSON string of plan features
        is_active: Optional new active status for the plan
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated plan details
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update plans"
        )
    
    # Find the plan
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Update plan fields
    if name:
        plan.name = name
    if description:
        plan.description = description
    if price is not None:
        plan.price = price
    if duration is not None:
        plan.duration = duration
    if features:
        plan.features = features
    if is_active is not None:
        plan.is_active = is_active
    
    db.commit()
    db.refresh(plan)
    
    return {
        "message": "Plan updated successfully",
        "plan": {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "price": plan.price,
            "duration": plan.duration,
            "features": plan.features,
            "is_active": plan.is_active
        }
    }

@router.delete("/{plan_id}", response_model=dict)
async def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a subscription plan.
    
    Args:
        plan_id: ID of the plan to delete
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Success message
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete plans"
        )
    
    # Find the plan
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Delete the plan
    db.delete(plan)
    db.commit()
    
    return {"message": "Plan deleted successfully"}