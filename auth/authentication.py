# auth/authentication.py - Authentication System

import streamlit as st
from datetime import datetime, timedelta
import hashlib
from utils.firebase_config import get_db_reference
from config import ROLES, SUPER_ADMIN_EMAILS, SESSION_TIMEOUT

class AuthManager:
    """Manages user authentication and authorization"""
    
    def __init__(self):
        self.users_ref = get_db_reference('users')
        self.sessions_ref = get_db_reference('sessions')
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password, name, role=ROLES['STUDENT']):
        """Register a new user"""
        try:
            # Check if user exists
            uid = email.split('@')[0].replace('.', '_')
            user_ref = self.users_ref.child(uid)
            
            if user_ref.get():
                return False, "User already exists"
            
            # Create user
            user_data = {
                'email': email,
                'name': name,
                'password': self.hash_password(password),
                'role': role,
                'created_at': datetime.now().isoformat(),
                'points': 0,
                'badges': [],
                'active': True
            }
            
            user_ref.set(user_data)
            return True, "Registration successful"
        
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login(self, email, password):
        """Authenticate user"""
        try:
            uid = email.split('@')[0].replace('.', '_')
            user_ref = self.users_ref.child(uid)
            user_data = user_ref.get()
            
            if not user_data:
                return False, None, "User not found"
            
            # Check if account is active
            if not user_data.get('active', True):
                return False, None, "Account is disabled"
            
            # Verify password
            if user_data.get('password') != self.hash_password(password):
                return False, None, "Invalid password"
            
            # Determine role
            role = user_data.get('role', ROLES['STUDENT'])
            
            # Super admin override
            if email in SUPER_ADMIN_EMAILS:
                role = ROLES['SUPER_ADMIN']
                user_ref.update({'role': role})
            
            # Update last login
            user_ref.update({'last_login': datetime.now().isoformat()})
            
            # Create session
            session_data = {
                'uid': uid,
                'email': email,
                'name': user_data.get('name', 'User'),
                'role': role,
                'login_time': datetime.now().isoformat()
            }
            
            return True, session_data, "Login successful"
        
        except Exception as e:
            return False, None, f"Login failed: {str(e)}"
    
    def logout(self):
        """Logout current user"""
        if 'user' in st.session_state:
            st.session_state.user = None
        if 'authenticated' in st.session_state:
            st.session_state.authenticated = False
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        if 'user' not in st.session_state or st.session_state.user is None:
            return False
        
        # Check session timeout
        if 'login_time' in st.session_state.user:
            login_time = datetime.fromisoformat(st.session_state.user['login_time'])
            if datetime.now() - login_time > timedelta(minutes=SESSION_TIMEOUT):
                self.logout()
                return False
        
        return True
    
    def get_current_user(self):
        """Get current logged in user"""
        if self.is_authenticated():
            return st.session_state.user
        return None
    
    def has_role(self, required_role):
        """Check if user has required role"""
        user = self.get_current_user()
        if not user:
            return False
        
        user_role = user.get('role', ROLES['STUDENT'])
        
        # Role hierarchy: SUPER_ADMIN > ADMIN > STUDENT
        role_hierarchy = {
            ROLES['SUPER_ADMIN']: 3,
            ROLES['ADMIN']: 2,
            ROLES['STUDENT']: 1
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.has_role(ROLES['ADMIN'])
    
    def is_super_admin(self):
        """Check if current user is super admin"""
        user = self.get_current_user()
        if not user:
            return False
        return user.get('role') == ROLES['SUPER_ADMIN']
    
    def require_auth(self, required_role=ROLES['STUDENT']):
        """Decorator-like function to require authentication"""
        if not self.is_authenticated():
            st.warning("⚠️ Please log in to continue")
            st.stop()
        
        if not self.has_role(required_role):
            st.error("❌ You don't have permission to access this page")
            st.stop()
    
    def get_all_users(self):
        """Get all users (admin only)"""
        users = self.users_ref.get()
        if not users:
            return []
        
        user_list = []
        for uid, data in users.items():
            user_list.append({
                'uid': uid,
                'email': data.get('email'),
                'name': data.get('name'),
                'role': data.get('role'),
                'active': data.get('active', True),
                'points': data.get('points', 0),
                'created_at': data.get('created_at')
            })
        
        return user_list
    
    def update_user_role(self, uid, new_role):
        """Update user role (super admin only)"""
        try:
            user_ref = self.users_ref.child(uid)
            user_ref.update({'role': new_role})
            return True, "Role updated successfully"
        except Exception as e:
            return False, f"Failed to update role: {str(e)}"
    
    def toggle_user_status(self, uid):
        """Activate/deactivate user (admin only)"""
        try:
            user_ref = self.users_ref.child(uid)
            user_data = user_ref.get()
            
            if not user_data:
                return False, "User not found"
            
            current_status = user_data.get('active', True)
            user_ref.update({'active': not current_status})
            
            status = "activated" if not current_status else "deactivated"
            return True, f"User {status} successfully"
        
        except Exception as e:
            return False, f"Failed to update status: {str(e)}"

# Initialize auth manager
auth_manager = AuthManager()