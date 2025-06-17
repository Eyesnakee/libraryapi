from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.security import get_current_user
from app.crud.book import book as crud_book
from app.db.session import get_db
from app.schemas.book import BookCreate, BookUpdate, BookRead

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Books"], dependencies=[Depends(get_current_user)]  # Убрали prefix="/books"
)


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    if book_in.isbn and crud_book.get_by_isbn(db, isbn=book_in.isbn):
        logger.warning(f"Book creation with duplicate ISBN: {book_in.isbn}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this ISBN already exists",
        )

    book = crud_book.create(db, obj_in=book_in)
    logger.info(f"Book created: ID={book.id}, Title={book.title}")
    return book


@router.get("/", response_model=list[BookRead])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud_book.get_multi(db, skip=skip, limit=limit)
    logger.info(f"Read {len(books)} books")
    return books


@router.get("/{book_id}", response_model=BookRead)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = crud_book.get(db, id=book_id)
    if not book:
        logger.warning(f"Book not found: ID={book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)):
    book = crud_book.get(db, id=book_id)
    if not book:
        logger.warning(f"Book update failed: ID={book_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    if book_in.isbn and book_in.isbn != book.isbn:
        if crud_book.get_by_isbn(db, isbn=book_in.isbn):
            logger.warning(f"Book update with duplicate ISBN: {book_in.isbn}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists",
            )

    updated_book = crud_book.update(db, db_obj=book, obj_in=book_in)
    logger.info(f"Book updated: ID={updated_book.id}")
    return updated_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = crud_book.get(db, id=book_id)
    if not book:
        logger.warning(f"Book delete failed: ID={book_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    crud_book.remove(db, id=book_id)
    logger.info(f"Book deleted: ID={book_id}")
    return None
