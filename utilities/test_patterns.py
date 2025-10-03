#!/usr/bin/env python3
"""
Test LinkedIn Pattern Matching for Exact Format
"""

import re

def test_patterns():
    """Test the patterns with sample LinkedIn content"""
    
    # Sample LinkedIn content (similar to your screenshot)
    sample_content = """
    Website http://www.2plan.com
    Industry Financial Services
    Company size 201-500 employees
    Headquarters Leeds
    Type Privately Held
    Specialties Financial Planning, Wealth Management
    """
    
    # Patterns in order of priority
    patterns = [
        # LinkedIn's standard range categories (HIGHEST PRIORITY)
        r'(1-10|11-50|51-200|201-500|501-1,000|1,001-5,000|5,001-10,000|10,001\+)\s+employees?',
        r'(1-10|11-50|51-200|201-500|501-1000|1001-5000|5001-10000|10000\+)\s+employees?',
        
        # General range patterns
        r'(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?',
        r'(\d+-\d+)\s+employees?',
        r'(\d+\+)\s+employees?',
        
        # Company size section specific
        r'Company size[:\s]*(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?',
        r'Company size[:\s]*(1-10|11-50|51-200|201-500|501-1000|1001-5000|5001-10000|10000\+)\s+employees?',
        
        # Fallback patterns (lower priority)
        r'(\d+(?:,\d+)?)\s+employees?',
        r'(\d+(?:,\d+)?)\s+associates?',
        r'Employees?[:\s]*(\d+(?:,\d+)?)',
    ]
    
    print("🔍 TESTING LINKEDIN PATTERN MATCHING")
    print("=" * 50)
    print("Sample content:")
    print(sample_content)
    print("\n" + "=" * 50)
    print("Testing patterns in priority order:")
    print("=" * 50)
    
    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, sample_content, re.IGNORECASE)
        if matches:
            result = matches[0].strip()
            if 'employees' not in result.lower():
                result = f"{result} employees"
            print(f"✅ Pattern {i}: Found '{result}'")
            print(f"   Regex: {pattern}")
            break
        else:
            print(f"❌ Pattern {i}: No match")
            print(f"   Regex: {pattern}")
    
    print("\n" + "=" * 50)
    print("Expected result: '201-500 employees'")
    print("=" * 50)

if __name__ == "__main__":
    test_patterns()