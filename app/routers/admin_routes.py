from fastapi import APIRouter, HTTPException, status, Request
from bson.objectid import ObjectId
from app.database import get_database
from app.utils.auth import decode_token

router = APIRouter(prefix="/admin", tags=["admin"])

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

@router.get("/dashboard-data")
async def get_dashboard_data(request: Request):
    """Get admin dashboard data"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this"
        )
    
    # Get admin's events
    admin_id = ObjectId(current_user["user_id"])
    events = await db["events"].find({"created_by": admin_id}).to_list(None)
    
    # Calculate stats
    total_events = len(events)
    total_seats_available = sum(e.get("available_seats", 0) for e in events)
    total_seats_booked = sum(e.get("total_seats", 0) - e.get("available_seats", 0) for e in events)
    
    # Get registrations for admin's events
    event_ids = [e["_id"] for e in events]
    registrations = await db["registrations"].find({"event_id": {"$in": event_ids}}).to_list(None)
    total_registrations = len(registrations)
    
    return {
        "total_events": total_events,
        "total_registrations": total_registrations,
        "total_seats_available": total_seats_available,
        "total_seats_booked": total_seats_booked,
        "events": [
            {
                "id": str(e["_id"]),
                "title": e["title"],
                "date": e["date"],
                "available_seats": e["available_seats"],
                "total_seats": e["total_seats"]
            }
            for e in events
        ]
    }

@router.get("/users")
async def get_all_users(request: Request):
    """Get all users (admin only)"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this"
        )
    
    users = await db["users"].find().to_list(None)
    
    return [
        {
            "id": str(u["_id"]),
            "name": u["name"],
            "email": u["email"],
            "is_admin": u.get("is_admin", False),
            "created_at": u["created_at"]
        }
        for u in users
    ]

@router.get("/events/{event_id}/stats")
async def get_event_statistics(event_id: str, request: Request):
    """Get statistics for a specific event (admin only)"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this"
        )
    
    try:
        event_oid = ObjectId(event_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID"
        )
    
    event = await db["events"].find_one({"_id": event_oid})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    registrations = await db["registrations"].find({"event_id": event_oid}).to_list(None)
    
    attendees = []
    for reg in registrations:
        user = await db["users"].find_one({"_id": reg["user_id"]})
        attendees.append({
            "name": user.get("name") if user else "Unknown",
            "email": user.get("email") if user else "Unknown",
            "ticket_number": reg["ticket_number"],
            "registration_date": reg["registration_date"]
        })
    
    return {
        "event_title": event["title"],
        "event_date": event["date"],
        "event_time": event["time"],
        "event_venue": event["venue"],
        "total_seats": event["total_seats"],
        "available_seats": event["available_seats"],
        "booked_seats": event["total_seats"] - event["available_seats"],
        "total_registrations": len(registrations),
        "attendees": attendees
    }

@router.get("/registrations", response_model=list)
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

@router.get("/registrations/event/{event_id}", response_model=list)
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
            "ticket_qr_path": reg["ticket_qr_path"],
            "registration_date": reg["registration_date"]
        })
    
    return result
