from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.db.models import Book
from app.schemas.book import BookCreate, BookUpdate

logger = logging.getLogger(__name__)


class CRUDBook:
    def get(self, db: Session, id: int) -> Optional[Book]:
        return db.query(Book).filter(Book.id == id).first()

    def get_by_isbn(self, db: Session, isbn: str) -> Optional[Book]:
        return db.query(Book).filter(Book.isbn == isbn).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Book]:
        return db.query(Book).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: BookCreate) -> Book:
        try:
            db_book = Book(**obj_in.model_dump())
            db.add(db_book)
            db.commit()
            db.refresh(db_book)
            logger.info(f"Book created: ID={db_book.id}, Title={db_book.title}")
            return db_book
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating book: {str(e)}")
            raise

    def update(self, db: Session, *, db_obj: Book, obj_in: BookUpdate) -> Book:
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Book updated: ID={db_obj.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating book ID={db_obj.id}: {str(e)}")
            raise

    def remove(self, db: Session, *, id: int) -> Optional[Book]:
        book = self.get(db, id=id)
        if book:
            try:
                db.delete(book)
                db.commit()
                logger.info(f"Book deleted: ID={id}")
                return book
            except Exception as e:
                db.rollback()
                logger.error(f"Error deleting book ID={id}: {str(e)}")
                raise
        return None


book = CRUDBook()
