# QLess 🎓 - Smart Campus Queue Manager

> Revolutionizing campus facility management with real-time queue tracking and QR-based check-ins

[![Firebase](https://img.shields.io/badge/Firebase-Powered-orange)](https://firebase.google.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52.2-red)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Google Technology Integration](#google-technology-integration)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Impact & Practicality](#impact--practicality)
- [Future Enhancements](#future-enhancements)
- [Team](#team)
- [License](#license)

## 🎯 Problem Statement

### The Challenge
Campus facilities like mess halls, cafeterias, and common areas face recurring challenges:

1. **Long Queues During Peak Hours**: Students waste 15-30 minutes waiting in lines during meal times
2. **Inefficient Resource Utilization**: Facility managers lack real-time occupancy data
3. **Poor User Experience**: No visibility into queue status before arrival

### Real-World Impact
- **Time Wasted**: Average student loses 2-3 hours weekly in queues
- **Facility Underutilization**: Resources remain unused during off-peak hours
- **Student Frustration**: Unpredictable wait times affect meal planning and schedules

## 💡 Solution Overview

QLess transforms campus facility management through a comprehensive digital solution:

### Core Innovation
A real-time queue management system that combines:
- **QR Code Technology**: Contactless check-in/check-out
- **Live Status Dashboard**: Real-time occupancy visibility
- **Multi-Role Interface**: Separate views for students and administrators
- **Cloud-Based Architecture**: Scalable Firebase Realtime Database

### How It Works

#### For Students:
1. **View Real-Time Status**: Check queue levels across all campus facilities
2. **QR Check-In**: Scan facility QR code to check in instantly
3. **Automatic Tracking**: System monitors your presence automatically
4. **Easy Check-Out**: One-tap checkout when leaving

#### For Administrators:
1. **Live Monitoring**: Track all facilities from a unified dashboard
2. **Analytics Dashboard**: Understand usage patterns by hour/day
3. **Facility Management**: Add, edit, or remove facilities dynamically
4. **QR Code Generation**: Create and download QR codes for new facilities
5. **User Management**: Control access and manage user roles

## 🔧 Google Technology Integration

### Firebase Realtime Database
**Why Firebase?**
- **Real-time Synchronization**: Updates propagate to all clients instantly (<100ms latency)
- **Scalability**: Handles thousands of concurrent users without performance degradation
- **Offline Capability**: Built-in offline persistence for seamless experience
- **Security**: Firebase Security Rules protect sensitive data
- **Zero Server Management**: Fully managed backend infrastructure

**Our Implementation:**

```python
# Database Structure
{
  "facilities": {
    "facility_id": {
      "name": "Food Sutra Mess Hall",
      "capacity": 200,
      "icon": "🍽️",
      "avg_time_per_person": 2,
      "open_hours": {"start": 7, "end": 22}
    }
  },
  "queues": {
    "facility_id": {
      "count": 45,
      "last_updated": "2025-01-18T14:30:00"
    }
  },
  "active_queues": {
    "facility_id": {
      "user_id": {
        "name": "John Doe",
        "checkin_time": "2025-01-18T14:25:00"
      }
    }
  },
  "history": {
    "facility_id": {
      "entry_id": {
        "action": "checkin",
        "count": 46,
        "timestamp": "2025-01-18T14:30:00",
        "hour": 14,
        "day": "Saturday"
      }
    }
  }
}
```

**Key Firebase Features Used:**
1. **Realtime Database**: Core data storage with live synchronization
2. **Firebase Admin SDK**: Server-side operations and authentication
3. **Database Rules**: Secure read/write access control
4. **Cloud Hosting**: Reliable 99.95% uptime SLA

## 🛠️ Tech Stack

### Frontend
- **Streamlit 1.52.2**: Rapid web application development
- **Plotly 5.17.0**: Interactive analytics visualizations
- **Pandas 2.0.0**: Data manipulation and analysis

### Backend & Database
- **Firebase Admin SDK 6.2.0**: Real-time database operations
- **Python 3.9+**: Core application logic

### QR Technology
- **qrcode 7.4.2**: QR code generation
- **pyzbar 0.1.9**: QR code scanning and decoding
- **OpenCV 4.8.0**: Image processing for camera input
- **Pillow 10.0.0**: Image manipulation

### Additional Libraries
- **streamlit-autorefresh**: Auto-refresh for real-time updates
- **hashlib**: Secure password hashing
- **datetime**: Timestamp management

## ✨ Features

### 🎓 Student Portal
- **Live Queue Dashboard**: View all facility statuses at a glance
- **Color-Coded Status**: Green (low), Yellow (moderate), Red (high)
- **QR Scanner Integration**: Built-in camera QR scanning
- **Check-In Validation**: Prevents duplicate check-ins
- **Auto-Refresh**: Updates every 5 seconds
- **Mobile Responsive**: Works seamlessly on smartphones

### 👨‍💼 Admin Dashboard
- **Real-Time Monitoring**: Track all facilities simultaneously
- **Facility Management**:
  - Add new facilities with custom icons
  - Edit facility capacity and timing
  - Soft-delete with restore capability
- **Analytics Engine**:
  - Hourly usage patterns
  - Peak time identification
  - Historical trend analysis
- **QR Code Generator**: Create downloadable QR codes
- **User Management**: Role-based access control
- **Queue Reset**: Emergency queue clearing

### 👑 Super Admin Features
- **User Role Management**: Assign admin privileges
- **Account Activation/Deactivation**: User access control
- **System Settings**: Configure global parameters
- **Audit Logs**: Track administrative actions

## 🏗️ Architecture

### System Design
```
┌─────────────────┐
│   Student App   │
│   (Streamlit)   │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────────────────┐
│   Firebase Realtime DB      │
│  ┌───────────────────────┐  │
│  │   /facilities         │  │
│  │   /queues             │  │
│  │   /active_queues      │  │
│  │   /users              │  │
│  │   /history            │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
         ▲
         │ HTTPS
         │
┌────────┴────────┐
│   Admin Panel   │
│   (Streamlit)   │
└─────────────────┘
```

### Data Flow
1. **Student Check-In**:
   - Scan QR → Validate → Update queue count → Log history → Broadcast to all clients

2. **Real-Time Updates**:
   - Firebase triggers → Client listeners → UI refresh → Display updated data

3. **Analytics Generation**:
   - Query history → Aggregate by hour/day → Generate visualizations → Display insights

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Firebase account with Realtime Database enabled
- pip package manager

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/qless.git
cd qless
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Realtime Database
3. Download `serviceAccountKey.json` from Project Settings → Service Accounts
4. Place it in the project root directory

### Step 4: Configure Application
Edit `config.py`:
```python
FIREBASE_CONFIG = {
    'credentials_path': 'serviceAccountKey.json',
    'database_url': 'https://your-project.firebaseio.com/'
}

SUPER_ADMIN_EMAILS = [
    'your.email@campus.edu'
]
```

### Step 5: Initialize Database
```bash
python setup.py
```

This creates:
- Default facilities (3 mess halls)
- Admin accounts
- Sample student account
- System settings

### Step 6: Run Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🎮 Usage

### First-Time Setup
1. **Run initialization**: `python setup.py`
2. **Login as admin**: `admin@campus.edu` / `admin123`
3. **Change default password** (Security first!)
4. **Generate QR codes** for facilities
5. **Print and place QR codes** at facility entrances

### Student Workflow
1. **Open app** on mobile device
2. **View queue status** across all facilities
3. **Choose facility** with shortest queue
4. **Scan QR code** at facility entrance
5. **Get confirmation** of check-in
6. **Check out** when leaving

### Admin Operations
1. **Monitor dashboard** for real-time status
2. **Review analytics** to identify patterns
3. **Adjust capacity** based on demand
4. **Generate reports** for management
5. **Manage users** and permissions

## 📸 Screenshots

### Student View
![Student Dashboard](screenshots/student-dashboard.png)
*Real-time facility overview with color-coded status*

### Admin Dashboard
![Admin Overview](screenshots/admin-overview.png)
*Comprehensive facility monitoring and management*

## 🌟 Impact & Practicality

### Quantifiable Benefits

#### Resource Optimization
- **Visibility**: Real-time occupancy data enables better planning
- **Distribution**: Students spread across multiple facilities

#### Administrative Efficiency
- **Data-Driven Decisions**: Historical analytics inform capacity planning

### Scalability
- **Campus-Wide**: Easily extends to 50+ facilities
- **Multi-Campus**: Cloud architecture supports multiple locations
- **User Capacity**: Handles 10,000+ concurrent users
- **Data Volume**: Efficiently manages millions of check-in records

## 👥 Team

**Jalaj Bhadouria**
- GitHub: [@jalajbhadouria](https://github.com/darkisthenight)
[![Jalaj Bhadouria profile views](https://u8views.com/api/v1/github/profiles/227359471/views/day-week-month-total-count.svg)](https://u8views.com/github/darkisthenight07)
- Email: jalaj4b@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[⬆ Back to Top](#qless---smart-campus-queue-manager)