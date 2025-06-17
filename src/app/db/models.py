from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base
import logging

logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    year = Column(Integer, nullable=True)
    isbn = Column(String, unique=True, index=True, nullable=True)
    copies_available = Column(Integer, default=1, nullable=False)
    description = Column(String, nullable=True)

    borrows = relationship("BorrowedBook", back_populates="book")

    __table_args__ = (
        CheckConstraint("copies_available >= 0", name="copies_available_non_negative"),
    )

    def __repr__(self):
        return (
            f"<Book(id={self.id}, title={self.title}, copies={self.copies_available})>"
        )


class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    borrows = relationship("BorrowedBook", back_populates="reader")

    def __repr__(self):
        return f"<Reader(id={self.id}, name={self.name})>"


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    reader_id = Column(Integer, ForeignKey("readers.id"), nullable=False)
    borrow_date = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    return_date = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="borrows")
    reader = relationship("Reader", back_populates="borrows")

    def __repr__(self):
        return (
            f"<BorrowedBook(id={self.id}, book_id={self.book_id}, "
            f"reader_id={self.reader_id}, return_date={self.return_date})>"
        )


logger.info("Database models defined")
