from pydantic import BaseModel
from datetime import datetime

class RegistrationResponseSchema(BaseModel):
    id: str
    user_id: str
    event_id: str
    ticket_qr_path: str
    ticket_number: str
    registration_date: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439010",
                "event_id": "507f1f77bcf86cd799439009",
                "ticket_qr_path": "/static/qrcodes/REG_12345.png",
                "ticket_number": "REG_12345",
                "registration_date": "2024-01-01T12:00:00"
            }
        }

class RegistrationWithEventSchema(BaseModel):
    id: str
    event_id: str
    event_title: str
    event_date: str
    event_time: str
    event_venue: str
    ticket_qr_path: str
    ticket_number: str
    registration_date: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "event_id": "507f1f77bcf86cd799439009",
                "event_title": "Python Conference 2024",
                "event_date": "2024-06-15",
                "event_time": "09:00",
                "event_venue": "Convention Center",
                "ticket_qr_path": "/static/qrcodes/REG_12345.png",
                "ticket_number": "REG_12345",
                "registration_date": "2024-01-01T12:00:00"
            }
        }
