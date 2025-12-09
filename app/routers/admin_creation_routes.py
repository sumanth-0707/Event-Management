from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from bson.objectid import ObjectId
import os
from app.database import get_database
from app.utils.auth import hash_password

router = APIRouter(tags=["admin-creation"])

def get_master_password():
    """Get master password from environment variable dynamically"""
    return os.getenv("MASTER_PASSWORD", "admin123")

class MasterPasswordRequest(BaseModel):
    master_password: str

class AdminCreationRequest(BaseModel):
    master_password: str
    name: str
    email: EmailStr
    phone: str = None
    password: str

@router.post("/verify-master-password")
async def verify_master_password(request: MasterPasswordRequest):
    """Verify master password before showing admin creation form"""
    master_password = get_master_password()
    if request.master_password != master_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid master password"
        )
    return {"message": "Master password verified"}

@router.post("/create-admin")
async def create_admin(request: AdminCreationRequest):
    """Create a new admin user"""
    
    # Verify master password
    master_password = get_master_password()
    if request.master_password != master_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid master password"
        )
    
    # Validate password length
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    db = get_database()
    users_collection = db["users"]
    
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create admin user
    admin_user = {
        "name": request.name,
        "email": request.email,
        "phone": request.phone or "",
        "password_hash": hash_password(request.password),
        "is_admin": True,
        "created_at": None  # Motor will set this
    }
    
    # Insert user
    result = await users_collection.insert_one(admin_user)
    
    return {
        "message": "Admin user created successfully",
        "user_id": str(result.inserted_id),
        "email": request.email,
        "name": request.name,
        "is_admin": True
    }

@router.get("/admin-stats")
async def get_admin_stats():
    """Get admin statistics"""
    db = get_database()
    
    users_count = await db["users"].count_documents({})
    admins_count = await db["users"].count_documents({"is_admin": True})
    events_count = await db["events"].count_documents({})
    registrations_count = await db["registrations"].count_documents({})
    
    return {
        "total_users": users_count,
        "total_admins": admins_count,
        "total_events": events_count,
        "total_registrations": registrations_count
    }
