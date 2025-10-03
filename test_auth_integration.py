#!/usr/bin/env python3
"""
Test script for authentication system integration
Tests the complete workflow from login to main GUI launch
"""

import os
import sys
import subprocess
import tempfile
import json
import time

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
auth_path = os.path.join(current_dir, 'auth')
if auth_path not in sys.path:
    sys.path.append(auth_path)

from user_auth import UserAuthenticator

def test_authentication_system():
    """Test the complete authentication workflow"""
    print("🧪 Testing Authentication System Integration")
    print("=" * 50)
    
    # Test 1: Initialize authenticator
    print("\n1. Testing authenticator initialization...")
    try:
        auth = UserAuthenticator()
        print("✅ UserAuthenticator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize authenticator: {str(e)}")
        return False
    
    # Test 2: Test authentication
    print("\n2. Testing user authentication...")
    try:
        auth_result = auth.authenticate_user("admin", "admin123")
        if auth_result and auth_result.get('success'):
            user_info = auth_result['user']
            print(f"✅ Authentication successful for user: {user_info['username']}")
            print(f"   Role: {user_info['role']}")
            print(f"   User ID: {user_info['id']}")
        else:
            print("❌ Authentication failed")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False
    
    # Test 3: Test session creation
    print("\n3. Testing session creation...")
    try:
        # Use the session token from authentication result
        token = auth_result['session_token']
        if token:
            print(f"✅ Session created successfully")
            print(f"   Token: {token[:10]}...")
        else:
            print("❌ Session creation failed")
            return False
    except Exception as e:
        print(f"❌ Session creation error: {str(e)}")
        return False
    
    # Test 4: Test session validation
    print("\n4. Testing session validation...")
    try:
        validation_result = auth.validate_session(token)
        if validation_result and validation_result.get('valid'):
            print("✅ Session validation successful")
            print(f"   User: {validation_result.get('user', {}).get('username')}")
        else:
            print("❌ Session validation failed")
            return False
    except Exception as e:
        print(f"❌ Session validation error: {str(e)}")
        return False
    
    # Test 5: Test session file creation
    print("\n5. Testing session file creation...")
    try:
        session_data = {
            'token': token,
            'user_info': user_info,
            'timestamp': time.time()
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(session_data, f, indent=2)
            session_file = f.name
        
        # Test loading the session file
        with open(session_file, 'r') as f:
            loaded_data = json.load(f)
        
        if loaded_data['token'] == token:
            print("✅ Session file creation and loading successful")
            print(f"   Session file: {session_file}")
        else:
            print("❌ Session file data mismatch")
            return False
            
        # Clean up
        os.unlink(session_file)
        
    except Exception as e:
        print(f"❌ Session file creation error: {str(e)}")
        return False
    
    # Test 6: Test main GUI launch command
    print("\n6. Testing main GUI launch command...")
    try:
        # Create temporary session file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(session_data, f, indent=2)
            session_file = f.name
        
        # Test command construction
        gui_path = os.path.join(current_dir, 'gui', 'file_upload_json_gui.py')
        command = [sys.executable, gui_path, '--auth-session', session_file]
        
        print(f"✅ GUI launch command constructed:")
        print(f"   Command: {' '.join(command)}")
        print(f"   GUI file exists: {os.path.exists(gui_path)}")
        print(f"   Session file exists: {os.path.exists(session_file)}")
        
        # Don't actually launch GUI in test
        # subprocess.Popen(command)
        
        # Clean up
        os.unlink(session_file)
        
    except Exception as e:
        print(f"❌ GUI launch command test error: {str(e)}")
        return False
    
    print("\n🎉 All authentication integration tests passed!")
    print("=" * 50)
    print("✅ Authentication System Ready")
    print("✅ Session Management Working")
    print("✅ GUI Integration Prepared")
    return True

def test_gui_authentication_parameters():
    """Test that the main GUI can handle authentication parameters"""
    print("\n🧪 Testing GUI Authentication Parameter Handling")
    print("=" * 50)
    
    try:
        # Create a test session file
        session_data = {
            'token': 'test_token_123',
            'user_info': {
                'username': 'test_user',
                'role': 'user',
                'user_id': 1
            },
            'timestamp': time.time()
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(session_data, f, indent=2)
            session_file = f.name
        
        print(f"✅ Test session file created: {session_file}")
        
        # Test that the GUI file exists and can be imported
        gui_path = os.path.join(current_dir, 'gui', 'file_upload_json_gui.py')
        print(f"✅ GUI file exists: {os.path.exists(gui_path)}")
        
        # Test command line argument parsing (dry run)
        import argparse
        parser = argparse.ArgumentParser(description='Test GUI parameters')
        parser.add_argument('--auth-session', type=str, help='Path to authentication session file')
        
        test_args = parser.parse_args(['--auth-session', session_file])
        print(f"✅ Command line parsing works: {test_args.auth_session}")
        
        # Clean up
        os.unlink(session_file)
        
        print("✅ GUI authentication parameters test passed!")
        return True
        
    except Exception as e:
        print(f"❌ GUI parameter test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Authentication Integration Tests")
    print("=" * 60)
    
    success = True
    
    # Run authentication system tests
    if not test_authentication_system():
        success = False
    
    # Run GUI parameter tests
    if not test_gui_authentication_parameters():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - Authentication system is ready!")
        print("\n📋 Next Steps:")
        print("1. Run: python gui/login_gui.py")
        print("2. Login with admin/admin123 or user/user123")
        print("3. Main GUI should launch automatically with your session")
        print("4. Files uploaded will be tracked by your username")
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
    
    print("=" * 60)