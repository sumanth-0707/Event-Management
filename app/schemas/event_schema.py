from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventCreateSchema(BaseModel):
    title: str
    description: str
    date: str
    time: str
    venue: str
    total_seats: int
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Python Conference 2024",
                "description": "A great conference for Python developers",
                "date": "2024-06-15",
                "time": "09:00",
                "venue": "Convention Center",
                "total_seats": 500
            }
        }

class EventUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    total_seats: Optional[int] = None
    available_seats: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Conference Title",
                "available_seats": 450
            }
        }

class EventResponseSchema(BaseModel):
    id: str
    title: str
    description: str
    date: str
    time: str
    venue: str
    total_seats: int
    available_seats: int
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "title": "Python Conference 2024",
                "description": "A great conference for Python developers",
                "date": "2024-06-15",
                "time": "09:00",
                "venue": "Convention Center",
                "total_seats": 500,
                "available_seats": 450,
                "created_by": "507f1f77bcf86cd799439010",
                "created_at": "2024-01-01T12:00:00"
            }
        }
