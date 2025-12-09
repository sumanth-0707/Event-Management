from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse
from bson.objectid import ObjectId
from datetime import timedelta
from app.database import get_database
from app.schemas.user_schema import UserRegisterSchema, UserLoginSchema, UserResponseSchema
from app.utils.auth import hash_password, verify_password, create_access_token, decode_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=dict)
async def register(user_data: UserRegisterSchema):
    """Register a new user"""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db["users"].find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    from datetime import datetime
    user_dict = {
        "name": user_data.name,
        "email": user_data.email,
        "password_hash": hashed_password,
        "is_admin": False,
        "created_at": datetime.utcnow()
    }
    
    result = await db["users"].insert_one(user_dict)
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }

@router.post("/login")
async def login(user_data: UserLoginSchema, response: Response):
    """Login user and set access token in cookie"""
    db = get_database()
    
    # Find user by email
    user = await db["users"].find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"], "is_admin": user.get("is_admin", False)},
        expires_delta=timedelta(hours=24)
    )
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=86400,  # 24 hours
        samesite="lax"
    )
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "user_id": str(user["_id"]),
        "is_admin": user.get("is_admin", False)
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

# Dependency function to get current user from cookie
async def get_current_user_from_cookie(request):
    """Extract and validate user from cookie"""
    from fastapi import Request
    
    # This is a helper - will be properly implemented in main.py
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
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {"user_id": user_id, "email": payload.get("email"), "is_admin": payload.get("is_admin", False)}

@router.get("/me", response_model=UserResponseSchema)
async def get_current_user(request: dict = Depends(get_current_user_from_cookie)):
    """Get current logged-in user info"""
    db = get_database()
    user = await db["users"].find_one({"_id": ObjectId(request["user_id"])})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "is_admin": user.get("is_admin", False),
        "created_at": user["created_at"]
    }


# Export the dependency
__all__ = ["router", "get_current_user_from_cookie"]
