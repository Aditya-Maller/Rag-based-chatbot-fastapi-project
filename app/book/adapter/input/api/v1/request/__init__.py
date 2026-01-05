from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class LoginRequest(BaseModel):
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class CreateBookRequest(BaseModel):
    book_id: int=Field(..., description="Unique Book ID")
    name: str=Field(...,description="Name of the student")
    book_title: str=Field(..., description="Title of the book")
    book_pages: int=Field(..., description="Number of pages")
    pub_date: date=Field(..., description="YYYY-MM-DD")
    price: float=Field(...,description="Book price")


class UpdateBookRequest(BaseModel):
    name: Optional[str] = None
    book_title: Optional[str] = None
    book_pages: Optional[int] = None
    pub_date: Optional[date] = None
    price: Optional[float] = None