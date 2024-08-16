from fastapi.testclient import TestClient
from fastapi import status
from main import app
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from config.database import get_db
from config.database import Base
import pytest
from app.models import Product, Combo
from httpx import AsyncClient

client = TestClient(app)

DATABASE_URL = 'sqlite:///:memory:'

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Product(sku="A", price=10.0))
    db.add(Product(sku="B", price=10.0))
    db.add(Combo(product_id=1, quantity=2, price=18.0))
    db.add(Combo(product_id=2, quantity=5, price=40.0))
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_get_products_and_combos(setup_database):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/products/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] is True
    assert len(data["products_and_combos"]) == 2
    assert len(data["products_and_combos"][0]['combos']) == 1
    assert any(combo['quantity'] == 2 and combo['price'] == 18.0 for combo in data["products_and_combos"][0]['combos'])
    assert len(data["products_and_combos"][1]['combos']) == 1
    assert any(combo['quantity'] == 5 and combo['price'] == 40.0 for combo in data["products_and_combos"][1]['combos'])

@pytest.mark.asyncio
async def test_calculate_total_with_missing_product(setup_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/calculate_total/", json=[
            {"id": 999, "sku":"A", "quantity": 1}
        ])
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data['status'] is False
    assert "Product not found" in data['message']

@pytest.mark.asyncio
async def test_calculate_total_with_combo_and_non_combo_products(setup_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/calculate_total/", json=[
            {"id": 1, "sku": "A", "quantity": 4},
            {"id": 2, "sku": "B", "quantity": 3}
        ])
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['status'] is True
    assert data['total'] == 66.0
    assert len(data['invoice']) == 2
    assert data['invoice'][0]['combo_quantity'] == 2
    assert data['invoice'][1]['combo_quantity'] == 0
    assert data['invoice'][0]['total_cost'] == 36.0
    assert data['invoice'][1]['total_cost'] == 30.0
