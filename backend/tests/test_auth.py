# backend/tests/test_auth.py

import pytest
from fastapi import status
from sqlmodel import Session


def test_register_success(client, session: Session):
    """Test successful user registration."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert data["is_active"] is True


def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username fails."""
    user_data = {
        "username": "testuser",  # Same as test_user
        "email": "different@example.com",
        "password": "password123"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username já está em uso" in response.json()["detail"]


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email fails."""
    user_data = {
        "username": "differentuser",
        "email": "test@example.com",  # Same as test_user
        "password": "password123"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email já está em uso" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login."""
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_username(client):
    """Test login with wrong username."""
    login_data = {
        "username": "wronguser",
        "password": "testpass123"
    }

    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Username ou senha incorretos" in response.json()["detail"]


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }

    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Username ou senha incorretos" in response.json()["detail"]