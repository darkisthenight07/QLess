# services/queue_service.py - Queue Management Service

from datetime import datetime
from utils.firebase_config import get_db_reference
import streamlit as st

class QueueService:
    """Service for managing queues"""
    
    def __init__(self):
        self.queues_ref = get_db_reference('queues')
        self.history_ref = get_db_reference('history')
        self.active_queues_ref = get_db_reference('active_queues')
    
    def get_queue_status(self, facility_id):
        """Get current queue status"""
        try:
            queue_ref = self.queues_ref.child(facility_id)
            data = queue_ref.get()
            
            if data:
                return {
                    'count': data.get('count', 0),
                    'last_updated': data.get('last_updated'),
                    'facility_id': facility_id
                }
            
            return {
                'count': 0,
                'last_updated': datetime.now().isoformat(),
                'facility_id': facility_id
            }
        
        except Exception as e:
            st.error(f"Error fetching queue status: {e}")
            return {'count': 0, 'last_updated': None, 'facility_id': facility_id}
    
    def is_user_checked_in(self, user_id):
        """Check if user is currently checked in to any facility"""
        try:
            all_active_queues = self.active_queues_ref.get()
            
            if not all_active_queues:
                return False, None
            
            # Check all facilities for this user
            for facility_id, users in all_active_queues.items():
                if users and user_id in users:
                    return True, facility_id
            
            return False, None
        
        except Exception as e:
            st.error(f"Error checking user status: {e}")
            return False, None
    
    def get_user_current_facility(self, user_id):
        """Get the facility where user is currently checked in"""
        is_checked_in, facility_id = self.is_user_checked_in(user_id)
        if is_checked_in:
            return facility_id
        return None
    
    def checkin(self, facility_id, user_id=None, user_name=None):
        """Check in to a facility"""
        try:
            # Check if user is already checked in somewhere
            if user_id:
                is_checked_in, current_facility = self.is_user_checked_in(user_id)
                if is_checked_in:
                    if current_facility == facility_id:
                        return False, None, "You are already checked in to this facility"
                    else:
                        # Get facility name for better message
                        from services.facility_service import facility_service
                        facility = facility_service.get_facility(current_facility)
                        facility_name = facility['name'] if facility else current_facility
                        return False, None, f"You are already checked in to {facility_name}. Please check out first."
            
            queue_ref = self.queues_ref.child(facility_id)
            current = queue_ref.get() or {}
            current_count = current.get('count', 0)
            
            new_count = current_count + 1
            
            # Update queue count
            queue_ref.update({
                'count': new_count,
                'last_updated': datetime.now().isoformat()
            })
            
            # Log to history
            history_entry = {
                'action': 'checkin',
                'count': new_count,
                'timestamp': datetime.now().isoformat(),
                'hour': datetime.now().hour,
                'day': datetime.now().strftime('%A')
            }
            
            if user_id:
                history_entry['user_id'] = user_id
                history_entry['user_name'] = user_name
            
            self.history_ref.child(facility_id).push(history_entry)
            
            # Add user to active queue
            if user_id:
                self.active_queues_ref.child(facility_id).child(user_id).set({
                    'name': user_name,
                    'checkin_time': datetime.now().isoformat()
                })
            
            return True, new_count, "Checked in successfully"
        
        except Exception as e:
            return False, None, f"Check-in failed: {str(e)}"
    
    def checkout(self, facility_id, user_id=None):
        """Check out from a facility"""
        try:
            # If user_id provided, verify they're checked in to this facility
            if user_id:
                is_checked_in, current_facility = self.is_user_checked_in(user_id)
                if not is_checked_in:
                    return False, None, "You are not checked in to any facility"
                if current_facility != facility_id:
                    from services.facility_service import facility_service
                    facility = facility_service.get_facility(current_facility)
                    facility_name = facility['name'] if facility else current_facility
                    return False, None, f"You are checked in to {facility_name}, not this facility"
            
            queue_ref = self.queues_ref.child(facility_id)
            current = queue_ref.get() or {}
            current_count = current.get('count', 0)
            
            if current_count <= 0:
                return False, 0, "Queue is already empty"
            
            new_count = current_count - 1
            
            # Update queue count
            queue_ref.update({
                'count': new_count,
                'last_updated': datetime.now().isoformat()
            })
            
            # Log to history
            history_entry = {
                'action': 'checkout',
                'count': new_count,
                'timestamp': datetime.now().isoformat(),
                'hour': datetime.now().hour,
                'day': datetime.now().strftime('%A')
            }
            
            if user_id:
                history_entry['user_id'] = user_id
            
            self.history_ref.child(facility_id).push(history_entry)
            
            # Remove user from active queue
            if user_id:
                self.active_queues_ref.child(facility_id).child(user_id).delete()
            
            return True, new_count, "Checked out successfully"
        
        except Exception as e:
            return False, None, f"Check-out failed: {str(e)}"
    
    def get_active_users(self, facility_id):
        """Get list of users currently in queue"""
        try:
            active_ref = self.active_queues_ref.child(facility_id)
            users = active_ref.get()
            
            if not users:
                return []
            
            user_list = []
            for uid, data in users.items():
                user_list.append({
                    'uid': uid,
                    'name': data.get('name'),
                    'checkin_time': data.get('checkin_time')
                })
            
            return user_list
        
        except Exception as e:
            st.error(f"Error fetching active users: {e}")
            return []
    
    def reset_queue(self, facility_id):
        """Reset queue count to zero (admin only)"""
        try:
            queue_ref = self.queues_ref.child(facility_id)
            queue_ref.set({
                'count': 0,
                'last_updated': datetime.now().isoformat()
            })
            
            # Clear active queue
            self.active_queues_ref.child(facility_id).delete()
            
            # Log reset action
            self.history_ref.child(facility_id).push({
                'action': 'reset',
                'count': 0,
                'timestamp': datetime.now().isoformat(),
                'admin_id': st.session_state.get('user', {}).get('uid', 'system')
            })
            
            return True, "Queue reset successfully"
        
        except Exception as e:
            return False, f"Failed to reset queue: {str(e)}"
    
    def get_queue_history(self, facility_id, limit=100):
        """Get queue history for analytics"""
        try:
            history_ref = self.history_ref.child(facility_id)
            history = history_ref.get()
            
            if not history:
                return []
            
            history_list = []
            for key, value in history.items():
                if isinstance(value, dict):
                    history_list.append({
                        'id': key,
                        **value
                    })
            
            # Sort by timestamp (most recent first)
            history_list.sort(
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            
            return history_list[:limit]
        
        except Exception as e:
            st.error(f"Error fetching history: {e}")
            return []
    
    def get_all_queue_status(self):
        """Get status of all queues"""
        try:
            queues = self.queues_ref.get()
            
            if not queues:
                return {}
            
            status_dict = {}
            for facility_id, data in queues.items():
                status_dict[facility_id] = {
                    'count': data.get('count', 0),
                    'last_updated': data.get('last_updated')
                }
            
            return status_dict
        
        except Exception as e:
            st.error(f"Error fetching all queues: {e}")
            return {}

# Initialize service
queue_service = QueueService()