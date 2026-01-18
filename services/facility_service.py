# services/facility_service.py - Facility Management Service

from datetime import datetime
from utils.firebase_config import get_db_reference
from config import DEFAULT_FACILITY_CONFIG
import streamlit as st

class FacilityService:
    """Service for managing facilities"""
    
    def __init__(self):
        self.facilities_ref = get_db_reference('facilities')
        self.queues_ref = get_db_reference('queues')
    
    def create_facility(self, name, capacity, icon, avg_time_per_person, 
                       open_hour_start=8, open_hour_end=22, description=""):
        """Create a new facility"""
        try:
            # Generate facility ID
            facility_id = name.lower().replace(' ', '_').replace('-', '_')
            
            # Check if facility exists
            facility_ref = self.facilities_ref.child(facility_id)
            if facility_ref.get():
                return False, "Facility with this name already exists"
            
            # Create facility
            facility_data = {
                'id': facility_id,
                'name': name,
                'capacity': capacity,
                'icon': icon,
                'avg_time_per_person': avg_time_per_person,
                'open_hours': {
                    'start': open_hour_start,
                    'end': open_hour_end
                },
                'description': description,
                'active': True,
                'created_at': datetime.now().isoformat(),
                'created_by': st.session_state.get('user', {}).get('uid', 'system')
            }
            
            facility_ref.set(facility_data)
            
            # Initialize queue for this facility
            queue_ref = self.queues_ref.child(facility_id)
            queue_ref.set({
                'count': 0,
                'last_updated': datetime.now().isoformat()
            })
            
            return True, "Facility created successfully"
        
        except Exception as e:
            return False, f"Failed to create facility: {str(e)}"
    
    def get_all_facilities(self, include_inactive=False):
        """Get all facilities"""
        facilities = self.facilities_ref.get()
        
        if not facilities:
            return []
        
        facility_list = []
        for fid, data in facilities.items():
            # Skip inactive if not requested
            if not include_inactive and not data.get('active', True):
                continue
            
            facility_list.append({
                'id': fid,
                'name': data.get('name'),
                'capacity': data.get('capacity'),
                'icon': data.get('icon'),
                'avg_time_per_person': data.get('avg_time_per_person'),
                'open_hours': data.get('open_hours'),
                'description': data.get('description', ''),
                'active': data.get('active', True),
                'created_at': data.get('created_at')
            })
        
        # Sort by name
        facility_list.sort(key=lambda x: x['name'])
        
        return facility_list
    
    def get_facility(self, facility_id):
        """Get a specific facility"""
        facility_ref = self.facilities_ref.child(facility_id)
        data = facility_ref.get()
        
        if not data:
            return None
        
        return {
            'id': facility_id,
            **data
        }
    
    def update_facility(self, facility_id, updates):
        """Update facility details"""
        try:
            facility_ref = self.facilities_ref.child(facility_id)
            
            if not facility_ref.get():
                return False, "Facility not found"
            
            # Add update timestamp
            updates['updated_at'] = datetime.now().isoformat()
            updates['updated_by'] = st.session_state.get('user', {}).get('uid', 'system')
            
            facility_ref.update(updates)
            return True, "Facility updated successfully"
        
        except Exception as e:
            return False, f"Failed to update facility: {str(e)}"
    
    def delete_facility(self, facility_id):
        """Delete a facility (soft delete)"""
        try:
            facility_ref = self.facilities_ref.child(facility_id)
            
            if not facility_ref.get():
                return False, "Facility not found"
            
            # Soft delete - mark as inactive
            facility_ref.update({
                'active': False,
                'deleted_at': datetime.now().isoformat(),
                'deleted_by': st.session_state.get('user', {}).get('uid', 'system')
            })
            
            return True, "Facility deleted successfully"
        
        except Exception as e:
            return False, f"Failed to delete facility: {str(e)}"
    
    def restore_facility(self, facility_id):
        """Restore a deleted facility"""
        try:
            facility_ref = self.facilities_ref.child(facility_id)
            
            if not facility_ref.get():
                return False, "Facility not found"
            
            facility_ref.update({
                'active': True,
                'restored_at': datetime.now().isoformat()
            })
            
            return True, "Facility restored successfully"
        
        except Exception as e:
            return False, f"Failed to restore facility: {str(e)}"
    
    def get_facility_stats(self, facility_id):
        """Get statistics for a facility"""
        # Get queue data
        queue_ref = self.queues_ref.child(facility_id)
        queue_data = queue_ref.get()
        
        # Get facility data
        facility = self.get_facility(facility_id)
        
        if not facility:
            return None
        
        current_count = queue_data.get('count', 0) if queue_data else 0
        capacity = facility['capacity']
        
        return {
            'current_count': current_count,
            'capacity': capacity,
            'occupancy_percentage': (current_count / capacity * 100) if capacity > 0 else 0,
            'wait_time': current_count * facility['avg_time_per_person'],
            'status': self._get_status(current_count, capacity),
            'last_updated': queue_data.get('last_updated') if queue_data else None
        }
    
    def _get_status(self, count, capacity):
        """Calculate status based on occupancy"""
        occupancy = (count / capacity) * 100 if capacity > 0 else 0
        
        if occupancy < 40:
            return {'level': 'low', 'emoji': '🟢', 'text': 'Low', 'color': '#28a745'}
        elif occupancy < 70:
            return {'level': 'moderate', 'emoji': '🟡', 'text': 'Moderate', 'color': '#ffc107'}
        else:
            return {'level': 'high', 'emoji': '🔴', 'text': 'High', 'color': '#dc3545'}
    
    def get_facility_display_name(self, facility_id):
        """Get formatted display name with icon"""
        facility = self.get_facility(facility_id)
        if not facility:
            return facility_id
        
        icon = facility.get('icon', '🏢')
        name = facility.get('name', facility_id)
        return f"{icon} {name}"

# Initialize service
facility_service = FacilityService()