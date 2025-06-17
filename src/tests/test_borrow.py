import pytest
from fastapi import status
from datetime import datetime
from app.db.models import Book, Reader


def test_borrow_book(auth_client, test_book, test_reader):
    response = auth_client.post(
        "/borrow/", json={"book_id": test_book.id, "reader_id": test_reader.id}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["book_id"] == test_book.id
    assert data["reader_id"] == test_reader.id
    assert data["return_date"] is None


def test_borrow_unavailable_book(auth_client, test_reader, db):
    book_data = {
        "title": "Unavailable Book",
        "author": "Unavailable Author",
        "copies_available": 0,
    }
    db_book = Book(**book_data)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    response = auth_client.post(
        "/borrow/", json={"book_id": db_book.id, "reader_id": test_reader.id}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No available copies" in response.json()["detail"]


def test_borrow_nonexistent_book(auth_client, test_reader):
    response = auth_client.post(
        "/borrow/", json={"book_id": 9999, "reader_id": test_reader.id}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_borrow_nonexistent_reader(auth_client, test_book):
    response = auth_client.post(
        "/borrow/", json={"book_id": test_book.id, "reader_id": 9999}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_borrow_limit_exceeded(auth_client, test_reader, db):
    books = []
    for i in range(4):
        book = Book(title=f"Book {i+1}", author=f"Author {i+1}", copies_available=1)
        db.add(book)
        books.append(book)
    db.commit()

    for i in range(3):
        auth_client.post(
            "/borrow/", json={"book_id": books[i].id, "reader_id": test_reader.id}
        )

    response = auth_client.post(
        "/borrow/", json={"book_id": books[3].id, "reader_id": test_reader.id}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "maximum limit" in response.json()["detail"]


def test_return_book(auth_client, test_book, test_reader, db):
    borrow_response = auth_client.post(
        "/borrow/", json={"book_id": test_book.id, "reader_id": test_reader.id}
    )
    borrow_id = borrow_response.json()["id"]

    return_response = auth_client.post(f"/borrow/return/{borrow_id}")
    assert return_response.status_code == status.HTTP_200_OK
    assert return_response.json()["return_date"] is not None

    book_response = auth_client.get(f"/books/{test_book.id}")
    assert book_response.json()["copies_available"] == test_book.copies_available


def test_return_already_returned(auth_client, test_book, test_reader):
    borrow_response = auth_client.post(
        "/borrow/", json={"book_id": test_book.id, "reader_id": test_reader.id}
    )
    borrow_id = borrow_response.json()["id"]

    auth_client.post(f"/borrow/return/{borrow_id}")

    response = auth_client.post(f"/borrow/return/{borrow_id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already been returned" in response.json()["detail"]


def test_return_nonexistent_borrow(auth_client):
    response = auth_client.post("/borrow/return/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_reader_borrows(auth_client, test_book, test_reader):
    auth_client.post(
        "/borrow/", json={"book_id": test_book.id, "reader_id": test_reader.id}
    )

    response = auth_client.get(f"/borrow/reader/{test_reader.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["book_id"] == test_book.id
    assert data[0]["return_date"] is None


def test_get_nonexistent_reader_borrows(auth_client):
    response = auth_client.get("/borrow/reader/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
