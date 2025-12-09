from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from pathlib import Path
import os

from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth_routes, event_routes, registration_routes, admin_routes, admin_creation_routes
from app.utils.auth import decode_token

# Get the base directory
BASE_DIR = Path(__file__).parent.parent

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Create FastAPI app
app = FastAPI(
    title="Event Management System",
    description="A complete event management system with FastAPI and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent / "static")),
    name="static"
)

# Helper function to get user from request
async def get_user_from_request(request: Request):
    """Extract user from request cookies if available"""
    token = request.cookies.get("access_token")
    if token:
        payload = decode_token(token)
        if payload:
            from app.database import get_database
            from bson.objectid import ObjectId
            db = get_database()
            user = await db["users"].find_one({"_id": ObjectId(payload.get("sub"))})
            if user:
                return {
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"],
                    "is_admin": user.get("is_admin", False)
                }
    return None

# Frontend Routes (MUST be before API routers to take precedence)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page"""
    user = await get_user_from_request(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    user = await get_user_from_request(request)
    if user:
        return RedirectResponse(url="/events", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "user": user})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Register page"""
    user = await get_user_from_request(request)
    if user:
        return RedirectResponse(url="/events", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, "user": user})

@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    """Events listing page"""
    user = await get_user_from_request(request)
    return templates.TemplateResponse("events.html", {"request": request, "user": user})

@app.get("/events/{event_id}", response_class=HTMLResponse)
async def event_detail_page(event_id: str, request: Request):
    """Event detail page"""
    user = await get_user_from_request(request)
    return templates.TemplateResponse("event_detail.html", {
        "request": request,
        "user": user,
        "event_id": event_id
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """User dashboard page"""
    user = await get_user_from_request(request)
    # Allow rendering dashboard page even if not logged in, will show registrations or redirect on load
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    """Admin dashboard page"""
    user = await get_user_from_request(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": user})

@app.get("/create-admin", response_class=HTMLResponse)
async def create_admin_page(request: Request):
    """Admin creation page - protected with master password"""
    return templates.TemplateResponse("create_admin.html", {"request": request})

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Include API routers (AFTER frontend routes so they don't override)
app.include_router(auth_routes.router)
app.include_router(event_routes.router)
app.include_router(registration_routes.router)
app.include_router(admin_routes.router)
app.include_router(admin_creation_routes.router)

# API Documentation
@app.get("/api/docs", response_class=HTMLResponse)
async def api_docs(request: Request):
    """API documentation"""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
