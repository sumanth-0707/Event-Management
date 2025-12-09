from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
from bson.objectid import ObjectId
from app.database import get_database
from app.schemas.registration_schema import RegistrationResponseSchema, RegistrationWithEventSchema
from app.utils.auth import decode_token
from app.utils.qrcode_gen import generate_qr_code, get_qr_code_data
from app.utils.email import send_registration_email
from datetime import datetime
import uuid
import os
from app.config import settings

router = APIRouter(prefix="/registrations", tags=["registrations"])

async def get_current_user_from_request(request: Request):
    """Extract user from request cookies"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "is_admin": payload.get("is_admin", False)
    }

@router.post("/{event_id}", response_model=dict)
async def register_for_event(event_id: str, request: Request, background_tasks: BackgroundTasks):
    """Register a user for an event"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    try:
        event_oid = ObjectId(event_id)
        user_oid = ObjectId(current_user["user_id"])
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    # Check if event exists and has available seats
    event = await db["events"].find_one({"_id": event_oid})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event["available_seats"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No seats available for this event"
        )
    
    # Check if user already registered for this event
    existing_registration = await db["registrations"].find_one({
        "user_id": user_oid,
        "event_id": event_oid
    })
    
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already registered for this event"
        )
    
    # Generate ticket number
    ticket_number = f"REG_{uuid.uuid4().hex[:8].upper()}"
    
    # Get user info for email
    user = await db["users"].find_one({"_id": user_oid})
    
    # Generate QR code
    qr_data = get_qr_code_data(ticket_number, current_user["email"], event_id)
    qr_path = generate_qr_code(qr_data, ticket_number)
    
    # Create registration
    registration_dict = {
        "user_id": user_oid,
        "event_id": event_oid,
        "ticket_qr_path": qr_path,
        "ticket_number": ticket_number,
        "registration_date": datetime.utcnow()
    }
    
    result = await db["registrations"].insert_one(registration_dict)
    
    # Decrease available seats
    await db["events"].update_one(
        {"_id": event_oid},
        {"$inc": {"available_seats": -1}}
    )
    
    # Send email in background
    background_tasks.add_task(
        send_registration_email,
        current_user["email"],
        user.get("name", "User"),
        ticket_number,
        qr_path
    )
    
    return {
        "message": "Successfully registered for event",
        "registration_id": str(result.inserted_id),
        "ticket_number": ticket_number,
        "qr_code_path": qr_path
    }

@router.get("/my-registrations", response_model=list)
async def get_my_registrations(request: Request):
    """Get all registrations for current user with self-healing QR codes."""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    try:
        user_oid = ObjectId(current_user["user_id"])
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    registrations = await db["registrations"].find({"user_id": user_oid}).to_list(None)
    
    result = []
    for reg in registrations:
        ticket_number = reg.get("ticket_number")
        if not ticket_number:
            continue

        # 1. Construct the correct web path from the source of truth (ticket_number)
        qr_path_web = f"/static/qrcodes/{ticket_number}.png"
        
        # 2. Check if the file exists on disk and regenerate if not.
        filename_disk = f"{ticket_number}.png"
        filepath_disk = os.path.join(settings.QR_CODE_DIR, filename_disk)

        if not os.path.exists(filepath_disk):
            # Regenerate if missing. User is already authenticated.
            user_email = current_user.get("email")
            event_id = str(reg.get("event_id"))
            
            if user_email and event_id:
                qr_data = get_qr_code_data(ticket_number, user_email, event_id)
                generate_qr_code(qr_data, ticket_number)

        # 3. Get event details
        event = await db["events"].find_one({"_id": reg["event_id"]})
        
        result.append({
            "id": str(reg["_id"]),
            "event_id": str(reg["event_id"]),
            "event_title": event.get("title") if event else "Unknown",
            "event_date": event.get("date") if event else "",
            "event_time": event.get("time") if event else "",
            "event_venue": event.get("venue") if event else "",
            "ticket_qr_path": qr_path_web,  # Always use the reliable, constructed path
            "ticket_number": ticket_number,
            "registration_date": reg["registration_date"]
        })
    
    return result

@router.get("/admin/registrations", response_model=list)
async def get_all_registrations(request: Request):
    """Get all registrations (admin only)"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all registrations"
        )
    
    registrations = await db["registrations"].find().to_list(None)
    
    result = []
    for reg in registrations:
        # Get event and user details
        event = await db["events"].find_one({"_id": reg["event_id"]})
        user = await db["users"].find_one({"_id": reg["user_id"]})
        
        result.append({
            "id": str(reg["_id"]),
            "user_name": user.get("name") if user else "Unknown",
            "user_email": user.get("email") if user else "Unknown",
            "event_id": str(reg["event_id"]),
            "event_title": event.get("title") if event else "Unknown",
            "ticket_number": reg["ticket_number"],
            "ticket_qr_path": reg["ticket_qr_path"],
            "registration_date": reg["registration_date"]
        })
    
    return result

@router.get("/admin/registrations/event/{event_id}", response_model=list)
async def get_event_registrations(event_id: str, request: Request):
    """Get all registrations for a specific event (admin only)"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view registrations"
        )
    
    try:
        event_oid = ObjectId(event_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID"
        )
    
    # Check if event exists
    event = await db["events"].find_one({"_id": event_oid})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    registrations = await db["registrations"].find({"event_id": event_oid}).to_list(None)
    
    result = []
    for reg in registrations:
        user = await db["users"].find_one({"_id": reg["user_id"]})
        
        result.append({
            "id": str(reg["_id"]),
            "user_name": user.get("name") if user else "Unknown",
            "user_email": user.get("email") if user else "Unknown",
            "ticket_number": reg["ticket_number"],
            "registration_date": reg["registration_date"]
        })
    
    return result
