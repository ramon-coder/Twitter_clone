"""
Tests for Subscriptions Router in Subscription and Recurring Payments Management System

This module contains tests for the subscriptions endpoints:
- Getting all subscriptions
- Getting a specific subscription
- Creating a subscription
- Updating a subscription
- Canceling a subscription
- Renewing a subscription
"""

import pytest

def test_create_subscription(client):
    """Test creating a new subscription"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "adminpassword",
        "full_name": "Admin User",
        "phone_number": "1234567890"
    })
    
    admin_login_response = client.post("/auth/token", data={
        "username": "adminuser",
        "password": "adminpassword"
    })
    
    admin_token = admin_login_response.json()["access_token"]
    
    # Create a test plan
    client.post("/plans/", json={
        "name": "Test Plan",
        "description": "Test subscription plan",
        "price": 9.99,
        "duration": 30,
        "features": '["Test feature"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    # Create a regular user and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "phone_number": "0987654321"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get all plans to find the test plan ID
    plans_response = client.get("/plans/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = plans_response.json()[0]["id"]
    
    # Create subscription
    response = client.post("/subscriptions/", json={
        "plan_id": plan_id,
        "auto_renew": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Subscription created successfully"
    assert data["subscription"]["plan_id"] == plan_id
    assert data["subscription"]["auto_renew"] == True

def test_get_subscriptions(client):
    """Test getting all subscriptions"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser2",
        "email": "admin2@example.com",
        "password": "adminpassword"
    })
    
    admin_login_response = client.post("/auth/token", data={
        "username": "adminuser2",
        "password": "adminpassword"
    })
    
    admin_token = admin_login_response.json()["access_token"]
    
    # Create a test plan
    client.post("/plans/", json={
        "name": "Test Plan 2",
        "description": "Test subscription plan 2",
        "price": 19.99,
        "duration": 30,
        "features": '["Test feature 2"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    # Create a regular user and login
    client.post("/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser2",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get all plans to find the test plan ID
    plans_response = client.get("/plans/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = plans_response.json()[0]["id"]
    
    # Create subscription
    client.post("/subscriptions/", json={
        "plan_id": plan_id,
        "auto_renew": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    # Get all subscriptions
    response = client.get("/subscriptions/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_specific_subscription(client):
    """Test getting a specific subscription"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser3",
        "email": "admin3@example.com",
        "password": "adminpassword"
    })
    
    admin_login_response = client.post("/auth/token", data={
        "username": "adminuser3",
        "password": "adminpassword"
    })
    
    admin_token = admin_login_response.json()["access_token"]
    
    # Create a test plan
    client.post("/plans/", json={
        "name": "Test Plan 3",
        "description": "Test subscription plan 3",
        "price": 29.99,
        "duration": 30,
        "features": '["Test feature 3"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    # Create a regular user and login
    client.post("/auth/register", json={
        "username": "testuser3",
        "email": "test3@example.com",
        "password": "testpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser3",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get all plans to find the test plan ID
    plans_response = client.get("/plans/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = plans_response.json()[0]["id"]
    
    # Create subscription
    create_response = client.post("/subscriptions/", json={
        "plan_id": plan_id,
        "auto_renew": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    subscription_id = create_response.json()["subscription"]["id"]
    
    # Get specific subscription
    response = client.get(f"/subscriptions/{subscription_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == subscription_id
    assert data["plan_id"] == plan_id

def test_update_subscription(client):
    """Test updating a subscription"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser4",
        "email": "admin4@example.com",
        "password": "adminpassword"
    })
    
    admin_login_response = client.post("/auth/token", data={
        "username": "adminuser4",
        "password": "adminpassword"
    })
    
    admin_token = admin_login_response.json()["access_token"]
    
    # Create two test plans
    client.post("/plans/", json={
        "name": "Test Plan 4",
        "description": "Test subscription plan 4",
        "price": 14.99,
        "duration": 30,
        "features": '["Test feature 4"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    client.post("/plans/", json={
        "name": "Test Plan 5",
        "description": "Test subscription plan 5",
        "price": 24.99,
        "duration": 30,
        "features": '["Test feature 5"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    # Create a regular user and login
    client.post("/auth/register", json={
        "username": "testuser4",
        "email": "test4@example.com",
        "password": "testpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser4",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get all plans to find the test plan IDs
    plans_response = client.get("/plans/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id1 = plans_response.json()[0]["id"]
    plan_id2 = plans_response.json()[1]["id"]
    
    # Create subscription
    create_response = client.post("/subscriptions/", json={
        "plan_id": plan_id1,
        "auto_renew": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    subscription_id = create_response.json()["subscription"]["id"]
    
    # Update subscription
    response = client.put(f"/subscriptions/{subscription_id}", json={
        "plan_id": plan_id2,
        "auto_renew": False
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Subscription updated successfully"
    assert data["subscription"]["plan_id"] == plan_id2
    assert data["subscription"]["auto_renew"] == False

def test_cancel_subscription(client):
    """Test canceling a subscription"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser5",
        "email": "admin5@example.com",
        "password": "adminpassword"
    })
    
    admin_login_response = client.post("/auth/token", data={
        "username": "adminuser5",
        "password": "adminpassword"
    })
    
    admin_token = admin_login_response.json()["access_token"]
    
    # Create a test plan
    client.post("/plans/", json={
        "name": "Test Plan 6",
        "description": "Test subscription plan 6",
        "price": 19.99,
        "duration": 30,
        "features": '["Test feature 6"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    # Create a regular user and login
    client.post("/auth/register", json={
        "username": "testuser5",
        "email": "test5@example.com",
        "password": "testpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser5",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get all plans to find the test plan ID
    plans_response = client.get("/plans/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = plans_response.json()[0]["id"]
    
    # Create subscription
    create_response = client.post("/subscriptions/", json={
        "plan_id": plan_id,
        "auto_renew": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    subscription_id = create_response.json()["subscription"]["id"]
    
    # Cancel subscription
    response = client.put(f"/subscriptions/{subscription_id}/cancel", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Subscription cancelled successfully"
    assert data["subscription"]["status"] == "cancelled"
    assert data["subscription"]["auto_renew"] == False

def test_renew_subscription(client):
    """Test renewing a subscription"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser6",
        "email": "admin6@example.com",
        "password": "adminpassword"
    })
    
    admin_login_response = client.post("/auth/token", data={
        "username": "adminuser6",
        "password": "adminpassword"
    })
    
    admin_token = admin_login_response.json()["access_token"]
    
    # Create a test plan
    client.post("/plans/", json={
        "name": "Test Plan 7",
        "description": "Test subscription plan 7",
        "price": 29.99,
        "duration": 30,
        "features": '["Test feature 7"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    # Create a regular user and login
    client.post("/auth/register", json={
        "username": "testuser6",
        "email": "test6@example.com",
        "password": "testpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser6",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get all plans to find the test plan ID
    plans_response = client.get("/plans/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = plans_response.json()[0]["id"]
    
    # Create subscription
    create_response = client.post("/subscriptions/", json={
        "plan_id": plan_id,
        "auto_renew": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    subscription_id = create_response.json()["subscription"]["id"]
    
    # Renew subscription
    response = client.put(f"/subscriptions/{subscription_id}/renew", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Subscription renewed successfully"

def test_get_user_subscriptions(client):
    """Test getting a user's subscriptions"""
    # First, create an admin user and login
    client.post("/auth/register", json={
        "username": "adminuser7",
        "email": "admin7@example.com",
        "password": "adminpassword"
    })
    
    admin_login_response = client.post("/auth/token", data={
        "username": "adminuser7",
        "password": "adminpassword"
    })
    
    admin_token = admin_login_response.json()["access_token"]
    
    # Create a test plan
    client.post("/plans/", json={
        "name": "Test Plan 8",
        "description": "Test subscription plan 8",
        "price": 14.99,
        "duration": 30,
        "features": '["Test feature 8"]'
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    # Create a regular user and login
    client.post("/auth/register", json={
        "username": "testuser7",
        "email": "test7@example.com",
        "password": "testpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser7",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get all plans to find the test plan ID
    plans_response = client.get("/plans/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    plan_id = plans_response.json()[0]["id"]
    
    # Create subscription
    create_response = client.post("/subscriptions/", json={
        "plan_id": plan_id,
        "auto_renew": True
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    # Get user's subscriptions
    response = client.get("/subscriptions/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1