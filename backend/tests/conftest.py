# backend/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import User, Category, Product
from app.auth import get_password_hash


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(session: Session):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_category(session: Session):
    """Create a test category."""
    category = Category(
        name="Test Category",
        description="A test category",
        slug="test-category",
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@pytest.fixture
def test_product(session: Session, test_category: Category):
    """Create a test product."""
    product = Product(
        nome="Test Product",
        descricao="A test product description",
        preco=29.99,
        quantidade_estoque=10,
        image_url="https://example.com/image.jpg",
        category_id=test_category.id,
        franquia="Test Franchise",
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@pytest.fixture
def auth_headers(client: TestClient, test_user: User):
    """Get authentication headers for test user."""
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}