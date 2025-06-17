from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class BookBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        json_schema_extra={"example": "The Great Gatsby"},
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=255,
        json_schema_extra={"example": "F. Scott Fitzgerald"},
    )
    year: Optional[int] = Field(None, gt=0, json_schema_extra={"example": 1925})
    isbn: Optional[str] = Field(
        None,
        min_length=10,
        max_length=13,
        json_schema_extra={"example": "9780743273565"},
    )
    copies_available: int = Field(1, ge=0, json_schema_extra={"example": 3})
    description: Optional[str] = Field(
        None,
        max_length=1000,
        json_schema_extra={"example": "A classic novel about the American Dream"},
    )


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    year: Optional[int] = Field(None, gt=0)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    copies_available: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=1000)


class BookRead(BookBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
