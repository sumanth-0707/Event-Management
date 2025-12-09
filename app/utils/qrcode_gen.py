import qrcode
from io import BytesIO
from pathlib import Path
from typing import Optional
from app.config import settings

def generate_qr_code(data: str, filename: str) -> str:
    """
    Generate a QR code and save it as PNG
    
    Args:
        data: The data to encode in QR code
        filename: The filename to save as (without extension)
    
    Returns:
        The relative path to the saved QR code
    """
    # Ensure QR code directory exists
    qr_dir = Path(settings.QR_CODE_DIR)
    qr_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    file_path = qr_dir / f"{filename}.png"
    img.save(str(file_path))
    
    # Return relative path for web access
    return f"/static/qrcodes/{filename}.png"

def get_qr_code_data(registration_id: str, user_email: str, event_id: str) -> str:
    """
    Generate the data string for QR code encoding
    
    Args:
        registration_id: The registration ID
        user_email: The user's email
        event_id: The event ID
    
    Returns:
        The formatted string for QR encoding
    """
    return f"TICKET|{registration_id}|{user_email}|{event_id}"
