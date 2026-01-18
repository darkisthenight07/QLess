# views/student_view.py - Student Interface

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
from services.qr_service import qr_service
from utils.qr_scanner import decode_qr_from_camera
from services.facility_service import facility_service
from services.queue_service import queue_service
from auth.authentication import auth_manager
from config import APP_CONFIG

# Auto-refresh only if not using camera
if 'using_camera' not in st.session_state:
    st.session_state.using_camera = False

if not st.session_state.using_camera:
    count = st_autorefresh(interval=APP_CONFIG['auto_refresh_interval'], key="student_refresh")

def show_student_view():
    """Main student interface"""
    
    st.title(f"🎓 {APP_CONFIG['app_name']} - Student Portal")
    query_params = st.query_params
    if 'facility' in query_params:
        facility_from_qr = query_params['facility']
        if 'scanned_from_url' not in st.session_state:
            st.session_state.scanned_qr_data = f"QLESS_CHECKIN:{facility_from_qr}"
            st.session_state.scanned_facility_id = facility_from_qr
            st.session_state.scanned_from_url = True
    st.markdown("### Check real-time queue status and manage your visits")
    
    # Check user's current check-in status
    user = auth_manager.get_current_user()
    user_id = user['uid'] if user else None
    
    current_facility = None
    if user_id:
        current_facility = queue_service.get_user_current_facility(user_id)
    
    # Show check-in status banner
    if current_facility:
        facility = facility_service.get_facility(current_facility)
        if facility:
            st.success(f"✅ You are currently checked in to **{facility['icon']} {facility['name']}**")
    
    # Get all active facilities
    facilities = facility_service.get_all_facilities(include_inactive=False)
    
    if not facilities:
        st.warning("No facilities available at the moment. Please check back later.")
        return
    
    # Show all facilities overview by default
    st.markdown("---")
    display_all_facilities_overview(facilities, current_facility)
    
    # QR Scanner buttons
    st.markdown("---")
    display_qr_scanner(current_facility)

def display_qr_scanner(current_facility):
    """Display QR code scanner for check-in"""
    
    st.subheader("📱 Scan QR Code to Check In")
    
    user = auth_manager.get_current_user()
    user_id = user['uid'] if user else None
    user_name = user['name'] if user else "Guest"
    
    # Show current status
    if current_facility:
        facility = facility_service.get_facility(current_facility)
        if facility:
            st.success(f"✅ Currently checked in at: **{facility['icon']} {facility['name']}**")
            
            # Checkout button
            if st.button("🚪 Check Out", width='stretch', type="primary", key="checkout_main"):
                success, new_count, message = queue_service.checkout(
                    current_facility,
                    user_id=user_id
                )
                
                if success:
                    st.success(f"👋 {message}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            
            st.info("ℹ️ Check out before scanning a new QR code")
            return
    
    # Initialize session state for scanned data
    if 'scanned_qr_data' not in st.session_state:
        st.session_state.scanned_qr_data = None
    if 'scanned_facility_id' not in st.session_state:
        st.session_state.scanned_facility_id = None
    
    # If already scanned and validated, show confirmation
    if st.session_state.scanned_qr_data and st.session_state.scanned_facility_id:
        facility = facility_service.get_facility(st.session_state.scanned_facility_id)
        
        if facility:
            st.success(f"✅ QR Code Validated: **{facility['icon']} {facility['name']}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Confirm Check-In", width='stretch', type="primary", key="confirm_checkin_btn"):
                    success, new_count, message = queue_service.checkin(
                        st.session_state.scanned_facility_id,
                        user_id=user_id,
                        user_name=user_name
                    )
                    
                    if success:
                        st.success(f"🎉 {message}")
                        st.balloons()
                        # Clear session state
                        st.session_state.scanned_qr_data = None
                        st.session_state.scanned_facility_id = None
                        st.session_state.using_camera = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            with col2:
                if st.button("❌ Cancel", width='stretch', key="cancel_checkin_btn"):
                    # Clear session state
                    st.session_state.scanned_qr_data = None
                    st.session_state.scanned_facility_id = None
                    st.session_state.using_camera = False
                    st.rerun()
        return
    
    # QR Scanner
    st.info("🎯 Scan the facility's QR code to check in")
    
    # Set flag to disable auto-refresh
    st.session_state.using_camera = True
    
    camera_image = st.camera_input("Take a picture of the QR code")
    
    if camera_image:
        with st.spinner("Scanning QR code..."):
            success, qr_data, message = decode_qr_from_camera(camera_image)
            
            if not success:
                st.error(f"❌ {message}")
                st.info("💡 Make sure the QR code is clearly visible and well-lit")
                return
            
            # Validate QR code
            valid, facility_id, validation_msg = qr_service.validate_qr_data(qr_data)
            
            if not valid:
                st.error(f"❌ {validation_msg}")
                st.warning("⚠️ This is not a valid QLess facility QR code")
                return
            
            # Store in session state
            st.session_state.scanned_qr_data = qr_data
            st.session_state.scanned_facility_id = facility_id
            st.rerun()

def display_all_facilities_overview(facilities, current_facility):
    """Display overview of all facilities"""
    
    st.subheader("📊 All Facilities Overview")
    
    # Get queue status for all facilities
    all_status = queue_service.get_all_queue_status()
    
    cols = st.columns(min(len(facilities), 4))
    
    for idx, facility in enumerate(facilities):
        col = cols[idx % 4]
        
        facility_id = facility['id']
        status_data = all_status.get(facility_id, {'count': 0})
        count = status_data.get('count', 0)
        
        # Calculate status
        capacity = facility['capacity']
        occupancy = (count / capacity * 100) if capacity > 0 else 0
        
        if occupancy < 40:
            color = '#28a745'
            status_text = 'Low'
        elif occupancy < 70:
            color = '#ffc107'
            status_text = 'Moderate'
        else:
            color = '#dc3545'
            status_text = 'High'
        
        # Add indicator if user is checked in here
        checked_in_badge = ""
        if facility_id == current_facility:
            checked_in_badge = "<p style='color: #007bff; font-weight: bold; margin: 5px 0;'>✓ You're here</p>"
        
        with col:
            st.markdown(f"""
            <div style="background-color: {color}20; padding: 15px; border-radius: 10px; 
                        border-left: 5px solid {color}; margin-bottom: 10px;">
                <h4>{facility['icon']} {facility['name']}</h4>
                <p style="font-size: 30px; margin: 5px 0; font-weight: bold;">{count}</p>
                <p style="color: {color}; font-weight: bold; margin: 0;">{status_text}</p>
                {checked_in_badge}
            </div>
            """, unsafe_allow_html=True)