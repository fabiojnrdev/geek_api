# backend/tests/test_products.py

import pytest
from fastapi import status
from decimal import Decimal


def test_get_products_empty(client):
    """Test getting products when none exist."""
    response = client.get("/products/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["size"] == 10


def test_get_products_with_data(client, test_product, test_category):
    """Test getting products with existing data."""
    response = client.get("/products/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1

    product = data["items"][0]
    assert product["nome"] == "Test Product"
    assert product["preco"] == "29.99"
    assert product["category"]["name"] == "Test Category"


def test_get_products_pagination(client, session, test_category):
    """Test products pagination."""
    # Create multiple products
    from app.models import Product
    for i in range(15):
        product = Product(
            nome=f"Product {i}",
            descricao=f"Description {i}",
            preco=Decimal("10.00"),
            quantidade_estoque=5,
            image_url="https://example.com/image.jpg",
            category_id=test_category.id,
            franquia=f"Franchise {i}",
        )
        session.add(product)
    session.commit()

    # Test first page
    response = client.get("/products/?page=1&size=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15
    assert data["page"] == 1

    # Test second page
    response = client.get("/products/?page=2&size=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15
    assert data["page"] == 2


def test_get_products_search(client, session, test_category):
    """Test products search functionality."""
    # Create products with different names
    from app.models import Product
    products_data = [
        ("Star Wars Figure", "A Star Wars action figure"),
        ("Marvel Comic", "A Marvel comic book"),
        ("Pokemon Card", "A Pokemon trading card"),
    ]

    for nome, desc in products_data:
        product = Product(
            nome=nome,
            descricao=desc,
            preco=Decimal("15.00"),
            quantidade_estoque=5,
            image_url="https://example.com/image.jpg",
            category_id=test_category.id,
            franquia="Test Franchise",
        )
        session.add(product)
    session.commit()

    # Search for "Star Wars"
    response = client.get("/products/?search=Star%20Wars")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert "Star Wars" in data["items"][0]["nome"]

    # Search for "Marvel"
    response = client.get("/products/?search=Marvel")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert "Marvel" in data["items"][0]["nome"]


def test_create_product_success(client, auth_headers, test_category):
    """Test successful product creation."""
    product_data = {
        "nome": "New Product",
        "descricao": "A new product description",
        "preco": "49.99",
        "quantidade_estoque": 20,
        "image_url": "https://example.com/new-image.jpg",
        "category_id": test_category.id,
        "franquia": "New Franchise"
    }

    response = client.post(
        "/products/",
        json=product_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["nome"] == "New Product"
    assert data["preco"] == "49.99"
    assert data["quantidade_estoque"] == 20
    assert data["category"]["id"] == test_category.id


def test_create_product_validation_errors(client, auth_headers, test_category):
    """Test product creation with validation errors."""

    # Test missing required fields
    incomplete_data = {
        "nome": "Test Product",
        # Missing descricao, preco, etc.
    }

    response = client.post(
        "/products/",
        json=incomplete_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test invalid preco (negative)
    invalid_data = {
        "nome": "Test Product",
        "descricao": "Description",
        "preco": "-10.00",
        "quantidade_estoque": 5,
        "image_url": "https://example.com/image.jpg",
        "category_id": test_category.id,
        "franquia": "Franchise"
    }

    response = client.post(
        "/products/",
        json=invalid_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test invalid category_id
    invalid_category_data = {
        "nome": "Test Product",
        "descricao": "Description",
        "preco": "10.00",
        "quantidade_estoque": 5,
        "image_url": "https://example.com/image.jpg",
        "category_id": 99999,  # Non-existent category
        "franquia": "Franchise"
    }

    response = client.post(
        "/products/",
        json=invalid_category_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Categoria não encontrada" in response.json()["detail"]


def test_create_product_unauthorized(client, test_category):
    """Test product creation without authentication."""
    product_data = {
        "nome": "New Product",
        "descricao": "Description",
        "preco": "29.99",
        "quantidade_estoque": 10,
        "image_url": "https://example.com/image.jpg",
        "category_id": test_category.id,
        "franquia": "Franchise"
    }

    response = client.post("/products/", json=product_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED