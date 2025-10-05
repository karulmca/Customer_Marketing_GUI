#!/usr/bin/env python3
"""
Database Cleanup Script - Drop Unused Tables
Safely removes tables that have no data and are not actively used
"""

import sys
import os
from datetime import datetime
from database_config.postgresql_config import PostgreSQLConfig
import psycopg2

def get_table_analysis():
    """Analyze all tables for usage"""
    config = PostgreSQLConfig()
    params = config.get_connection_params()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    all_tables = [row[0] for row in cursor.fetchall()]
    
    table_analysis = {}
    
    for table in all_tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            table_analysis[table] = {
                'row_count': count,
                'status': 'USED' if count > 0 else 'EMPTY'
            }
        except Exception as e:
            table_analysis[table] = {
                'row_count': 0,
                'status': f'ERROR: {str(e)}',
                'error': True
            }
    
    cursor.close()
    conn.close()
    return table_analysis

def identify_unused_tables():
    """Identify tables that can be safely dropped"""
    
    # Tables that are actively used (have data or are essential)
    ESSENTIAL_TABLES = {
        'users',           # Authentication system
        'user_sessions',   # Session management (even if empty, needed for auth)
        'login_attempts',  # Security logging
        'file_upload',     # File storage system
        'company_data',    # Main data storage
        'processing_jobs'  # Job management
    }
    
    # Tables that are candidates for removal (empty and not essential)
    CANDIDATE_TABLES = {
        'api_usage': 'API usage tracking - empty and not currently used',
        'companies': 'Duplicate/alternative company storage - empty',
        'company_results': 'Processing results - empty, functionality moved to file_upload',
        'excel_files': 'Legacy Excel file tracking - empty, replaced by file_upload',
        'processing_logs': 'Detailed processing logs - empty, not actively used',
        'upload_history': 'Legacy upload tracking - empty, replaced by file_upload'
    }
    
    analysis = get_table_analysis()
    
    tables_to_drop = []
    tables_to_keep = []
    
    for table_name, info in analysis.items():
        if table_name in ESSENTIAL_TABLES:
            tables_to_keep.append({
                'name': table_name,
                'reason': 'Essential for system operation',
                'row_count': info['row_count']
            })
        elif table_name in CANDIDATE_TABLES:
            if info['status'] == 'EMPTY':
                tables_to_drop.append({
                    'name': table_name,
                    'reason': CANDIDATE_TABLES[table_name],
                    'row_count': info['row_count']
                })
            else:
                tables_to_keep.append({
                    'name': table_name,
                    'reason': f'Has data ({info["row_count"]} rows)',
                    'row_count': info['row_count']
                })
        else:
            # Unknown table - keep it safe
            tables_to_keep.append({
                'name': table_name,
                'reason': 'Unknown table - keeping for safety',
                'row_count': info['row_count']
            })
    
    return tables_to_drop, tables_to_keep

def create_backup_script(tables_to_drop):
    """Create a backup script to recreate dropped tables if needed"""
    backup_script = f"""-- Database Table Restoration Script
-- Generated on: {datetime.now().isoformat()}
-- 
-- This script can recreate the tables that were dropped by cleanup_unused_tables.py
-- Only run this if you need to restore the dropped tables

"""
    
    config = PostgreSQLConfig()
    params = config.get_connection_params()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    for table in tables_to_drop:
        table_name = table['name']
        try:
            # Get table schema
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            if columns:
                backup_script += f"-- Recreate {table_name} table\\n"
                backup_script += f"CREATE TABLE IF NOT EXISTS {table_name} (\\n"
                
                column_defs = []
                for col_name, data_type, is_nullable, default in columns:
                    col_def = f"    {col_name} {data_type.upper()}"
                    if is_nullable == 'NO':
                        col_def += " NOT NULL"
                    if default:
                        col_def += f" DEFAULT {default}"
                    column_defs.append(col_def)
                
                backup_script += ",\\n".join(column_defs)
                backup_script += "\\n);\\n\\n"
        
        except Exception as e:
            backup_script += f"-- ERROR getting schema for {table_name}: {str(e)}\\n\\n"
    
    cursor.close()
    conn.close()
    
    # Save backup script
    backup_file = f"restore_dropped_tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    with open(backup_file, 'w') as f:
        f.write(backup_script)
    
    print(f"📄 Backup restoration script created: {backup_file}")
    return backup_file

def drop_unused_tables(tables_to_drop, confirm=False):
    """Drop the unused tables"""
    if not tables_to_drop:
        print("✅ No unused tables found to drop.")
        return
    
    if not confirm:
        print("⚠️  DRY RUN MODE - No tables will be dropped")
        print("   Add --confirm flag to actually drop tables")
        print()
    
    print(f"📋 Tables to be dropped ({len(tables_to_drop)}):")
    for table in tables_to_drop:
        status = "WILL DROP" if confirm else "WOULD DROP"
        print(f"   🗑️  {table['name']} - {table['reason']} [{status}]")
    
    if not confirm:
        return
    
    # Create backup script first
    backup_file = create_backup_script(tables_to_drop)
    
    # Drop tables
    config = PostgreSQLConfig()
    params = config.get_connection_params()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    dropped_count = 0
    errors = []
    
    for table in tables_to_drop:
        table_name = table['name']
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            conn.commit()
            print(f"✅ Dropped table: {table_name}")
            dropped_count += 1
            
        except Exception as e:
            error_msg = f"❌ Error dropping {table_name}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"\\n📊 Summary:")
    print(f"   ✅ Successfully dropped: {dropped_count} tables")
    if errors:
        print(f"   ❌ Errors: {len(errors)}")
        for error in errors:
            print(f"      {error}")
    print(f"   📄 Backup script: {backup_file}")

def main():
    print("🧹 Database Cleanup - Unused Table Analysis")
    print("=" * 60)
    
    # Analyze tables
    tables_to_drop, tables_to_keep = identify_unused_tables()
    
    print(f"\\n📊 Analysis Results:")
    print(f"   🗑️  Tables to drop: {len(tables_to_drop)}")
    print(f"   ✅ Tables to keep: {len(tables_to_keep)}")
    
    print(f"\\n🔒 Tables to KEEP ({len(tables_to_keep)}):")
    for table in tables_to_keep:
        print(f"   ✅ {table['name']} ({table['row_count']} rows) - {table['reason']}")
    
    print(f"\\n🗑️  Tables to DROP ({len(tables_to_drop)}):")
    for table in tables_to_drop:
        print(f"   ❌ {table['name']} ({table['row_count']} rows) - {table['reason']}")
    
    # Check command line arguments
    confirm = '--confirm' in sys.argv
    
    print("\\n" + "=" * 60)
    drop_unused_tables(tables_to_drop, confirm=confirm)
    
    if not confirm and tables_to_drop:
        print("\\n💡 To actually drop the tables, run:")
        print("   python cleanup_unused_tables.py --confirm")

if __name__ == "__main__":
    main()