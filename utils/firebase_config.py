# utils/firebase_config.py - Firebase Initialization
import firebase_admin
from firebase_admin import credentials, db
from config import FIREBASE_CONFIG
import os

_firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase connection"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            cred_path = FIREBASE_CONFIG['credentials_path']
            
            if not os.path.exists(cred_path):
                raise FileNotFoundError(
                    f"Firebase credentials not found at {cred_path}. "
                    "Please download serviceAccountKey.json from Firebase Console."
                )
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_CONFIG['database_url']
            })
            
            _firebase_initialized = True
            print("✅ Firebase initialized successfully")
    
    except Exception as e:
        print(f"❌ Firebase initialization error: {e}")
        raise

def get_db_reference(path):
    """Get Firebase database reference"""
    initialize_firebase()
    return db.reference(path)

def get_db():
    """Get Firebase database instance"""
    initialize_firebase()
    return db