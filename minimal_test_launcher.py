"""
Minimal test launcher to verify executable creation works
"""
import os
import sys
from pathlib import Path

def main():
    """Minimal test main function"""
    current_dir = Path(__file__).parent.absolute()
    
    # Create a simple test file
    test_file = current_dir / "minimal_test.txt"
    with open(test_file, 'w') as f:
        f.write("Minimal test executable launched successfully!\n")
        f.write(f"Current directory: {current_dir}\n")
        f.write(f"Executable: {sys.executable}\n")
        f.write(f"Arguments: {sys.argv}\n")
        f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
    
    print("Minimal test completed - check minimal_test.txt")

if __name__ == "__main__":
    main()