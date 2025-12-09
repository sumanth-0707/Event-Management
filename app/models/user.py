from datetime import datetime
from typing import Optional
from bson import ObjectId

class User:
    """User model for MongoDB"""
    
    collection_name = "users"
    
    def __init__(
        self,
        name: str,
        email: str,
        password_hash: str,
        is_admin: bool = False,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash,
            "is_admin": self.is_admin,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=data.get("_id"),
            name=data.get("name"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            is_admin=data.get("is_admin", False),
            created_at=data.get("created_at")
        )
