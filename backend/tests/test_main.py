def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Reporte Bolívar API" in response.json()["message"]

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_ready" in data

def test_register_and_login(client):
    # Test register
    user_data = {
        "email": "test@example.com",
        "password": "secretpassword",
        "name": "Test User"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    
    # Test duplicate register
    response_dup = client.post("/api/auth/register", json=user_data)
    assert response_dup.status_code == 400
    
    # Test login
    login_data = {
        "username": "test@example.com",
        "password": "secretpassword"
    }
    response_login = client.post("/api/auth/login", data=login_data)
    assert response_login.status_code == 200
    token_data = response_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Test auth /me
    token = token_data["access_token"]
    response_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response_me.status_code == 200
    me_data = response_me.json()
    assert me_data["email"] == "test@example.com"

def test_get_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
