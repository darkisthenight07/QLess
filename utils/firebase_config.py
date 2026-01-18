import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import json
import os

_firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase connection"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    try:
        if not firebase_admin._apps:
            # Check if running on Streamlit Cloud
            if hasattr(st, 'secrets') and 'firebase' in st.secrets:
                # Use Streamlit secrets
                firebase_config = dict(st.secrets['firebase'])
                cred = credentials.Certificate(firebase_config)
                database_url = st.secrets['firebase']['database_url']
            else:
                # Local development
                cred_path = 'serviceAccountKey.json'
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(
                        f"Firebase credentials not found. "
                        "Add serviceAccountKey.json or configure Streamlit secrets."
                    )
                cred = credentials.Certificate(cred_path)
                from config import FIREBASE_CONFIG
                database_url = FIREBASE_CONFIG['database_url']
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
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