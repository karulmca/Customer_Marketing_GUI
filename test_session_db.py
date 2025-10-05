#!/usr/bin/env python3
"""
Test script to check session database persistence
"""

from database_config.postgresql_config import PostgreSQLConfig
import psycopg2
import json

def check_sessions():
    """Check existing sessions in database"""
    try:
        print("🔍 Checking sessions in database...")
        
        db_config = PostgreSQLConfig()
        connection = psycopg2.connect(**db_config.get_connection_params())
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT session_id, session_data, created_at 
            FROM user_sessions 
            ORDER BY created_at DESC
        """)
        sessions = cursor.fetchall()
        
        print(f"📊 Found {len(sessions)} sessions in database:")
        for session_id, session_data, created_at in sessions:
            try:
                data = json.loads(session_data)
                username = data.get('user_info', {}).get('username', 'unknown')
                print(f"  - {session_id[:8]}... | User: {username} | Created: {created_at}")
            except:
                print(f"  - {session_id[:8]}... | Invalid data | Created: {created_at}")
        
        cursor.close()
        connection.close()
        print("✅ Database check complete")
        return sessions
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

if __name__ == "__main__":
    check_sessions()