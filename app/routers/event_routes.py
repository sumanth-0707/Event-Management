from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
from bson.objectid import ObjectId
from app.database import get_database
from app.schemas.event_schema import EventCreateSchema, EventUpdateSchema, EventResponseSchema
from app.utils.auth import decode_token
from app.models.event import Event
from app.utils.email import send_event_created_email
from datetime import datetime

router = APIRouter(prefix="/api/events", tags=["events"])

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

@router.get("/", response_model=list)
async def get_all_events():
    """Get all events"""
    db = get_database()
    events = await db["events"].find().to_list(None)
    
    return [
        {
            "id": str(event["_id"]),
            "title": event["title"],
            "description": event["description"],
            "date": event["date"],
            "time": event["time"],
            "venue": event["venue"],
            "total_seats": event["total_seats"],
            "available_seats": event["available_seats"],
            "created_by": str(event.get("created_by", "Unknown")),
            "created_at": event.get("created_at", datetime.min)
        }
        for event in events
    ]

@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str):
    """Get a specific event by ID - API endpoint"""
    db = get_database()
    
    try:
        event = await db["events"].find_one({"_id": ObjectId(event_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID"
        )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return {
        "id": str(event["_id"]),
        "title": event["title"],
        "description": event["description"],
        "date": event["date"],
        "time": event["time"],
        "venue": event["venue"],
        "total_seats": event["total_seats"],
        "available_seats": event["available_seats"],
        "created_by": str(event.get("created_by", "Unknown")),
        "created_at": event.get("created_at", datetime.min)
    }

@router.post("/", response_model=dict)
async def create_event(event_data: EventCreateSchema, request: Request, background_tasks: BackgroundTasks):
    """Create a new event (admin only)"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create events"
        )
    
    event_dict = {
        "title": event_data.title,
        "description": event_data.description,
        "date": event_data.date,
        "time": event_data.time,
        "venue": event_data.venue,
        "total_seats": event_data.total_seats,
        "available_seats": event_data.total_seats,
        "created_by": ObjectId(current_user["user_id"]),
        "created_at": datetime.utcnow()
    }
    
    result = await db["events"].insert_one(event_dict)

    background_tasks.add_task(
        send_event_created_email,
        admin_email=current_user["email"],
        event_title=event_data.title,
        event_date=event_data.date,
        event_description=event_data.description,
        event_venue=event_data.venue
    )
    
    return {
        "message": "Event created successfully",
        "event_id": str(result.inserted_id)
    }

@router.put("/{event_id}", response_model=dict)
async def update_event(event_id: str, event_data: EventUpdateSchema, request: Request):
    """Update an event (admin only)"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update events"
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
    
    # Prepare update data
    update_data = {}
    if event_data.title is not None:
        update_data["title"] = event_data.title
    if event_data.description is not None:
        update_data["description"] = event_data.description
    if event_data.date is not None:
        update_data["date"] = event_data.date
    if event_data.time is not None:
        update_data["time"] = event_data.time
    if event_data.venue is not None:
        update_data["venue"] = event_data.venue
    if event_data.total_seats is not None:
        update_data["total_seats"] = event_data.total_seats
    if event_data.available_seats is not None:
        update_data["available_seats"] = event_data.available_seats
    
    await db["events"].update_one({"_id": event_oid}, {"$set": update_data})
    
    return {"message": "Event updated successfully"}

@router.delete("/{event_id}", response_model=dict)
async def delete_event(event_id: str, request: Request):
    """Delete an event (admin only)"""
    db = get_database()
    current_user = await get_current_user_from_request(request)
    
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete events"
        )
    
    try:
        event_oid = ObjectId(event_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID"
        )
    
    result = await db["events"].delete_one({"_id": event_oid})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return {"message": "Event deleted successfully"}
