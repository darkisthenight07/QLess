# utils/qr_scanner.py - QR Code Scanner Utility

import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image

def decode_qr_from_camera(camera_image):
    """Decode QR code from camera input"""
    try:
        # Convert to PIL Image
        image = Image.open(camera_image)
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Decode QR codes
        decoded_objects = decode(img_array)
        
        if not decoded_objects:
            return False, None, "No QR code detected"
        
        # Get first QR code data
        qr_data = decoded_objects[0].data.decode('utf-8')
        
        return True, qr_data, "QR code scanned successfully"
    
    except Exception as e:
        return False, None, f"Error scanning QR: {str(e)}"