# Event Management System

A complete event management platform built with **FastAPI**, **MongoDB**, and modern web technologies.

## Quick Features

✓ User registration & JWT authentication  
✓ Browse and book event tickets  
✓ Instant QR code ticket generation  
✓ User dashboard with bookings  
✓ Admin dashboard to manage events & registrations  
✓ Download/print QR code tickets  
✓ Responsive design (desktop, tablet, mobile)  
✓ Production-ready code

## Project Structure

```
event-management/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app setup
│   ├── config.py               # Configuration and settings
│   ├── database.py             # MongoDB connection and indexes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT utilities
│   │   ├── email.py            # Email sending
│   │   └── qrcode_gen.py       # QR code generation
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
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── auth.js
│       ├── images/
│       └── qrcodes/             # Generated QR codes
├── requirements.txt
├── .env.example
└── README.md
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **PyJWT** - JWT token handling
- **Passlib + bcrypt** - Password hashing and verification
- **python-multipart** - Form data handling
- **email-validator** - Email validation
- **qrcode + Pillow** - QR code generation
- **aiosmtplib** - Async email sending
- **python-dotenv** - Environment configuration

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Responsive styling
- **JavaScript (ES6+)** - Client-side interactivity
- **Jinja2** - Server-side templating

### Database
- **MongoDB** - NoSQL document database

## Installation

### Prerequisites
- Python 3.8+
- MongoDB 4.0+
- pip package manager

### Setup Steps

1. **Clone the repository**
```bash
cd event-management
```

2. **Create a virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
```

5. **Configure MongoDB**
- Install MongoDB locally or use MongoDB Atlas cloud service
- Update `MONGODB_URL` in `.env`

6. **Configure Email Service**
- For Gmail: Generate an App Password (not your regular password)
- Update `EMAIL_FROM` and `EMAIL_PASSWORD` in `.env`

7. **Run the application**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user

### Events
- `GET /events/` - Get all events
- `GET /events/{event_id}` - Get event details
- `POST /events/` - Create event (admin only)
- `PUT /events/{event_id}` - Update event (admin only)
- `DELETE /events/{event_id}` - Delete event (admin only)

### Registrations
- `POST /registrations/{event_id}` - Register for event
- `GET /registrations/my-registrations` - Get user's registrations
- `GET /registrations/admin/registrations` - Get all registrations (admin only)
- `GET /registrations/admin/registrations/event/{event_id}` - Get event registrations (admin only)

### Admin
- `GET /admin/dashboard-data` - Get dashboard statistics
- `GET /admin/users` - Get all users (admin only)
- `GET /admin/events/{event_id}/stats` - Get event statistics (admin only)

## Frontend Routes

- `/` - Home page
- `/login` - Login page
- `/register` - Registration page
- `/events` - Events listing
- `/events/{id}` - Event details
- `/dashboard` - User's bookings dashboard
- `/admin/dashboard` - Admin dashboard

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  name: string,
  email: string,
  password_hash: string,
  is_admin: boolean,
  created_at: datetime
}
```

### Events Collection
```javascript
{
  _id: ObjectId,
  title: string,
  description: string,
  date: string,
  time: string,
  venue: string,
  total_seats: number,
  available_seats: number,
  created_by: ObjectId,
  created_at: datetime
}
```

### Registrations Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  event_id: ObjectId,
  ticket_qr_path: string,
  ticket_number: string,
  registration_date: datetime
}
```

## Configuration

### Environment Variables

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=event_management

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# App
DEBUG=True
```

## Usage

### Register as a User
1. Click "Register" on the login page
2. Fill in your details (name, email, password)
3. Click "Register" button
4. You'll be redirected to login page
5. Login with your credentials

### Register for an Event
1. Login to your account
2. Go to "Events" page
3. Browse available events
4. Click "View Details" on an event
5. Click "Register Now" button
6. You'll receive a confirmation email with QR code ticket
7. Your ticket appears on your dashboard

### Admin Functions
1. Login as admin (admin account needs to be created in database)
2. Go to "Admin Dashboard"
3. Create new events
4. View all registrations
5. Monitor seat availability
6. View attendee lists

## Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ HTTP-only cookies for token storage
- ✅ Role-based access control (user/admin)
- ✅ Email validation
- ✅ CORS protection (can be configured)
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (using MongoDB)

## Error Handling

The application includes comprehensive error handling:
- Validation errors with detailed messages
- Authentication errors
- Authorization errors
- Resource not found errors
- Database connection errors
- Email sending errors (gracefully handled)

## Performance Considerations

- Async/await for non-blocking operations
- MongoDB indexes on frequently queried fields
- Connection pooling with Motor
- Efficient QR code generation
- Static file caching

## Deployment

### Production Checklist
- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Set `DEBUG=False`
- [ ] Use a production WSGI server (Gunicorn, etc.)
- [ ] Configure CORS properly
- [ ] Use HTTPS/SSL
- [ ] Set up proper email service
- [ ] Use MongoDB Atlas or managed MongoDB service
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Regular database backups

### Example Production Run
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing

To test the application:

1. **Create admin user** (in MongoDB):
```javascript
db.users.insertOne({
  name: "Admin User",
  email: "admin@example.com",
  password_hash: "<hashed_password>",
  is_admin: true,
  created_at: new Date()
})
```

2. **Create test events** via admin dashboard

3. **Register for events** via user account

4. **Check registrations** via admin dashboard

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running
- Check `MONGODB_URL` in `.env`
- Verify network connectivity

### Email Not Sending
- Check SMTP credentials in `.env`
- Enable "Less secure apps" for Gmail (if using Gmail)
- Use App-specific passwords for Gmail
- Check `EMAIL_FROM` and `EMAIL_PASSWORD`

### QR Code Not Generating
- Ensure `pillow` is installed
- Check write permissions in `static/qrcodes/` directory
- Verify disk space availability

### JWT Token Invalid
- Check `SECRET_KEY` hasn't changed
- Verify token expiration time
- Clear browser cookies and re-login

## Future Enhancements

- [ ] Event categories and filtering
- [ ] Search functionality
- [ ] Event images/media
- [ ] Batch email sending
- [ ] Event cancellation/rescheduling
- [ ] Ticket validation scanning
- [ ] Payment integration
- [ ] SMS notifications
- [ ] Calendar integration
- [ ] Analytics dashboard
- [ ] Mobile app
- [ ] API rate limiting
- [ ] WebSocket for real-time updates

## Contributing

Contributions are welcome! Please ensure code follows best practices and includes appropriate documentation.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

---

Built with ❤️ using FastAPI and MongoDB
