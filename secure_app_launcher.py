"""
Company Data Scraper - Secure Application Launcher
Main entry point with authentication
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import sqlite3
    except ImportError:
        missing_deps.append("sqlite3")
    
    try:
        import hashlib
    except ImportError:
        missing_deps.append("hashlib")
    
    try:
        import secrets
    except ImportError:
        missing_deps.append("secrets")
    
    return missing_deps

def create_directories():
    """Create required directories"""
    directories = [
        "auth",
        "assets",
        "logs",
        "results"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main application entry point"""
    try:
        print("🚀 Starting Company Data Scraper...")
        print("=" * 50)
        
        # Check dependencies
        missing_deps = check_dependencies()
        if missing_deps:
            error_msg = f"Missing required dependencies: {', '.join(missing_deps)}"
            print(f"❌ {error_msg}")
            
            # Show error dialog
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Dependency Error", 
                               f"{error_msg}\\n\\nPlease install the required dependencies.")
            return
        
        # Create required directories
        create_directories()
        print("📁 Required directories created/verified")
        
        # Import and start login application
        from gui.login_gui import LoginWindow
        
        print("🔐 Launching secure login interface...")
        print("📋 Default credentials: admin / admin123")
        print("⚠️  Change default password in production!")
        print("=" * 50)
        
        # Create and run login application
        login_app = LoginWindow()
        login_app.run()
        
        print("👋 Application closed successfully")
        
    except ImportError as e:
        error_msg = f"Failed to import required modules: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Import Error", 
                               f"{error_msg}\\n\\nPlease check your Python installation.")
        except:
            pass
    
    except Exception as e:
        error_msg = f"Application startup failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Startup Error", error_msg)
        except:
            pass

if __name__ == "__main__":
    main()