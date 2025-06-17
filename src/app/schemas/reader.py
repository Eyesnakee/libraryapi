from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class ReaderBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, json_schema_extra={"example": "John Doe"}
    )
    email: EmailStr = Field(..., json_schema_extra={"example": "john@example.com"})


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None)


class ReaderRead(ReaderBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
