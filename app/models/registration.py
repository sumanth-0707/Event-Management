from datetime import datetime
from typing import Optional
from bson import ObjectId

class Registration:
    """Registration model for MongoDB"""
    
    collection_name = "registrations"
    
    def __init__(
        self,
        user_id: ObjectId,
        event_id: ObjectId,
        ticket_qr_path: str,
        ticket_number: str,
        _id: Optional[ObjectId] = None,
        registration_date: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.event_id = event_id
        self.ticket_qr_path = ticket_qr_path
        self.ticket_number = ticket_number
        self.registration_date = registration_date or datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "ticket_qr_path": self.ticket_qr_path,
            "ticket_number": self.ticket_number,
            "registration_date": self.registration_date
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=data.get("_id"),
            user_id=data.get("user_id"),
            event_id=data.get("event_id"),
            ticket_qr_path=data.get("ticket_qr_path"),
            ticket_number=data.get("ticket_number"),
            registration_date=data.get("registration_date")
        )
