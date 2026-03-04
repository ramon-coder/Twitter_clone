"""
Tests for Plans Router in Subscription and Recurring Payments Management System

This module contains tests for the plans endpoints:
- Getting all plans
- Getting a specific plan
- Creating a plan
- Updating a plan
- Deleting a plan
"""

import pytest

def test_get_all_plans(client):
    """Test getting all plans"""
    response = client.get("/plans/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_plan(client):
    """Test creating a new plan"""
    # First, create an admin user
    client.post("/auth/register", json={
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "adminpassword",
        "full_name": "Admin User",
        "phone_number": "1234567890"
    })
    
    # Login as admin
    login_response = client.post("/auth/token", data={
        "username": "adminuser",
        "password": "adminpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Create a new plan
    response = client.post("/plans/", json={
        "name": "Premium",
        "description": "Premium plan with all features",
        "price": 29.99,
        "duration": 30,
        "features": '["Unlimited access", "Priority support", "Advanced analytics"]'
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Plan created successfully"
    assert data["plan"]["name"] == "Premium"
    assert data["plan"]["price"] == 29.99

def test_create_plan_with_existing_name(client):
    """Test creating a plan with an existing name"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser2",
        "email": "admin2@example.com",
        "password": "adminpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "adminuser2",
        "password": "adminpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Create first plan
    client.post("/plans/", json={
        "name": "Basic",
        "description": "Basic plan",
        "price": 9.99,
        "duration": 30,
        "features": '["Limited access"]'
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    # Attempt to create plan with same name
    response = client.post("/plans/", json={
        "name": "Basic",
        "description": "Another basic plan",
        "price": 14.99,
        "duration": 30,
        "features": '["Some features"]'
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 400

def test_get_specific_plan(client):
    """Test getting a specific plan"""
    # First, create an admin user, login, and create a plan
    client.post("/auth/register", json={
        "username": "adminuser3",
        "email": "admin3@example.com",
        "password": "adminpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "adminuser3",
        "password": "adminpassword"
    })
    
    token = login_response.json()["access_token"]
    
    create_response = client.post("/plans/", json={
        "name": "Test Plan",
        "description": "Test plan description",
        "price": 19.99,
        "duration": 30,
        "features": '["Test feature"]'
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = create_response.json()["plan"]["id"]
    
    # Get the specific plan
    response = client.get(f"/plans/{plan_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plan_id
    assert data["name"] == "Test Plan"

def test_get_nonexistent_plan(client):
    """Test getting a nonexistent plan"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser4",
        "email": "admin4@example.com",
        "password": "adminpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "adminuser4",
        "password": "adminpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Attempt to get a nonexistent plan
    response = client.get("/plans/999", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404

def test_update_plan(client):
    """Test updating a plan"""
    # First, create an admin user, login, and create a plan
    client.post("/auth/register", json={
        "username": "adminuser5",
        "email": "admin5@example.com",
        "password": "adminpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "adminuser5",
        "password": "adminpassword"
    })
    
    token = login_response.json()["access_token"]
    
    create_response = client.post("/plans/", json={
        "name": "Update Test Plan",
        "description": "Original description",
        "price": 19.99,
        "duration": 30,
        "features": '["Original feature"]'
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = create_response.json()["plan"]["id"]
    
    # Update the plan
    response = client.put(f"/plans/{plan_id}", json={
        "name": "Updated Test Plan",
        "description": "Updated description",
        "price": 24.99,
        "duration": 30,
        "features": '["Updated feature"]',
        "is_active": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Plan updated successfully"
    assert data["plan"]["name"] == "Updated Test Plan"
    assert data["plan"]["price"] == 24.99

def test_delete_plan(client):
    """Test deleting a plan"""
    # First, create an admin user, login, and create a plan
    client.post("/auth/register", json={
        "username": "adminuser6",
        "email": "admin6@example.com",
        "password": "adminpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "adminuser6",
        "password": "adminpassword"
    })
    
    token = login_response.json()["access_token"]
    
    create_response = client.post("/plans/", json={
        "name": "Delete Test Plan",
        "description": "Test plan to be deleted",
        "price": 9.99,
        "duration": 30,
        "features": '["To be deleted"]'
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = create_response.json()["plan"]["id"]
    
    # Delete the plan
    response = client.delete(f"/plans/{plan_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "Plan deleted successfully"

def test_non_admin_cannot_create_plan(client):
    """Test that a non-admin user cannot create a plan"""
    # First, create a regular user
    client.post("/auth/register", json={
        "username": "regularuser",
        "email": "regular@example.com",
        "password": "regularpassword"
    })
    
    # Login as regular user
    login_response = client.post("/auth/token", data={
        "username": "regularuser",
        "password": "regularpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Attempt to create a plan
    response = client.post("/plans/", json={
        "name": "NonAdmin Plan",
        "description": "Plan created by non-admin user",
        "price": 9.99,
        "duration": 30,
        "features": '["Test feature"]'
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 403