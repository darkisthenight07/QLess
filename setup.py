# setup.py - Initialize QLess Database

from utils.firebase_config import initialize_firebase, get_db_reference
from auth.authentication import auth_manager
from services.facility_service import facility_service
from config import SUPER_ADMIN_EMAILS, ROLES
from datetime import datetime

def setup_database():
    """Initialize database with default data"""
    
    print("🔧 Initializing QLess Database...")
    print("=" * 60)
    
    # Initialize Firebase
    initialize_firebase()
    
    # 1. Create default facilities
    print("\n📍 Creating default facilities...")
    
    default_facilities = [
        {
            'name': 'Food Sutra Mess Hall',
            'capacity': 200,
            'icon': '🍽️',
            'avg_time_per_person': 2,
            'open_hour_start': 7,
            'open_hour_end': 22,
            'description': 'serving breakfast, lunch, and dinner'
        },
        {
            'name': 'Sheela Mess Hall',
            'capacity': 200,
            'icon': '🍽️',
            'avg_time_per_person': 2,
            'open_hour_start': 7,
            'open_hour_end': 22,
            'description': 'serving breakfast, lunch, and dinner'
        },
        {
            'name': 'Surinder Arora Mess Hall',
            'capacity': 200,
            'icon': '🍽️',
            'avg_time_per_person': 2,
            'open_hour_start': 7,
            'open_hour_end': 22,
            'description': 'serving breakfast, lunch, and dinner'
        }
    ]
    
    for facility in default_facilities:
        success, message = facility_service.create_facility(**facility)
        if success:
            print(f"   ✅ Created: {facility['icon']} {facility['name']}")
        else:
            print(f"   ⚠️  {facility['name']}: {message}")
    
    # 2. Create admin accounts
    print("\n👥 Creating admin accounts...")
    
    for email in SUPER_ADMIN_EMAILS:
        success, message = auth_manager.register_user(
            email=email,
            password='admin123',  # Default password - CHANGE THIS!
            name='Admin User',
            role=ROLES['SUPER_ADMIN']
        )
        
        if success:
            print(f"   ✅ Created admin: {email}")
            print(f"      🔑 Default password: admin123 (CHANGE THIS!)")
        else:
            print(f"   ⚠️  {email}: {message}")
    
    # 3. Create sample student account
    print("\n🎓 Creating sample student account...")
    
    success, message = auth_manager.register_user(
        email='student@campus.edu',
        password='student123',
        name='Test Student',
        role=ROLES['STUDENT']
    )
    
    if success:
        print(f"   ✅ Created student: student@campus.edu")
        print(f"      🔑 Password: student123")
    else:
        print(f"   ⚠️  {message}")
    
    # 4. Initialize settings
    print("\n⚙️  Initializing system settings...")
    
    settings_ref = get_db_reference('settings')
    settings_ref.set({
        'app_name': 'QLess',
        'version': '1.0.0',
        'initialized_at': datetime.now().isoformat(),
        'auto_refresh_interval': 5000,
        'features': {
            'notifications': False,
            'predictions': False
        }
    })
    
    print("   ✅ Settings initialized")
    
    # Success message
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\n🚀 You can now run: streamlit run app.py")
    print("\n📝 Default Login Credentials:")
    print("   Admin: admin@campus.edu / admin123")
    print("   Student: student@campus.edu / student123")
    print("\n⚠️  IMPORTANT: Change default passwords after first login!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        setup_database()
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nPlease check:")
        print("1. serviceAccountKey.json is in the project root")
        print("2. Firebase database URL is correct in config.py")
        print("3. Firebase Realtime Database is enabled")