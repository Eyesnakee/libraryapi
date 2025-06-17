from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.crud.borrow import borrow as crud_borrow
from app.crud.book import book as crud_book
from app.crud.reader import reader as crud_reader
from app.db.session import get_db
from app.schemas.borrow import BorrowRead, BorrowCreate

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Borrow"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=BorrowRead, status_code=status.HTTP_201_CREATED)
def borrow_book(borrow_in: BorrowCreate, db: Session = Depends(get_db)):
    book = crud_book.get(db, id=borrow_in.book_id)
    if not book:
        logger.warning(f"Borrow failed: Book ID={borrow_in.book_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    reader = crud_reader.get(db, id=borrow_in.reader_id)
    if not reader:
        logger.warning(f"Borrow failed: Reader ID={borrow_in.reader_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
        )

    if book.copies_available < 1:
        logger.warning(f"Borrow failed: No available copies for book ID={book.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available copies of this book",
        )

    active_borrows = crud_borrow.get_active_by_reader(db, reader_id=reader.id)
    if len(active_borrows) >= 3:
        logger.warning(f"Borrow failed: Reader ID={reader.id} has reached the limit")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reader has reached the maximum limit of borrowed books",
        )

    borrow_record = crud_borrow.create(db, obj_in=borrow_in)
    logger.info(
        f"Book borrowed: Book ID={book.id} by Reader ID={reader.id}, Record ID={borrow_record.id}"
    )
    return borrow_record


@router.post("/return/{borrow_id}", response_model=BorrowRead)
def return_book(borrow_id: int, db: Session = Depends(get_db)):
    borrow_record = crud_borrow.get(db, id=borrow_id)
    if not borrow_record:
        logger.warning(f"Return failed: Borrow record ID={borrow_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Borrow record not found"
        )

    if borrow_record.return_date:
        logger.warning(
            f"Return failed: Book already returned for record ID={borrow_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book has already been returned",
        )

    returned_record = crud_borrow.return_book(db, db_obj=borrow_record)
    logger.info(
        f"Book returned: Record ID={returned_record.id}, Book ID={returned_record.book_id}"
    )
    return returned_record


@router.get("/reader/{reader_id}", response_model=list[BorrowRead])
def get_reader_borrows(reader_id: int, db: Session = Depends(get_db)):
    reader = crud_reader.get(db, id=reader_id)
    if not reader:
        logger.warning(f"Get borrows failed: Reader ID={reader_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
        )

    borrows = crud_borrow.get_active_by_reader(db, reader_id=reader_id)
    logger.info(f"Retrieved {len(borrows)} active borrows for Reader ID={reader_id}")
    return borrows
