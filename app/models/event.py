from datetime import datetime
from typing import Optional
from bson import ObjectId

class Event:
    """Event model for MongoDB"""
    
    collection_name = "events"
    
    def __init__(
        self,
        title: str,
        description: str,
        date: str,
        time: str,
        venue: str,
        total_seats: int,
        created_by: ObjectId,
        available_seats: Optional[int] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.venue = venue
        self.total_seats = total_seats
        self.available_seats = available_seats if available_seats is not None else total_seats
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "title": self.title,
            "description": self.description,
            "date": self.date,
            "time": self.time,
            "venue": self.venue,
            "total_seats": self.total_seats,
            "available_seats": self.available_seats,
            "created_by": self.created_by,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=data.get("_id"),
            title=data.get("title"),
            description=data.get("description"),
            date=data.get("date"),
            time=data.get("time"),
            venue=data.get("venue"),
            total_seats=data.get("total_seats"),
            available_seats=data.get("available_seats"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at")
        )
