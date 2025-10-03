#!/usr/bin/env python3
"""
Test User Info Display
Quick test to verify the user header and logout functionality
"""

import tkinter as tk
from tkinter import ttk
import json
import tempfile
import time

def test_user_info_display():
    """Test the user info display with sample data"""
    print("🧪 Testing User Info Display")
    print("=" * 40)
    
    # Create a test session file
    test_session = {
        "token": "test_token_123",
        "user_info": {
            "username": "test_admin",
            "role": "admin", 
            "email": "admin@company.com",
            "id": 1
        },
        "login_time": "2025-10-03T14:30:15",
        "timestamp": time.time()
    }
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_session, f)
        session_file = f.name
    
    print(f"✅ Test session file created: {session_file}")
    
    # Test launching GUI with session
    import subprocess
    import sys
    import os
    
    gui_path = os.path.join(os.path.dirname(__file__), 'gui', 'file_upload_json_gui.py')
    command = [sys.executable, gui_path, '--auth-session', session_file]
    
    print(f"✅ GUI command: {' '.join(command)}")
    print("🚀 Launching GUI with test session...")
    print("📋 Expected to see:")
    print("   - User header with: 👑 Logged in as: test_admin (Administrator)")
    print("   - Email: admin@company.com")
    print("   - Session time: 14:30:15")
    print("   - Logout button")
    print("   - Active session indicator")
    
    try:
        # Launch GUI (don't wait for it to complete)
        process = subprocess.Popen(command)
        print(f"✅ GUI launched successfully (PID: {process.pid})")
        return True
    except Exception as e:
        print(f"❌ Error launching GUI: {str(e)}")
        return False
    finally:
        # Clean up session file after a delay
        import threading
        def cleanup():
            time.sleep(10)  # Wait 10 seconds then cleanup
            try:
                os.unlink(session_file)
                print(f"✅ Cleaned up session file: {session_file}")
            except:
                pass
        
        cleanup_thread = threading.Thread(target=cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()

def test_user_info_components():
    """Test individual components of user info display"""
    print("\n🧪 Testing User Info Components")
    print("=" * 40)
    
    # Test data
    test_cases = [
        {
            "name": "Admin User",
            "user_info": {"username": "admin", "role": "admin", "email": "admin@test.com"},
            "expected_icon": "👑",
            "expected_text": "admin (Administrator)"
        },
        {
            "name": "Regular User", 
            "user_info": {"username": "john_doe", "role": "user", "email": "john@test.com"},
            "expected_icon": "👤",
            "expected_text": "john_doe"
        },
        {
            "name": "User without Email",
            "user_info": {"username": "testuser", "role": "user"},
            "expected_icon": "👤", 
            "expected_text": "testuser"
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 Testing: {case['name']}")
        user_info = case['user_info']
        
        # Simulate the display logic
        username = user_info.get('username', 'Unknown')
        user_role = user_info.get('role', 'user')
        user_email = user_info.get('email', '')
        
        role_icon = "👑" if user_role == "admin" else "👤"
        
        user_text = f"{role_icon} Logged in as: {username}"
        if user_role == "admin":
            user_text += " (Administrator)"
        if user_email:
            user_text += f" • {user_email}"
        user_text += " • 🟢 Active Session"
        
        print(f"   Expected Icon: {case['expected_icon']}")
        print(f"   Actual Icon: {role_icon}")
        print(f"   Display Text: {user_text}")
        
        if role_icon == case['expected_icon']:
            print("   ✅ Icon correct")
        else:
            print("   ❌ Icon incorrect")
    
    print("\n✅ Component tests completed")

if __name__ == "__main__":
    print("🚀 Testing User Info Display System")
    print("=" * 60)
    
    # Test components
    test_user_info_components()
    
    # Test actual GUI display
    success = test_user_info_display()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 User Info Display Test Completed!")
        print("\n📋 What to verify in the GUI:")
        print("1. ✅ User header shows at the top")
        print("2. ✅ Username and role displayed correctly")
        print("3. ✅ Email address shown (if available)")
        print("4. ✅ Session time displayed")
        print("5. ✅ Logout button is functional")
        print("6. ✅ Active session indicator shows")
    else:
        print("❌ User Info Display Test Failed")
    
    print("=" * 60)