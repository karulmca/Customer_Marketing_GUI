"""
User Authentication System
Handles user login, authentication, and session management with PostgreSQL
"""

import hashlib
import bcrypt
import os
import sys
from typing import Optional, Dict, Any
import secrets
from datetime import datetime, timedelta

# Add project paths for database access
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
database_config_path = os.path.join(parent_dir, 'database_config')
if database_config_path not in sys.path:
    sys.path.insert(0, database_config_path)

from db_utils import get_database_connection
import psycopg2
from psycopg2.extras import RealDictCursor

class UserAuthenticator:
    def register_user(self, username: str, password: str, email: str = None, role: str = "user") -> Dict[str, Any]:
        """Register a new user (alias for create_user)"""
        return self.create_user(username, password, email, role)
    """Handles user authentication and session management with PostgreSQL"""
    
    def __init__(self):
        """Initialize the authenticator with PostgreSQL connection"""
        self.session_timeout = 3600  # 1 hour in seconds
        self.active_sessions = {}  # In-memory session storage
        
        # Initialize PostgreSQL connection
        self.db_connection = get_database_connection("postgresql")
        if not self.db_connection:
            raise Exception("Could not initialize database connection")
        
        # Initialize database tables
        self._init_database()
        self._create_default_users()
    
    def _init_database(self):
        """Initialize the user database tables in PostgreSQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create login attempts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    ip_address VARCHAR(45),
                    success BOOLEAN NOT NULL,
                    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ User authentication tables created successfully in PostgreSQL")
            
        except Exception as e:
            print(f"❌ Error initializing user database: {str(e)}")
    
    def _get_connection(self):
        """Get PostgreSQL database connection"""
        try:
            if self.db_connection and self.db_connection.manager:
                # Get connection parameters from the config
                params = self.db_connection.manager.config.get_connection_params()
                return psycopg2.connect(**params)
            else:
                raise Exception("Database connection not initialized")
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            raise
    
    def _create_default_users(self):
        """Create default users if no users exist"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # Create default admin user
                admin_password = "admin123"  # Change this in production!
                admin_hash = self._hash_password(admin_password)
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, role)
                    VALUES (%s, %s, %s, %s)
                """, ("admin", admin_hash, "admin@company.com", "admin"))
                
                # Create default regular user
                user_password = "user123"
                user_hash = self._hash_password(user_password)
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, role)
                    VALUES (%s, %s, %s, %s)
                """, ("user", user_hash, "user@company.com", "user"))
                
                conn.commit()
                cursor.close()
                conn.close()
                print("🔐 Default users created:")
                print("   Admin: username='admin', password='admin123'")
                print("   User: username='user', password='user123'")
                print("⚠️  Please change default passwords in production!")
                
        except Exception as e:
            print(f"❌ Error creating default users: {str(e)}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored bcrypt hash"""
        try:
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = stored_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, stored_hash_bytes)
        except Exception:
            return False
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Authenticate user credentials
        Returns: Dict with success status, user info, and session token
        """
        result = {
            "success": False,
            "message": "",
            "user": None,
            "session_token": None
        }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get user from database
            cursor.execute("""
                SELECT id, username, password_hash, email, role, is_active
                FROM users 
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            
            user_data = cursor.fetchone()
            
            if user_data and self._verify_password(password, user_data['password_hash']):
                # Successful authentication
                user_id = user_data['id']
                
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (user_id,))
                
                # Create session token
                session_token = secrets.token_urlsafe(32)
                session_data = {
                    "user_id": user_id,
                    "username": user_data['username'],
                    "email": user_data['email'],
                    "role": user_data['role'],
                    "login_time": datetime.now(),
                    "expires_at": datetime.now() + timedelta(seconds=self.session_timeout)
                }
                
                self.active_sessions[session_token] = session_data
                
                # Log successful attempt
                cursor.execute("""
                    INSERT INTO login_attempts (username, ip_address, success)
                    VALUES (%s, %s, %s)
                """, (username, ip_address, True))
                
                result.update({
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "id": user_id,
                        "username": user_data['username'],
                        "email": user_data['email'],
                        "role": user_data['role']
                    },
                    "session_token": session_token
                })
                
            else:
                # Failed authentication
                cursor.execute("""
                    INSERT INTO login_attempts (username, ip_address, success)
                    VALUES (%s, %s, %s)
                """, (username, ip_address, False))
                
                result["message"] = "Invalid username or password"
            
            conn.commit()
            cursor.close()
            conn.close()
                
        except Exception as e:
            result["message"] = f"Authentication error: {str(e)}"
        
        return result
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate session token and return user info"""
        if not session_token or session_token not in self.active_sessions:
            return {"valid": False, "message": "Invalid session"}
        
        session_data = self.active_sessions[session_token]
        
        # Check if session expired
        if datetime.now() > session_data["expires_at"]:
            del self.active_sessions[session_token]
            return {"valid": False, "message": "Session expired"}
        
        # Extend session
        session_data["expires_at"] = datetime.now() + timedelta(seconds=self.session_timeout)
        
        return {
            "valid": True,
            "user": {
                "id": session_data["user_id"],
                "username": session_data["username"],
                "email": session_data["email"],
                "role": session_data["role"]
            }
        }
    
    def logout(self, session_token: str) -> bool:
        """Logout user by removing session"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False
    
    def create_user(self, username: str, password: str, email: str = None, role: str = "user") -> Dict[str, Any]:
        """Create new user account"""
        result = {"success": False, "message": ""}
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                result["message"] = "Username already exists"
                cursor.close()
                conn.close()
                return result
            
            # Create user
            password_hash = self._hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role)
                VALUES (%s, %s, %s, %s)
            """, (username, password_hash, email, role))
            
            conn.commit()
            cursor.close()
            conn.close()
            result.update({
                "success": True,
                "message": "User created successfully"
            })
            
        except Exception as e:
            result["message"] = f"Error creating user: {str(e)}"
        
        return result
    
    def get_login_attempts(self, limit: int = 10) -> list:
        """Get recent login attempts for monitoring"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT username, ip_address, success, attempt_time
                FROM login_attempts 
                ORDER BY attempt_time DESC 
                LIMIT %s
            """, (limit,))
            
            attempts = []
            for row in cursor.fetchall():
                attempts.append({
                    "username": row['username'],
                    "ip_address": row['ip_address'],
                    "success": bool(row['success']),
                    "attempt_time": row['attempt_time']
                })
            
            cursor.close()
            conn.close()
            return attempts
            
        except Exception as e:
            print(f"❌ Error getting login attempts: {str(e)}")
            return []
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_tokens = [
            token for token, data in self.active_sessions.items()
            if current_time > data["expires_at"]
        ]
        
        for token in expired_tokens:
            del self.active_sessions[token]
        
        return len(expired_tokens)

# Global authenticator instance
auth_manager = UserAuthenticator()