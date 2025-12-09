# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
```

Update these in `.env`:
- `MONGODB_URL` - Your MongoDB connection string
- `SECRET_KEY` - Change to a random secret key
- `EMAIL_FROM` & `EMAIL_PASSWORD` - For email notifications

### 3. Start MongoDB
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas (update MONGODB_URL in .env)
```

### 4. Run Application
```bash
python -m uvicorn app.main:app --reload
```

### 5. Access Application
- **Frontend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## First Time Setup

### Create Admin User

In MongoDB, run these commands:

```javascript
// Connect to MongoDB
use event_management

// Create admin user
db.users.insertOne({
  name: "Admin User",
  email: "admin@test.com",
  password_hash: "$2b$12$oI7FPRzRNqbqGzxJ6pA8h.8OxDKRWs6nGh5hL6I7qh7C6I5qH5L8C",
  is_admin: true,
  created_at: new Date()
})

// The above password_hash is bcrypt hash of "admin123"
// For your own password, use: python -c "from app.utils.auth import hash_password; print(hash_password('your_password'))"
```

### Test the Application

1. **Login as Admin**
   - Go to http://localhost:8000/login
   - Email: `admin@test.com`
   - Password: `admin123`

2. **Create an Event**
   - Click Admin Dashboard
   - Fill in event details
   - Click "Create Event"

3. **Register as User**
   - Logout (click Logout in navbar)
   - Click Register
   - Create a new account

4. **Register for Event**
   - Login with your user account
   - Go to Events
   - Click View Details on an event
   - Click Register Now
   - Check your email for the QR code ticket

## Project Files Overview

### Core Files
- `app/main.py` - FastAPI application and route definitions
- `app/config.py` - Configuration and environment variables
- `app/database.py` - MongoDB connection and setup

### API Routes
- `app/routers/auth_routes.py` - User registration and login
- `app/routers/event_routes.py` - Event management (CRUD)
- `app/routers/registration_routes.py` - Event registrations
- `app/routers/admin_routes.py` - Admin dashboard data

### Utilities
- `app/utils/auth.py` - JWT and password utilities
- `app/utils/email.py` - Email sending service
- `app/utils/qrcode_gen.py` - QR code generation

### Frontend
- `app/templates/` - HTML templates (Jinja2)
- `app/static/css/style.css` - Styling
- `app/static/js/auth.js` - Client-side utilities

## API Examples

### Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Get All Events
```bash
curl -X GET "http://localhost:8000/events/"
```

### Create Event (Admin)
```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -b "access_token=YOUR_TOKEN" \
  -d '{
    "title": "Python Conference",
    "description": "Annual Python conference",
    "date": "2024-06-15",
    "time": "09:00",
    "venue": "Convention Center",
    "total_seats": 500
  }'
```

### Register for Event
```bash
curl -X POST "http://localhost:8000/registrations/{event_id}" \
  -b "access_token=YOUR_TOKEN"
```

## Folder Structure After Setup

```
event-management/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── email.py
│   │   └── qrcode_gen.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── event.py
│   │   └── registration.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── event_schema.py
│   │   └── registration_schema.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── event_routes.py
│   │   ├── registration_routes.py
│   │   └── admin_routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── events.html
│   │   ├── event_detail.html
│   │   ├── dashboard.html
│   │   └── admin_dashboard.html
│   └── static/
│       ├── css/style.css
│       ├── js/auth.js
│       ├── images/
│       └── qrcodes/
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

## Common Issues & Solutions

### Issue: "Cannot connect to MongoDB"
**Solution:**
- Ensure MongoDB is running: `mongod`
- Check MONGODB_URL in .env
- For Atlas: whitelist your IP and use correct connection string

### Issue: "Email not sending"
**Solution:**
- Verify SMTP credentials in .env
- Use App-specific password for Gmail (not regular password)
- Check firewall/security settings

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Use a different port
python -m uvicorn app.main:app --reload --port 8001
```

### Issue: "ModuleNotFoundError"
**Solution:**
- Activate virtual environment
- Run `pip install -r requirements.txt` again
- Ensure you're in the correct directory

## Next Steps

1. **Customize Configuration:** Edit `app/config.py` for your needs
2. **Add More Features:** Extend routers with new endpoints
3. **Improve UI:** Customize templates and CSS
4. **Deploy:** Follow deployment section in README.md
5. **Monitor:** Add logging and error tracking

## Getting Help

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **MongoDB Docs:** https://docs.mongodb.com
- **Uvicorn Docs:** https://www.uvicorn.org
- **Project README:** See README.md

## Production Deployment

For production, update `.env`:
```env
DEBUG=False
SECRET_KEY=<generate-secure-random-key>
MONGODB_URL=<production-mongodb-url>
```

Use production ASGI server:
```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

Happy event managing! 🎉
