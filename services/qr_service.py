# services/qr_service.py - QR Code Generation and Validation

import qrcode
from io import BytesIO
import base64
from datetime import datetime
import hashlib

class QRService:
    """Service for QR code generation and validation"""
    
    def generate_facility_qr(self, facility_id, facility_name):
        """Generate QR code for a facility"""
        # Create QR data with facility info
        app_url = "http://192.168.91.54:8501"
        qr_data = f"{app_url}/?facility={facility_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str, qr_data
    
    def validate_qr_data(self, qr_data):
        """Validate and extract facility_id from QR data"""
        if not qr_data or not qr_data.startswith("QLESS_CHECKIN:"):
            return False, None, "Invalid QR code"
        
        try:
            facility_id = qr_data.split("QLESS_CHECKIN:")[1]
            return True, facility_id, "Valid QR code"
        except:
            return False, None, "Invalid QR code format"

# Initialize service
qr_service = QRService()