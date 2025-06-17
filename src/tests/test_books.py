import pytest
from fastapi import status
from app.db.models import Book


def test_create_book(auth_client, db):
    response = auth_client.post(
        "/books/",
        json={"title": "New Book", "author": "New Author", "copies_available": 5},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Book"
    assert data["copies_available"] == 5


def test_create_book_with_description(auth_client, db):
    response = auth_client.post(
        "/books/",
        json={
            "title": "Book with Description",
            "author": "Author",
            "description": "This is a detailed description of the book",
            "copies_available": 3,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["description"] == "This is a detailed description of the book"
    assert data["copies_available"] == 3


def test_update_book_description(auth_client, test_book):
    response = auth_client.put(
        f"/books/{test_book.id}", json={"description": "Updated book description"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "Updated book description"


def test_create_book_duplicate_isbn(auth_client, test_book, db):
    if not test_book.isbn:
        test_book.isbn = "1234567890"
        db.commit()

    response = auth_client.post(
        "/books/",
        json={
            "title": "Duplicate Book",
            "author": "Duplicate Author",
            "isbn": test_book.isbn,
            "copies_available": 2,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Book with this ISBN already exists" in response.json()["detail"]


def test_get_books(auth_client, test_book):
    response = auth_client.get("/books/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == test_book.title


def test_get_book(auth_client, test_book):
    response = auth_client.get(f"/books/{test_book.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == test_book.title


def test_get_nonexistent_book(auth_client):
    response = auth_client.get("/books/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_book(auth_client, test_book):
    response = auth_client.put(
        f"/books/{test_book.id}",
        json={"title": "Updated Title", "copies_available": 10},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["copies_available"] == 10


def test_update_book_invalid_data(auth_client, test_book):
    response = auth_client.put(f"/books/{test_book.id}", json={"copies_available": -1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_book(auth_client, test_book):
    response = auth_client.delete(f"/books/{test_book.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = auth_client.get(f"/books/{test_book.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_book(auth_client):
    response = auth_client.delete("/books/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
