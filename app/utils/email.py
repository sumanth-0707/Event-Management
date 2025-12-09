import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from app.config import settings

async def send_registration_email(recipient_email: str, username: str, ticket_number: str, qr_code_path: str):
    """
    Send registration confirmation email with ticket QR code link
    
    Args:
        recipient_email: Recipient's email address
        username: User's name
        ticket_number: Registration ticket number
        qr_code_path: URL path to QR code image
    """
    try:
        # Create email message
        message = MIMEMultipart("related")
        message["Subject"] = "Event Registration Confirmation"
        message["From"] = settings.EMAIL_FROM
        message["To"] = recipient_email
        
        # HTML content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Welcome to Event Management System!</h2>
                <p>Hi {username},</p>
                <p>Thank you for registering for the event. Your registration is confirmed.</p>
                <p><strong>Ticket Number:</strong> {ticket_number}</p>
                <div style="margin-top: 20px;">
                    <p><strong>Your Event Ticket (QR Code):</strong></p>
                    <img src="cid:qrcode" alt="Event Ticket QR Code" style="max-width: 200px;">
                </div>
                <p>Please present this QR code at the event venue.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">This is an automated email, please do not reply.</p>
            </body>
        </html>
        """
        
        # Attach HTML content
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        # Attach QR code image
        if qr_code_path:
            try:
                with open(qr_code_path, "rb") as f:
                    img_data = f.read()
                image = MIMEImage(img_data, name="qrcode.png")
                image.add_header("Content-ID", "<qrcode>")
                image.add_header("Content-Disposition", "inline", filename="qrcode.png")
                message.attach(image)
            except FileNotFoundError:
                import logging
                logging.warning(f"QR code image not found at {qr_code_path}")


        # Send email
        async with aiosmtplib.SMTP(hostname=settings.SMTP_SERVER, port=settings.SMTP_PORT) as smtp:
            await smtp.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
            await smtp.send_message(message)
        
        import logging
        logging.info(f"Registration confirmation email sent to {recipient_email}")
        return True
    
    except Exception as e:
        # Email sending is optional - registration succeeds even if email fails
        import logging
        logging.warning(f"Could not send confirmation email (this is non-critical)")
        return False

async def send_event_created_email(admin_email: str, event_title: str, event_date: str, event_description: str, event_venue: str):
    """
    Send confirmation email when admin creates an event
    
    Args:
        admin_email: Admin's email address
        event_title: Title of the created event
        event_date: Date of the event
        event_description: Description of the event
        event_venue: Venue of the event
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Event Created Successfully"
        message["From"] = settings.EMAIL_FROM
        message["To"] = admin_email
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Event Created Successfully!</h2>
                <p>Your event has been created successfully.</p>
                <p><strong>Event Title:</strong> {event_title}</p>
                <p><strong>Event Date:</strong> {event_date}</p>
                <p><strong>Venue:</strong> {event_venue}</p>
                <p><strong>Description:</strong></p>
                <p>{event_description}</p>
                <p>Users can now register for your event.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">This is an automated email, please do not reply.</p>
            </body>
        </html>
        """
        
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        async with aiosmtplib.SMTP(hostname=settings.SMTP_SERVER, port=settings.SMTP_PORT) as smtp:
            await smtp.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
            await smtp.send_message(message)
        
        import logging
        logging.info(f"Event notification sent to {admin_email}")
        return True
    
    except Exception as e:
        # Email sending is optional - event creation succeeds even if email fails
        import logging
        logging.warning(f"Could not send event notification email (this is non-critical)")
        return False
