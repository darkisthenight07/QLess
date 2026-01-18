# app.py - Main Application Entry Point

import streamlit as st
from config import APP_CONFIG, ROLES
from auth.authentication import auth_manager
from views.login_view import show_login_page, show_logout_button
from views.student_view import show_student_view
from views.admin_view import show_admin_view
from utils.firebase_config import initialize_firebase

# Page configuration
st.set_page_config(
    page_title=f"{APP_CONFIG['app_name']} - Smart Campus Queue Manager",
    page_icon=APP_CONFIG['page_icon'],
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size: 50px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
    }
    div[data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Firebase
try:
    initialize_firebase()
except Exception as e:
    st.error(f"❌ Firebase initialization failed: {e}")
    st.info("Please check your Firebase configuration in config.py and ensure serviceAccountKey.json is present.")
    st.stop()

def main():
    """Main application logic"""
    
    # Check authentication
    if not auth_manager.is_authenticated():
        show_login_page()
        return
    
    # Get current user
    user = auth_manager.get_current_user()
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/4CAF50/FFFFFF?text=QLess", width='stretch')
        st.title(APP_CONFIG['app_name'])
        st.markdown(f"**Version** {APP_CONFIG['app_version']}")
        st.markdown("---")
    
    # Show logout button
    show_logout_button()
    
    # Route based on role
    user_role = user.get('role', ROLES['STUDENT'])
    
    # View selector for admins
    if user_role in [ROLES['ADMIN'], ROLES['SUPER_ADMIN']]:
        with st.sidebar:
            st.markdown("### 🎯 View Mode")
            view_mode = st.radio(
                "Select Interface",
                ["Student View", "Admin Dashboard"],
                key="view_mode"
            )
        
        if view_mode == "Admin Dashboard":
            show_admin_view()
        else:
            show_student_view()
    else:
        # Students only see student view
        show_student_view()
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; color: gray; padding: 20px;">
            <p>{APP_CONFIG['app_name']} - Smart Campus Queue Manager</p>
            <p style="font-size: 12px;">Built for HackSync 2024 | Made with ❤️ using Python, Streamlit & Firebase</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()