# views/admin_view.py - Admin Interface

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.qr_service import qr_service
import base64
from datetime import datetime
from services.facility_service import facility_service
from services.queue_service import queue_service
from auth.authentication import auth_manager
from config import APP_CONFIG, ROLES

# Auto-refresh
count = st_autorefresh(interval=APP_CONFIG['auto_refresh_interval'], key="admin_refresh")

def show_admin_view():
    """Main admin interface"""
    
    st.title(f"👨‍💼 {APP_CONFIG['app_name']} - Admin Dashboard")
    
    # Admin menu
    menu = st.sidebar.radio(
        "Admin Menu",
        ["📊 Overview", "🏢 Manage Facilities", "📈 Analytics", "👥 User Management"],
        key="admin_menu"
    )
    
    if menu == "📊 Overview":
        show_overview()
    elif menu == "🏢 Manage Facilities":
        show_facility_management()
    elif menu == "📈 Analytics":
        show_analytics()
    elif menu == "👥 User Management":
        show_user_management()

def show_overview():
    """Show dashboard overview"""
    st.subheader("📊 Real-Time Overview")
    
    facilities = facility_service.get_all_facilities()
    
    if not facilities:
        st.warning("No facilities configured yet. Add facilities to get started.")
        return
    
    # Summary metrics
    total_capacity = sum(f['capacity'] for f in facilities)
    all_status = queue_service.get_all_queue_status()
    total_active = sum(s.get('count', 0) for s in all_status.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Facilities", len(facilities))
    
    with col2:
        st.metric("Total Capacity", total_capacity)
    
    with col3:
        st.metric("Active Users", total_active)
    
    with col4:
        occupancy = (total_active / total_capacity * 100) if total_capacity > 0 else 0
        st.metric("Overall Occupancy", f"{occupancy:.1f}%")
    
    st.markdown("---")
    
    # Facility cards
    st.subheader("🏢 Facility Status")
    
    cols = st.columns(min(len(facilities), 3))
    
    for idx, facility in enumerate(facilities):
        col = cols[idx % 3]
        
        with col:
            stats = facility_service.get_facility_stats(facility['id'])
            
            with st.container():
                st.markdown(f"### {facility['icon']} {facility['name']}")
                
                st.metric("Queue", stats['current_count'])
                st.metric("Wait Time", f"{stats['wait_time']} min")
                
                status = stats['status']
                st.markdown(f"**Status:** {status['emoji']} {status['text']}")
                
                # Quick actions
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("🔄 Reset", key=f"reset_{facility['id']}"):
                        success, message = queue_service.reset_queue(facility['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                with col_b:
                    if st.button("📊 Details", key=f"details_{facility['id']}"):
                        st.session_state.selected_facility = facility['id']
                        st.rerun()

def show_facility_management():
    """Facility management interface"""
    st.subheader("🏢 Manage Facilities")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Facility", "📝 Edit Facilities", "🗑️ Deleted Facilities", "📱 QR Codes"])
    
    with tab1:
        show_add_facility_form()
    
    with tab2:
        show_edit_facilities()
    
    with tab3:
        show_deleted_facilities()

    with tab4:
        show_qr_codes()

def show_add_facility_form():
    """Form to add new facility"""
    st.markdown("### ➕ Add New Facility")
    
    with st.form("add_facility_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Facility Name*", placeholder="e.g., Main Cafeteria")
            
            capacity = st.number_input(
                "Capacity*",
                min_value=1,
                max_value=1000,
                value=100,
                help="Maximum number of people"
            )
            
            icon = st.text_input(
                "Icon (Emoji)*",
                value="🏢",
                help="Choose an emoji to represent this facility"
            )
        
        with col2:
            avg_time = st.number_input(
                "Avg. Time per Person (minutes)*",
                min_value=1,
                max_value=60,
                value=3,
                help="Average time each person spends"
            )
            
            col_start, col_end = st.columns(2)
            
            with col_start:
                open_hour = st.number_input(
                    "Opening Hour",
                    min_value=0,
                    max_value=23,
                    value=8,
                    help="24-hour format"
                )
            
            with col_end:
                close_hour = st.number_input(
                    "Closing Hour",
                    min_value=0,
                    max_value=23,
                    value=22,
                    help="24-hour format"
                )
        
        description = st.text_area(
            "Description (Optional)",
            placeholder="Brief description of this facility...",
            max_chars=200
        )
        
        submit = st.form_submit_button("➕ Create Facility", type="primary", width='stretch')
        
        if submit:
            if not name or not icon:
                st.error("Please fill in all required fields")
            elif open_hour >= close_hour:
                st.error("Opening hour must be before closing hour")
            else:
                success, message = facility_service.create_facility(
                    name=name,
                    capacity=capacity,
                    icon=icon,
                    avg_time_per_person=avg_time,
                    open_hour_start=open_hour,
                    open_hour_end=close_hour,
                    description=description
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

def show_edit_facilities():
    """Edit existing facilities"""
    facilities = facility_service.get_all_facilities(include_inactive=False)
    
    if not facilities:
        st.info("No facilities to edit")
        return
    
    st.markdown("### 📝 Edit Existing Facilities")
    
    # Facility selector
    facility_options = {f['id']: f"{f['icon']} {f['name']}" for f in facilities}
    
    selected_id = st.selectbox(
        "Select Facility to Edit",
        options=list(facility_options.keys()),
        format_func=lambda x: facility_options[x]
    )
    
    if not selected_id:
        return
    
    facility = facility_service.get_facility(selected_id)
    
    # Edit form
    with st.form(f"edit_facility_{selected_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Facility Name", value=facility['name'])
            capacity = st.number_input("Capacity", min_value=1, value=facility['capacity'])
            icon = st.text_input("Icon", value=facility['icon'])
        
        with col2:
            avg_time = st.number_input(
                "Avg. Time per Person",
                min_value=1,
                value=facility['avg_time_per_person']
            )
            
            open_hours = facility.get('open_hours', {'start': 8, 'end': 22})
            
            col_start, col_end = st.columns(2)
            with col_start:
                open_hour = st.number_input("Opening Hour", value=open_hours['start'])
            with col_end:
                close_hour = st.number_input("Closing Hour", value=open_hours['end'])
        
        description = st.text_area(
            "Description",
            value=facility.get('description', ''),
            max_chars=200
        )
        
        col_save, col_delete = st.columns(2)
        
        with col_save:
            save = st.form_submit_button("💾 Save Changes", type="primary", width='stretch')
        
        with col_delete:
            delete = st.form_submit_button("🗑️ Delete", width='stretch')
        
        if save:
            updates = {
                'name': name,
                'capacity': capacity,
                'icon': icon,
                'avg_time_per_person': avg_time,
                'open_hours': {'start': open_hour, 'end': close_hour},
                'description': description
            }
            
            success, message = facility_service.update_facility(selected_id, updates)
            
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")
        
        if delete:
            success, message = facility_service.delete_facility(selected_id)
            
            if success:
                st.warning(f"🗑️ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")

def show_deleted_facilities():
    """Show and restore deleted facilities"""
    facilities = facility_service.get_all_facilities(include_inactive=True)
    deleted = [f for f in facilities if not f.get('active', True)]
    
    if not deleted:
        st.info("No deleted facilities")
        return
    
    st.markdown("### 🗑️ Deleted Facilities")
    
    for facility in deleted:
        with st.expander(f"{facility['icon']} {facility['name']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Capacity:** {facility['capacity']}")
                st.write(f"**Deleted:** {facility.get('deleted_at', 'Unknown')}")
            
            with col2:
                if st.button("♻️ Restore", key=f"restore_{facility['id']}"):
                    success, message = facility_service.restore_facility(facility['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                        
def show_qr_codes():
    """Generate and display QR codes for facilities"""
    st.markdown("### 📱 Facility QR Codes")
    st.info("💡 Students must scan these QR codes to check in at facilities")
    
    facilities = facility_service.get_all_facilities(include_inactive=False)
    
    if not facilities:
        st.warning("No facilities available")
        return
    
    # Display QR codes in a grid
    cols = st.columns(2)
    
    for idx, facility in enumerate(facilities):
        col = cols[idx % 2]
        
        with col:
            with st.container():
                st.markdown(f"#### {facility['icon']} {facility['name']}")
                
                # Generate QR code
                img_str, qr_data = qr_service.generate_facility_qr(
                    facility['id'],
                    facility['name']
                )
                
                # Display QR code
                st.image(f"data:image/png;base64,{img_str}", width=300)
                
                # Download button
                qr_bytes = base64.b64decode(img_str)
                st.download_button(
                    label="💾 Download QR Code",
                    data=qr_bytes,
                    file_name=f"qr_{facility['id']}.png",
                    mime="image/png",
                    key=f"download_qr_{facility['id']}"
                )
                
                st.markdown("---")

def show_analytics():
    """Show analytics dashboard"""
    st.subheader("📈 Analytics & Insights")
    
    facilities = facility_service.get_all_facilities()
    
    if not facilities:
        st.warning("No facilities available for analytics")
        return
    
    # Facility selector
    facility_options = {f['id']: f"{f['icon']} {f['name']}" for f in facilities}
    
    selected_id = st.selectbox(
        "Select Facility",
        options=list(facility_options.keys()),
        format_func=lambda x: facility_options[x],
        key="analytics_facility"
    )
    
    # Get history
    history = queue_service.get_queue_history(selected_id, limit=200)
    
    if not history:
        st.info("No historical data available yet")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    
    # Hourly average chart
    hourly_avg = df.groupby('hour')['count'].mean().reset_index()
    
    fig = px.line(
        hourly_avg,
        x='hour',
        y='count',
        title='Average Queue by Hour',
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Average Queue Count",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Peak Hour", f"{df.groupby('hour')['count'].mean().idxmax()}:00")
    
    with col2:
        st.metric("Avg Queue", f"{df['count'].mean():.1f}")
    
    with col3:
        st.metric("Max Queue", df['count'].max())

def show_user_management():
    """User management (super admin only)"""
    
    if not auth_manager.is_super_admin():
        st.warning("🔒 This section is only accessible to Super Admins")
        return
    
    st.subheader("👥 User Management")
    
    users = auth_manager.get_all_users()
    
    if not users:
        st.info("No users registered yet")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(users)
    
    # Display users
    st.dataframe(
        df[['name', 'email', 'role', 'points', 'active']],
        width='stretch',
        hide_index=True
    )
    
    # User actions
    st.markdown("---")
    st.markdown("### Manage Individual User")
    
    user_options = {u['uid']: f"{u['name']} ({u['email']})" for u in users}
    
    selected_uid = st.selectbox(
        "Select User",
        options=list(user_options.keys()),
        format_func=lambda x: user_options[x]
    )
    
    if selected_uid:
        user = next(u for u in users if u['uid'] == selected_uid)
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_role = st.selectbox(
                "Change Role",
                options=[ROLES['STUDENT'], ROLES['ADMIN'], ROLES['SUPER_ADMIN']],
                index=[ROLES['STUDENT'], ROLES['ADMIN'], ROLES['SUPER_ADMIN']].index(user['role'])
            )
            
            if st.button("💾 Update Role"):
                success, message = auth_manager.update_user_role(selected_uid, new_role)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            status_text = "Deactivate" if user['active'] else "Activate"
            
            if st.button(f"🔄 {status_text} User"):
                success, message = auth_manager.toggle_user_status(selected_uid)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
