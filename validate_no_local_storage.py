#!/usr/bin/env python3
"""
Validation script to verify NO LOCAL STORAGE is being used
"""

import os
import sys
import tempfile
import time
from pathlib import Path

def scan_for_temp_files():
    """Check if any temporary files are created during processing"""
    
    temp_dirs = [
        tempfile.gettempdir(),
        "C:\\temp",
        "C:\\tmp",
        os.path.join(os.getcwd(), "temp"),
        os.path.join(os.getcwd(), "tmp"),
    ]
    
    print("🔍 Scanning for temporary file creation...")
    print("=" * 60)
    
    # Get initial state
    initial_files = {}
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                files = list(Path(temp_dir).glob("**/*"))
                initial_files[temp_dir] = set(str(f) for f in files if f.is_file())
                print(f"📁 {temp_dir}: {len(initial_files[temp_dir])} existing files")
            except PermissionError:
                print(f"⚠️  {temp_dir}: Permission denied")
                initial_files[temp_dir] = set()
        else:
            print(f"❌ {temp_dir}: Directory doesn't exist")
            initial_files[temp_dir] = set()
    
    print(f"\n⏱️  Monitoring for 30 seconds...")
    print("   (Run file upload/processing during this time)")
    
    # Monitor for changes
    for i in range(30):
        time.sleep(1)
        print(f"   Monitoring... {i+1}/30 seconds", end='\r')
    
    print("\n")
    
    # Check final state
    temp_files_created = []
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                files = list(Path(temp_dir).glob("**/*"))
                current_files = set(str(f) for f in files if f.is_file())
                new_files = current_files - initial_files[temp_dir]
                
                if new_files:
                    print(f"⚠️  NEW FILES in {temp_dir}:")
                    for new_file in new_files:
                        print(f"     - {new_file}")
                        temp_files_created.append(new_file)
                else:
                    print(f"✅ {temp_dir}: No new files created")
            except PermissionError:
                print(f"⚠️  {temp_dir}: Permission denied for final check")
    
    print("\n" + "=" * 60)
    
    if temp_files_created:
        print(f"❌ VALIDATION FAILED: {len(temp_files_created)} temporary files were created!")
        print("   The system is still using local storage.")
        return False
    else:
        print("✅ VALIDATION PASSED: No temporary files were created!")
        print("   The system is operating without local storage.")
        return True

def check_code_for_temp_usage():
    """Check code for potential temporary file usage"""
    
    print("\n🔍 Checking code for temporary file usage patterns...")
    print("=" * 60)
    
    suspicious_patterns = [
        "tempfile.gettempdir()",
        "tempfile.mktemp",
        "tempfile.NamedTemporaryFile",
        "tempfile.TemporaryDirectory",
        "/tmp/",
        "C:\\\\temp",
        "open(.*\\.xlsx",
        "to_excel.*file",
        "file_path.*temp"
    ]
    
    files_to_check = [
        "backend_api/main.py",
        "backend_api/company_processor.py"
    ]
    
    issues_found = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"📄 Checking {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in suspicious_patterns:
                        if pattern.lower() in line.lower() and not line.strip().startswith('#'):
                            issues_found.append({
                                'file': file_path,
                                'line': i,
                                'content': line.strip(),
                                'pattern': pattern
                            })
    
    if issues_found:
        print(f"\n⚠️  Found {len(issues_found)} potential temporary file usage patterns:")
        for issue in issues_found:
            print(f"   📄 {issue['file']}:{issue['line']}")
            print(f"      Pattern: {issue['pattern']}")
            print(f"      Code: {issue['content']}")
            print()
    else:
        print("✅ No suspicious temporary file patterns found in code.")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    print("🚀 NO LOCAL STORAGE VALIDATION")
    print("=" * 60)
    print("This script validates that the system operates without local storage.")
    print("Start file upload/processing in another terminal during the monitoring period.")
    print()
    
    # Check code first
    code_clean = check_code_for_temp_usage()
    
    # Monitor temp file creation
    runtime_clean = scan_for_temp_files()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL VALIDATION RESULTS:")
    print(f"   Code Analysis: {'✅ PASSED' if code_clean else '❌ FAILED'}")
    print(f"   Runtime Check: {'✅ PASSED' if runtime_clean else '❌ FAILED'}")
    
    if code_clean and runtime_clean:
        print("\n🎉 SUCCESS: System operates without local storage!")
    else:
        print("\n❌ FAILED: System still uses local storage. Review and fix issues above.")