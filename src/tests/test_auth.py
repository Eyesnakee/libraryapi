from fastapi import status
import logging

logger = logging.getLogger(__name__)


def test_register(client):
    response = client.post(
        "/auth/register", json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in response.json()


def test_register_duplicate_email(client):
    client.post(
        "/auth/register", json={"email": "test@example.com", "password": "testpassword"}
    )

    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "anotherpassword"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


def test_login_success(client):
    client.post(
        "/auth/register", json={"email": "test@example.com", "password": "testpassword"}
    )

    response = client.post(
        "/auth/login", data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post(
        "/auth/register", json={"email": "test@example.com", "password": "testpassword"}
    )

    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_invalid_user(client):
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "anypassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint(auth_client):
    response = auth_client.get("/books/")
    assert response.status_code == status.HTTP_200_OK


def test_unprotected_endpoint(client):
    response = client.get("/books/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
