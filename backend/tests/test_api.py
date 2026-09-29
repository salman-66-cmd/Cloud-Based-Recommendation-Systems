import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "redis" in data

def test_auth_login_admin():
    response = client.post("/api/auth/login", json={
        "email": "admin@cloudrec.io",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"

def test_auth_register_and_login():
    test_email = "test.architect@cloudrec.io"
    # Register
    reg_resp = client.post("/api/auth/register", json={
        "name": "Test Architect",
        "email": test_email,
        "password": "StrongPassword!123"
    })
    # If already exists or created
    assert reg_resp.status_code in [201, 400]

    login_resp = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "StrongPassword!123"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

def test_get_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    assert "name" in data[0]
    assert "item_count" in data[0]

def test_get_items_paginated():
    response = client.get("/api/items?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 100
    assert len(data["items"]) == 10
    assert "cloud_provider" in data["items"][0]

def test_get_item_detail_and_similar():
    # Fetch first item
    items_resp = client.get("/api/items?page=1&page_size=1")
    item_id = items_resp.json()["items"][0]["id"]

    detail_resp = client.get(f"/api/items/{item_id}")
    assert detail_resp.status_code == 200
    item_data = detail_resp.json()
    assert item_data["id"] == item_id
    assert "similar_items" in item_data

def test_trending_and_popular_recommendations():
    trending = client.get("/api/recommendations/trending?limit=5")
    assert trending.status_code == 200
    assert len(trending.json()["recommendations"]) > 0

    popular = client.get("/api/recommendations/popular?limit=5")
    assert popular.status_code == 200
    assert len(popular.json()["recommendations"]) > 0

def test_personalized_recommendations():
    # Login as seeded user
    login_resp = client.post("/api/auth/login", json={
        "email": "elena.ai@cloudrec.io",
        "password": "Password@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Hybrid recommendations
    rec_resp = client.get("/api/recommendations?limit=6", headers=headers)
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert len(rec_data["recommendations"]) == 6
    assert rec_data["recommendations"][0]["reason"] != ""

    # Content-based recommendations
    cb_resp = client.get("/api/recommendations/content-based?limit=5", headers=headers)
    assert cb_resp.status_code == 200
    assert len(cb_resp.json()["recommendations"]) == 5

    # Collaborative recommendations
    cf_resp = client.get("/api/recommendations/collaborative?limit=5", headers=headers)
    assert cf_resp.status_code == 200
    assert len(cf_resp.json()["recommendations"]) == 5

def test_interactions_and_ratings_flow():
    login_resp = client.post("/api/auth/login", json={
        "email": "marcus.k8s@cloudrec.io",
        "password": "Password@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Record like
    inter_resp = client.post("/api/interactions", json={
        "item_id": 1,
        "interaction_type": "like"
    }, headers=headers)
    assert inter_resp.status_code == 201

    # Record rating
    rating_resp = client.post("/api/ratings", json={
        "item_id": 1,
        "rating": 5.0,
        "review": "Testing rating API from automated suite"
    }, headers=headers)
    assert rating_resp.status_code == 200
    assert rating_resp.json()["rating"] == 5.0

    # Verify favorites endpoint
    fav_resp = client.get("/api/interactions/favorites", headers=headers)
    assert fav_resp.status_code == 200

def test_admin_analytics_and_authorization():
    # Normal user should be rejected with 403
    user_login = client.post("/api/auth/login", json={
        "email": "marcus.k8s@cloudrec.io",
        "password": "Password@123"
    })
    user_headers = {"Authorization": f"Bearer {user_login.json()['access_token']}"}
    forbidden_resp = client.get("/api/admin/stats", headers=user_headers)
    assert forbidden_resp.status_code == 403

    # Admin user should succeed
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@cloudrec.io",
        "password": "Admin@123"
    })
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    admin_resp = client.get("/api/admin/stats", headers=admin_headers)
    assert admin_resp.status_code == 200
    stats = admin_resp.json()
    assert stats["total_users"] >= 30
    assert stats["total_items"] >= 100
    assert "user_growth" in stats
    assert "ratings_distribution" in stats
