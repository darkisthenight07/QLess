# utils/qr_scanner.py - QR Code Scanner Utility (Alternative Implementation)

import cv2
import numpy as np
from PIL import Image

def decode_qr_from_camera(camera_image):
    """
    Decode QR code from camera input using OpenCV's QRCodeDetector
    This works without pyzbar/libzbar dependencies
    """
    try:
        # Convert to PIL Image
        image = Image.open(camera_image)
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Initialize QR Code detector
        qr_detector = cv2.QRCodeDetector()
        
        # Detect and decode
        qr_data, bbox, straight_qrcode = qr_detector.detectAndDecode(img_array)
        
        if qr_data:
            return True, qr_data, "QR code scanned successfully"
        else:
            return False, None, "No QR code detected"
    
    except Exception as e:
        return False, None, f"Error scanning QR: {str(e)}"