import pytest
from fastapi import status
from app.db.models import Reader


def test_create_reader(auth_client):
    response = auth_client.post(
        "/readers/", json={"name": "John Doe", "email": "john@example.com"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"


def test_create_reader_duplicate_email(auth_client, test_reader):
    response = auth_client.post(
        "/readers/", json={"name": "Jane Doe", "email": test_reader.email}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


def test_get_readers(auth_client, test_reader):
    response = auth_client.get("/readers/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_reader.name


def test_get_reader(auth_client, test_reader):
    response = auth_client.get(f"/readers/{test_reader.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_reader.name


def test_get_nonexistent_reader(auth_client):
    response = auth_client.get("/readers/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_reader(auth_client, test_reader):
    response = auth_client.put(
        f"/readers/{test_reader.id}", json={"name": "Updated Name"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"


def test_update_reader_duplicate_email(auth_client, test_reader, db):
    reader2 = Reader(name="Another Reader", email="another@example.com")
    db.add(reader2)
    db.commit()
    db.refresh(reader2)

    response = auth_client.put(
        f"/readers/{reader2.id}", json={"email": test_reader.email}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


def test_delete_reader(auth_client, test_reader):
    response = auth_client.delete(f"/readers/{test_reader.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = auth_client.get(f"/readers/{test_reader.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_reader(auth_client):
    response = auth_client.delete("/readers/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
