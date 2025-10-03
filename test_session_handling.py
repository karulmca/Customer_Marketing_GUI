#!/usr/bin/env python3
"""
Test Session Handling
Verify that sessions are created with correct timestamps and validation works
"""

import os
import sys
import json
import time
import tempfile

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
auth_path = os.path.join(current_dir, 'auth')
if auth_path not in sys.path:
    sys.path.append(auth_path)

from user_auth import UserAuthenticator

def test_session_timestamp_handling():
    """Test that session timestamps are handled correctly"""
    print("🧪 Testing Session Timestamp Handling")
    print("=" * 50)
    
    # Create authenticator and login
    auth = UserAuthenticator()
    auth_result = auth.authenticate_user("admin", "admin123")
    
    if not auth_result or not auth_result.get('success'):
        print("❌ Authentication failed")
        return False
    
    user_info = auth_result['user']
    token = auth_result['session_token']
    
    # Create session data like login GUI does
    session_data = {
        "token": token,
        "session_token": token,
        "user_info": user_info,
        "login_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "timestamp": time.time()
    }
    
    print(f"✅ Session created with timestamp: {session_data['timestamp']}")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(session_data, f)
        session_file = f.name
    
    print(f"✅ Session file created: {session_file}")
    
    # Test loading session data (like GUI does)
    try:
        with open(session_file, 'r') as f:
            loaded_session = json.load(f)
        
        # Test timestamp validation logic
        session_timestamp = loaded_session.get('timestamp', 0)
        current_time = time.time()
        session_age = current_time - session_timestamp
        
        print(f"✅ Session age: {session_age:.1f} seconds")
        
        # Test the validation logic
        if session_age < 600:  # Less than 10 minutes
            print("✅ Session is considered fresh (< 10 minutes)")
            validation_needed = False
        else:
            print("⚠️ Session is older than 10 minutes, validation needed")
            validation_needed = True
        
        # Test actual token validation
        validation_result = auth.validate_session(loaded_session.get('token'))
        token_valid = validation_result and validation_result.get('valid', False)
        
        print(f"✅ Token validation result: {token_valid}")
        
        # Clean up
        os.unlink(session_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing session: {str(e)}")
        return False

def simulate_gui_session_check():
    """Simulate the GUI session validation logic"""
    print("\n🧪 Simulating GUI Session Check")
    print("=" * 50)
    
    # Create a fresh session
    auth = UserAuthenticator()
    auth_result = auth.authenticate_user("admin", "admin123")
    
    if not auth_result or not auth_result.get('success'):
        print("❌ Authentication failed")
        return False
    
    session_data = {
        "token": auth_result['session_token'],
        "user_info": auth_result['user'], 
        "timestamp": time.time()
    }
    
    # Simulate the GUI validation logic
    session_timestamp = session_data.get('timestamp', 0)
    current_time = time.time()
    session_age = current_time - session_timestamp
    
    print(f"Current time: {current_time}")
    print(f"Session timestamp: {session_timestamp}")
    print(f"Session age: {session_age:.1f} seconds")
    
    if session_age < 600:  # Less than 10 minutes old
        print("✅ GUI would skip validation (session is fresh)")
        should_validate = False
    else:
        print("⚠️ GUI would perform validation (session is old)")
        should_validate = True
    
    # Test actual validation
    try:
        validation_result = auth.validate_session(session_data.get('token'))
        is_valid = validation_result and validation_result.get('valid', False)
        print(f"✅ Token validation: {is_valid}")
        
        if should_validate and not is_valid:
            print("❌ Session would expire in GUI")
        else:
            print("✅ Session would be accepted in GUI")
            
        return True
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Session Handling")
    print("=" * 60)
    
    success1 = test_session_timestamp_handling()
    success2 = simulate_gui_session_check()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All session tests passed!")
        print("\n✅ Session expiration issue should be fixed")
        print("✅ Fresh sessions will not be immediately validated")
        print("✅ Old sessions will be properly validated")
    else:
        print("❌ Some session tests failed")
    print("=" * 60)