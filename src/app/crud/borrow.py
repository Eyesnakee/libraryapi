from datetime import datetime, timezone
from typing import List, Optional
import logging

from sqlalchemy.orm import Session

from app.db.models import BorrowedBook, Book, Reader
from app.schemas.borrow import BorrowCreate

logger = logging.getLogger(__name__)


class CRUDBorrow:
    MAX_ACTIVE_BORROWS = 3

    def get(self, db: Session, id: int) -> Optional[BorrowedBook]:
        return db.query(BorrowedBook).filter(BorrowedBook.id == id).first()

    def get_active_by_reader(self, db: Session, reader_id: int) -> List[BorrowedBook]:
        return (
            db.query(BorrowedBook)
            .filter(
                BorrowedBook.reader_id == reader_id, BorrowedBook.return_date == None
            )
            .all()
        )

    def create(self, db: Session, *, obj_in: BorrowCreate) -> BorrowedBook:
        try:
            book = db.get(Book, obj_in.book_id)
            if not book or book.copies_available < 1:
                raise ValueError("Book not available")
            active_borrows = self.get_active_by_reader(db, reader_id=obj_in.reader_id)
            if len(active_borrows) >= self.MAX_ACTIVE_BORROWS:
                raise ValueError("Reader has reached the borrow limit")

            db_borrow = BorrowedBook(
                book_id=obj_in.book_id,
                reader_id=obj_in.reader_id,
                borrow_date=datetime.now(timezone.utc),
            )

            book.copies_available -= 1

            db.add(db_borrow)
            db.add(book)
            db.commit()
            db.refresh(db_borrow)
            logger.info(
                f"Book borrowed: Book ID={book.id}, Reader ID={obj_in.reader_id}"
            )
            return db_borrow
        except Exception as e:
            db.rollback()
            logger.error(f"Borrow failed: {str(e)}")
            raise

    def return_book(self, db: Session, *, db_obj: BorrowedBook) -> BorrowedBook:
        try:
            if db_obj.return_date:
                raise ValueError("Book already returned")

            db_obj.return_date = datetime.now(timezone.utc)

            book = db.get(Book, db_obj.book_id)
            if book:
                book.copies_available += 1
                db.add(book)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Book returned: Borrow ID={db_obj.id}, Book ID={book.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Return failed: {str(e)}")
            raise


borrow = CRUDBorrow()
