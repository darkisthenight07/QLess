# views/login_view.py - Login and Registration Interface

import streamlit as st
from auth.authentication import auth_manager
from config import APP_CONFIG

def show_login_page():
    """Display login/registration page"""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and title
        st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 60px; margin: 0;">🎓</h1>
            <h1 style="margin: 10px 0;">{APP_CONFIG['app_name']}</h1>
            <p style="color: gray; font-size: 18px;">Smart Campus Queue Manager</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tab selection
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            show_login_form()
        
        with tab2:
            show_registration_form()

def show_login_form():
    """Display login form"""
    st.markdown("### Welcome Back!")
    
    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="your.email@campus.edu",
            help="Use your campus email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("🔓 Login", width='stretch', type="primary")
        
        with col2:
            forgot = st.form_submit_button("🔑 Forgot Password?", width='stretch')
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Authenticating..."):
                    success, user_data, message = auth_manager.login(email, password)
                    
                    if success:
                        st.session_state.user = user_data
                        st.session_state.authenticated = True
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        if forgot:
            st.info("Please contact admin to reset your password")

def show_registration_form():
    """Display registration form"""
    st.markdown("### Create Account")
    
    with st.form("registration_form"):
        name = st.text_input(
            "Full Name",
            placeholder="John Doe"
        )
        
        email = st.text_input(
            "Campus Email",
            placeholder="john.doe@campus.edu",
            help="Use your official campus email"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 6 characters"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter password"
            )
        
        # Terms and conditions
        terms = st.checkbox("I agree to the Terms and Conditions")
        
        submit = st.form_submit_button("📝 Create Account", width='stretch', type="primary")
        
        if submit:
            # Validation
            if not all([name, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif not email.endswith('@campus.edu'):
                st.warning("Please use your campus email (@campus.edu)")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            elif password != confirm_password:
                st.error("Passwords don't match")
            elif not terms:
                st.error("Please agree to the Terms and Conditions")
            else:
                with st.spinner("Creating account..."):
                    success, message = auth_manager.register_user(
                        email=email,
                        password=password,
                        name=name
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.info("Please login with your credentials")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")

def show_logout_button():
    """Show logout button in sidebar"""
    with st.sidebar:
        st.markdown("---")
        
        user = auth_manager.get_current_user()
        if user:
            st.markdown(f"👤 **{user['name']}**")
            st.caption(user['email'])
            
            # Show role badge
            role = user.get('role', 'student')
            role_colors = {
                'student': '🎓',
                'admin': '👨‍💼',
                'super_admin': '👑'
            }
            st.caption(f"Role: {role_colors.get(role, '👤')} {role.replace('_', ' ').title()}")
            
            if st.button("🚪 Logout", width='stretch'):
                auth_manager.logout()
                st.success("Logged out successfully")
                st.rerun()