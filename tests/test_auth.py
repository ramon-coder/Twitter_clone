"""
Tests for Authentication Router in Subscription and Recurring Payments Management System

This module contains tests for the authentication endpoints:
- Token generation
- User registration
- Password change
- Password reset
- Getting current user information
"""

import pytest

def test_register_user(client):
    """Test registering a new user"""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "phone_number": "1234567890"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "testuser@example.com"

def test_register_existing_user(client):
    """Test registering a user with an existing username"""
    # First, register a user
    client.post("/auth/register", json={
        "username": "existinguser",
        "email": "existinguser@example.com",
        "password": "password123"
    })
    
    # Attempt to register the same user again
    response = client.post("/auth/register", json={
        "username": "existinguser",
        "email": "anotheremail@example.com",
        "password": "password456"
    })
    
    assert response.status_code == 400

def test_login_with_valid_credentials(client):
    """Test login with valid credentials"""
    # First, register a user
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "testpassword123"
    })
    
    # Attempt login
    response = client.post("/auth/token", data={
        "username": "loginuser",
        "password": "testpassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_with_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post("/auth/token", data={
        "username": "nonexistentuser",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401

def test_get_current_user(client):
    """Test getting current user information"""
    # First, register a user
    client.post("/auth/register", json={
        "username": "currentuser",
        "email": "currentuser@example.com",
        "password": "testpassword"
    })
    
    # Login to get token
    login_response = client.post("/auth/token", data={
        "username": "currentuser",
        "password": "testpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/auth/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "currentuser@example.com"

def test_change_password(client):
    """Test changing password"""
    # First, register a user
    client.post("/auth/register", json={
        "username": "changepassuser",
        "email": "changepass@example.com",
        "password": "oldpassword"
    })
    
    # Login to get token
    login_response = client.post("/auth/token", data={
        "username": "changepassuser",
        "password": "oldpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Change password
    response = client.post("/auth/change-password", json={
        "current_password": "oldpassword",
        "new_password": "newpassword"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

def test_change_password_invalid_current(client):
    """Test changing password with invalid current password"""
    # First, register a user
    client.post("/auth/register", json={
        "username": "invalidpassuser",
        "email": "invalidpass@example.com",
        "password": "oldpassword"
    })
    
    # Login to get token
    login_response = client.post("/auth/token", data={
        "username": "invalidpassuser",
        "password": "oldpassword"
    })
    
    token = login_response.json()["access_token"]
    
    # Attempt to change password with invalid current password
    response = client.post("/auth/change-password", json={
        "current_password": "wrongpassword",
        "new_password": "newpassword"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 400

def test_reset_password(client):
    """Test requesting password reset"""
    # First, register a user
    client.post("/auth/register", json={
        "username": "resetpassuser",
        "email": "resetpass@example.com",
        "password": "testpassword"
    })
    
    # Request password reset
    response = client.post("/auth/reset-password", json={
        "email": "resetpass@example.com"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset link has been sent to your email"

def test_reset_password_nonexistent_email(client):
    """Test requesting password reset for nonexistent email"""
    response = client.post("/auth/reset-password", json={
        "email": "nonexistent@example.com"
    })
    
    assert response.status_code == 404