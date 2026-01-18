# config.py - Application Configuration
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Firebase Configuration
FIREBASE_CONFIG = {
    'credentials_path': os.path.join(BASE_DIR, 'serviceAccountKey.json'),
    'database_url': 'https://qless-f288a-default-rtdb.firebaseio.com/'  # Replace with your URL
}

# Application Settings
APP_CONFIG = {
    'app_name': 'QLess',
    'app_version': '1.0.0',
    'page_icon': '🎓',
    'auto_refresh_interval': 5000  # milliseconds
}

# User Roles
ROLES = {
    'STUDENT': 'student',
    'ADMIN': 'admin',
    'SUPER_ADMIN': 'super_admin'
}

# Admin Emails (Super Admins)
SUPER_ADMIN_EMAILS = [
    'admin@iiti.ac.in',
    'your.email@campus.edu'  # Add your email
]

# Queue Status Thresholds
QUEUE_THRESHOLDS = {
    'low': 0.4,      # < 40% capacity
    'moderate': 0.7,  # 40-70% capacity
    'high': 1.0       # > 70% capacity
}

# Default Facility Settings
DEFAULT_FACILITY_CONFIG = {
    'capacity': 100,
    'avg_time_per_person': 3,  # minutes
    'icon': '🏢',
    'open_hours': {
        'start': 8,  # 8 AM
        'end': 22    # 10 PM
    }
}

# UI Theme
THEME = {
    'primary_color': '#4CAF50',
    'secondary_color': '#2196F3',
    'warning_color': '#FFC107',
    'danger_color': '#F44336',
    'success_color': '#28a745'
}

# Session Timeout (minutes)
SESSION_TIMEOUT = 30

# Feature Flags
FEATURES = {
    'notifications': False,
    'predictions': False,
}