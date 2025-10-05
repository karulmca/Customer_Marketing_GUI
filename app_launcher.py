"""
Company Data Scraper - Main Entry Point for Executable
Production-ready launcher for the complete application
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def setup_logging():
    """Setup logging for the application"""
    log_dir = current_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main application entry point"""
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Create debug file for executable testing
        debug_file = current_dir / "debug_launch.txt"
        with open(debug_file, 'w') as f:
            f.write(f"Company Data Scraper Launch Debug\n")
            f.write(f"Time: {__import__('datetime').datetime.now()}\n")
            f.write(f"Directory: {current_dir}\n")
            f.write(f"Executable: {__import__('sys').executable}\n")
            f.write(f"Frozen: {getattr(__import__('sys'), 'frozen', False)}\n")
            f.write(f"MEIPASS: {hasattr(__import__('sys'), '_MEIPASS')}\n")
        
        logger.info("Starting Company Data Scraper Application")
        logger.info(f"Application directory: {current_dir}")
        
        # Check for .env file
        env_file = current_dir / ".env"
        if not env_file.exists():
            # Try database_config/.env as fallback
            env_file = current_dir / "database_config" / ".env"
            
        logger.info(f"Looking for .env file at: {env_file}")
        if env_file.exists():
            logger.info(".env file found")
        else:
            logger.warning(".env file not found - database connection may fail")
        
        # Test database connection before launching GUI
        try:
            from database_config.postgresql_config import PostgreSQLConfig
            config = PostgreSQLConfig()
            if config.test_connection():
                logger.info("Database connection verified")
                with open(debug_file, 'a') as f:
                    f.write("Database connection: SUCCESS\n")
            else:
                logger.error("Database connection failed")
                with open(debug_file, 'a') as f:
                    f.write("Database connection: FAILED\n")
        except Exception as db_error:
            logger.error(f"Database connection error: {db_error}")
            with open(debug_file, 'a') as f:
                f.write(f"Database error: {db_error}\n")
        
        # Import and start the login GUI
        from gui.login_gui import main as start_login
        
        logger.info("🔐 Launching authentication system...")
        start_login()
        
    except ImportError as e:
        error_msg = f"❌ Import Error: {str(e)}\nPlease ensure all required packages are installed."
        print(error_msg)
        logging.error(error_msg)
        
        # Show user-friendly error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Import Error", error_msg)
        except:
            pass
        
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"❌ Application Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        logging.error(error_msg)
        
        # Show user-friendly error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", f"An unexpected error occurred:\n\n{str(e)}")
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()