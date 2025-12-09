from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }

class UserResponseSchema(BaseModel):
    id: str
    name: str
    email: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "email": "john@example.com",
                "is_admin": False,
                "created_at": "2024-01-01T12:00:00"
            }
        }
