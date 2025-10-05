#!/usr/bin/env python3
"""
File Upload GUI with PostgreSQL Backend - JSON Storage Approach
Uploads files as JSON data for later scheduled processing
Now with integrated authentication support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import sys
from datetime import datetime
import threading
import json
import argparse
import tempfile
import time

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
database_config_path = os.path.join(parent_dir, 'database_config')
if database_config_path not in sys.path:
    sys.path.insert(0, database_config_path)

try:
    from db_utils import get_database_connection, check_database_requirements
    from file_upload_processor import FileUploadProcessor
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Database dependencies not available: {e}")
    DATABASE_AVAILABLE = False

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tipwindow = None
        
    def enter(self, event=None):
        self.showtip()
        
    def leave(self, event=None):
        self.hidetip()
        
    def showtip(self):
        if self.tipwindow or not self.text:
            return
        try:
            x, y, cx, cy = self.widget.bbox("insert")
        except:
            # Fallback if bbox fails
            x = y = cx = cy = 0
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Enhanced styling for tooltip
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#f8f9fa", relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 10, "normal"), wraplength=450,
                        padx=8, pady=6, foreground="#333333")
        label.pack()
        
        # Add slight shadow effect (Windows-like)
        tw.attributes('-alpha', 0.95)
        
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class FileUploadJSONGUI:
    def __init__(self, root, session_file_path=None):
        self.root = root
        self.session_file_path = session_file_path
        self.session_data = None
        self.user_info = None
        
        # Load authentication session if provided
        self.load_session()
        
        # Set window title with user info
        title = "File Upload & PostgreSQL Manager - JSON Storage"
        if self.user_info:
            title += f" - Welcome {self.user_info['username']}"
        self.root.title(title)
        self.root.geometry("1250x850")
        
        # Force window to be visible and on top initially
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        # Remove topmost after 3 seconds
        self.root.after(3000, lambda: self.root.attributes('-topmost', False))
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Variables
        self.uploaded_file_path = tk.StringVar()
        
        # Status variables
        self.is_processing = False
        self.df_preview = None
        self.db_connection = None
        self.file_processor = None
        
        # Initialize database connection
        self.init_database()
        
        self.create_widgets()
        
        # Start session validation if authenticated
        if self.session_data:
            self.start_session_monitoring()
        
    def init_database(self):
        """Initialize PostgreSQL database connection"""
        if not DATABASE_AVAILABLE:
            print("⚠️  Database dependencies not available")
            return False
            
        try:
            print("🔄 Initializing database connection...")
            self.db_connection = get_database_connection("postgresql")
            
            if not self.db_connection:
                print("❌ Failed to create database connection")
                return False
                
            # Test connection once
            if not self.db_connection.test_connection():
                print("❌ Database connection test failed")
                return False
                
            # Initialize database manager
            if not self.db_connection.connect():
                print("❌ Failed to initialize database manager")
                return False
                
            # Ensure tables exist
            self.db_connection.create_tables()
            
            # Initialize file processor
            self.file_processor = FileUploadProcessor()
            
            print("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            return False
    
    def get_db_status(self):
        """Get current database connection status"""
        try:
            if self.db_connection and self.db_connection.test_connection():
                return "✅ Connected"
            else:
                return "❌ Disconnected"
        except:
            return "❌ Error"
    
    def create_widgets(self):
        # User info header (only show if authenticated)
        if self.user_info:
            self.create_user_info_header()
        
        # Main container with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: File Upload (JSON Storage)
        upload_frame = ttk.Frame(notebook)
        notebook.add(upload_frame, text="📁 File Upload (JSON)")
        
        # Tab 2: Uploaded Files View
        files_frame = ttk.Frame(notebook)
        notebook.add(files_frame, text="📋 Uploaded Files")
        
        # Tab 3: Processed Data View
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="🗄️ Processed Data")
        
        # Tab 4: Job Processing
        jobs_frame = ttk.Frame(notebook)
        notebook.add(jobs_frame, text="⚙️ Processing Jobs")
        
        # Tab 5: Statistics
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="📊 Statistics")
        
        # Tab 6: Settings
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        
        self.create_upload_tab(upload_frame)
        self.create_files_tab(files_frame)
        self.create_data_tab(data_frame)  
        self.create_jobs_tab(jobs_frame)
        self.create_stats_tab(stats_frame)
        self.create_settings_tab(settings_frame)
    
    def create_user_info_header(self):
        """Create user information header with username and logout button"""
        # User info frame at the top
        user_frame = ttk.Frame(self.root)
        user_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Left side - User information
        user_info_frame = ttk.Frame(user_frame)
        user_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # User icon and info
        username = self.user_info.get('username', 'Unknown')
        user_role = self.user_info.get('role', 'user')
        user_email = self.user_info.get('email', '')
        
        # Role icon based on user role
        role_icon = "👑" if user_role == "admin" else "👤"
        
        # User info label
        user_text = f"{role_icon} Logged in as: {username}"
        if user_role == "admin":
            user_text += " (Administrator)"
        if user_email:
            user_text += f" • {user_email}"
            
        self.user_info_label = ttk.Label(user_info_frame, text=user_text, 
                                        font=('Arial', 10, 'bold'),
                                        foreground='#2c5530')
        self.user_info_label.pack(side=tk.LEFT, padx=(10, 0), pady=5)
        
        # Right side - Logout button and session info
        logout_frame = ttk.Frame(user_frame)
        logout_frame.pack(side=tk.RIGHT)
        
        # Session time info
        if self.session_data and self.session_data.get('login_time'):
            login_time = self.session_data.get('login_time', '')
            # Extract just the time part if it's in ISO format
            if 'T' in login_time:
                time_part = login_time.split('T')[1].split('.')[0]  # Get HH:MM:SS
                session_text = f"Session: {time_part}"
            else:
                session_text = f"Session: {login_time}"
            
            session_label = ttk.Label(logout_frame, text=session_text, 
                                    font=('Arial', 9),
                                    foreground='#666666')
            session_label.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        
        # Logout button
        logout_btn = ttk.Button(logout_frame, text="🚪 Logout", 
                               command=self.logout_user,
                               width=12)
        logout_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=5)
        
        # Separator line
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=(5, 0))
        
    def logout_user(self):
        """Handle user logout"""
        username = self.user_info.get('username', 'User')
        if messagebox.askyesno("Logout", f"Are you sure you want to logout, {username}?\n\nThis will close the application and end your session."):
            # Show logout message
            messagebox.showinfo("Logged Out", f"Goodbye {username}! You have been successfully logged out.")
            # Clean up and exit
            self.cleanup_and_exit()
    
    def update_user_info_display(self):
        """Update the user info display with current session status"""
        if hasattr(self, 'user_info_label') and self.user_info:
            username = self.user_info.get('username', 'Unknown')
            user_role = self.user_info.get('role', 'user')
            user_email = self.user_info.get('email', '')
            
            # Role icon based on user role
            role_icon = "👑" if user_role == "admin" else "👤"
            
            # Build user info text
            user_text = f"{role_icon} Logged in as: {username}"
            if user_role == "admin":
                user_text += " (Administrator)"
            if user_email:
                user_text += f" • {user_email}"
                
            # Add session status indicator
            if self.session_data:
                user_text += " • 🟢 Active Session"
            else:
                user_text += " • 🔴 No Session"
            
            self.user_info_label.config(text=user_text)
        
    def create_upload_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with info icon
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="📁 File Upload and Scheduled to Processing", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Info icon with tooltip
        info_icon = ttk.Label(title_frame, text=" ℹ️", font=('Arial', 16), 
                             cursor="question_arrow", foreground="#007ACC")
        info_icon.pack(side=tk.LEFT, padx=(10, 0))
        
        # Add hover effects
        def on_enter(e):
            info_icon.configure(foreground="#0056b3")
        def on_leave(e):
            info_icon.configure(foreground="#007ACC")
        
        info_icon.bind("<Enter>", on_enter)
        info_icon.bind("<Leave>", on_leave)
        
        # Create tooltip for info icon
        info_text = """🔄 How It Works:

1. 📤 Upload Excel/CSV files → Stored as JSON in 'file_upload' table
2. ⏸️ Files remain in 'pending' status until processed  
3. ⚙️ Scheduled jobs process the JSON data → Extract to 'company_data' table
4. 📊 Monitor processing status and manage jobs through GUI tabs

💡 This workflow allows for better job management and processing control.
🚀 Auto-processing can be enabled in the Settings tab."""
        
        self.create_tooltip(info_icon, info_text)
        
        # Database status frame
        status_frame = ttk.LabelFrame(main_frame, text="Database Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        db_status = self.get_db_status()
        self.db_status_label = ttk.Label(status_frame, text=f"PostgreSQL: {db_status}")
        self.db_status_label.pack(side=tk.LEFT)
        
        refresh_db_btn = ttk.Button(status_frame, text="🔄 Refresh", command=self.refresh_db_status)
        refresh_db_btn.pack(side=tk.RIGHT)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Select File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.uploaded_file_path, width=70)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # File info frame
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_info_text = scrolledtext.ScrolledText(info_frame, height=5, wrap=tk.WORD)
        self.file_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons frame - PUT BUTTONS BEFORE PREVIEW!
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Make upload button more prominent
        upload_btn = ttk.Button(control_frame, text="📤 UPLOAD FILE TO DATABASE", 
                               command=self.upload_as_json, width=30)
        upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(control_frame, text="🗑️ Clear", command=self.clear_upload)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add processing button too
        process_now_btn = ttk.Button(control_frame, text="⚡ Upload & Process Now", 
                                   command=self.upload_and_process, width=25)
        process_now_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(control_frame, textvariable=self.status_var)
        status_bar.pack(side=tk.RIGHT)
        
        # Preview frame - AFTER buttons so it doesn't hide them
        preview_frame = ttk.LabelFrame(main_frame, text="Data Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create Treeview for preview
        columns = ("Column1", "Column2", "Column3", "Column4", "Column5")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=150)
            
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for the given widget"""
        ToolTip(widget, text)
        
    def create_files_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📋 Uploaded Files (JSON Storage)", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = ttk.Button(control_frame, text="🔄 Refresh", command=self.refresh_files_view)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        process_selected_btn = ttk.Button(control_frame, text="⚡ Process Selected", 
                                         command=self.process_selected_files)
        process_selected_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        view_json_btn = ttk.Button(control_frame, text="👁️ View JSON Data", 
                                  command=self.view_json_data)
        view_json_btn.pack(side=tk.LEFT)
        
        # Files view frame
        files_view_frame = ttk.LabelFrame(main_frame, text="Uploaded Files", padding="10")
        files_view_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for files
        files_columns = ("ID", "File Name", "Upload Date", "Records", "Status", "Uploaded By", "Size (KB)")
        self.files_tree = ttk.Treeview(files_view_frame, columns=files_columns, show="headings", height=15)
        
        for col in files_columns:
            self.files_tree.heading(col, text=col)
            self.files_tree.column(col, width=100)
            
        files_scrollbar_y = ttk.Scrollbar(files_view_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        files_scrollbar_x = ttk.Scrollbar(files_view_frame, orient=tk.HORIZONTAL, command=self.files_tree.xview)
        self.files_tree.configure(yscrollcommand=files_scrollbar_y.set, xscrollcommand=files_scrollbar_x.set)
        
        self.files_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        files_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        files_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load initial files view
        self.refresh_files_view()
        
    def create_data_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🗄️ Processed Company Data", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Source file filter frame
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(filter_frame, text="📁 Source File:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.source_file_var = tk.StringVar()
        self.source_file_dropdown = ttk.Combobox(filter_frame, textvariable=self.source_file_var, 
                                                width=25, state="readonly")
        self.source_file_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        self.source_file_dropdown.bind('<<ComboboxSelected>>', self.on_source_file_selected)
        
        # Control buttons
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_data_view)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = ttk.Button(buttons_frame, text="📤 Export", command=self.export_processed_data)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ttk.Button(buttons_frame, text="🗑️ Delete Selected", command=self.delete_selected_data)
        delete_btn.pack(side=tk.LEFT)
        
        # Data view frame
        data_view_frame = ttk.LabelFrame(main_frame, text="Processed Company Data", padding="10")
        data_view_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for processed data
        data_columns = ("ID", "Company Name", "LinkedIn URL", "Website", "Size", "Industry", "Revenue", "Source File")
        self.data_tree = ttk.Treeview(data_view_frame, columns=data_columns, show="headings", height=15)
        
        for col in data_columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=120)
            
        data_scrollbar_y = ttk.Scrollbar(data_view_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        data_scrollbar_x = ttk.Scrollbar(data_view_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=data_scrollbar_y.set, xscrollcommand=data_scrollbar_x.set)
        
        self.data_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        data_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        data_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load initial data view
        self.refresh_data_view()
        
    def create_jobs_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="⚙️ Processing Jobs Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = ttk.Button(control_frame, text="🔄 Refresh Jobs", command=self.refresh_jobs_view)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        process_all_btn = ttk.Button(control_frame, text="⚡ Process All Pending", 
                                    command=self.process_all_pending)
        process_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        monitor_btn = ttk.Button(control_frame, text="📊 Show Processing Stats", 
                                command=self.show_processing_stats)
        monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        create_job_btn = ttk.Button(control_frame, text="➕ Create Job", 
                                   command=self.create_processing_job)
        create_job_btn.pack(side=tk.LEFT)
        
        # Jobs info frame
        jobs_info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Job Processing Info", padding="10")
        jobs_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """📋 Processing Jobs:
• Queued: Jobs waiting to be processed
• Running: Jobs currently being processed  
• Completed: Successfully processed jobs
• Failed: Jobs that encountered errors
• Jobs can be retried up to 3 times automatically"""
        
        jobs_info_label = ttk.Label(jobs_info_frame, text=info_text, justify=tk.LEFT)
        jobs_info_label.pack(anchor=tk.W)
        
        # Jobs view frame
        jobs_view_frame = ttk.LabelFrame(main_frame, text="Processing Jobs", padding="10")
        jobs_view_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for jobs
        jobs_columns = ("Job ID", "Type", "File ID", "Status", "Scheduled", "Started", "Completed", "Retries")
        self.jobs_tree = ttk.Treeview(jobs_view_frame, columns=jobs_columns, show="headings", height=12)
        
        for col in jobs_columns:
            self.jobs_tree.heading(col, text=col)
            self.jobs_tree.column(col, width=100)
            
        jobs_scrollbar_y = ttk.Scrollbar(jobs_view_frame, orient=tk.VERTICAL, command=self.jobs_tree.yview)
        jobs_scrollbar_x = ttk.Scrollbar(jobs_view_frame, orient=tk.HORIZONTAL, command=self.jobs_tree.xview)
        self.jobs_tree.configure(yscrollcommand=jobs_scrollbar_y.set, xscrollcommand=jobs_scrollbar_x.set)
        
        self.jobs_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        jobs_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        jobs_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load initial jobs view
        self.refresh_jobs_view()
        
    def create_stats_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 System Statistics", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        refresh_stats_btn = ttk.Button(control_frame, text="🔄 Refresh Stats", command=self.refresh_stats)
        refresh_stats_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_all_btn = ttk.Button(control_frame, text="📤 Export All Data", command=self.export_all_data)
        export_all_btn.pack(side=tk.LEFT)
        
        # Statistics frame
        stats_display_frame = ttk.LabelFrame(main_frame, text="Database Statistics", padding="10")
        stats_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = scrolledtext.ScrolledText(stats_display_frame, height=20, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Load initial stats
        self.refresh_stats()
    
    # Implementation methods for the UI
    def refresh_db_status(self):
        """Refresh database connection status"""
        try:
            db_status = self.get_db_status()
            self.db_status_label.config(text=f"PostgreSQL: {db_status}")
            
            # If disconnected, try to reconnect
            if "❌" in db_status:
                print("🔄 Attempting to reconnect to database...")
                if self.init_database():
                    self.db_status_label.config(text="PostgreSQL: ✅ Connected")
                    print("✅ Database reconnected successfully")
                else:
                    print("❌ Database reconnection failed")
        except Exception as e:
            print(f"❌ Error refreshing database status: {e}")
            self.db_status_label.config(text="PostgreSQL: ❌ Error")
        
    def browse_file(self):
        """Browse for file to upload"""
        file_types = [
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select file to upload",
            filetypes=file_types
        )
        
        if filename:
            self.uploaded_file_path.set(filename)
            self.analyze_file()
            
    def analyze_file(self):
        """Analyze the uploaded file and show preview"""
        file_path = self.uploaded_file_path.get()
        if not file_path or not os.path.exists(file_path):
            return
            
        try:
            # Read file based on extension
            if file_path.lower().endswith(('.xlsx', '.xls')):
                self.df_preview = pd.read_excel(file_path)
            elif file_path.lower().endswith('.csv'):
                self.df_preview = pd.read_csv(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
                
            # Update file info
            info = f"📁 File: {os.path.basename(file_path)}\n"
            info += f"📊 Rows: {len(self.df_preview)}\n"
            info += f"📋 Columns: {len(self.df_preview.columns)}\n"
            info += f"💾 Size: {os.path.getsize(file_path)} bytes\n"
            info += f"🔄 Will be stored as JSON for scheduled processing"
                
            self.file_info_text.delete(1.0, tk.END)
            self.file_info_text.insert(1.0, info)
            
            # Update preview
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")
            
    def update_preview(self):
        """Update the preview treeview with file data"""
        # Clear existing data
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
            
        if self.df_preview is None:
            return
            
        # Update column headers
        columns = list(self.df_preview.columns)[:5]  # Show first 5 columns
        self.preview_tree["columns"] = columns
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=150)
            
        # Add data rows (first 10 rows)
        for i, row in self.df_preview.head(10).iterrows():
            values = [str(row[col]) if col in row else "" for col in columns]
            self.preview_tree.insert("", tk.END, values=values)
            
    def upload_as_json(self):
        """Upload file as JSON to file_upload table"""
        if self.df_preview is None:
            messagebox.showerror("Error", "Please select and analyze a file first")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Upload already in progress")
            return
            
        if not self.file_processor:
            messagebox.showerror("Error", "File processor not initialized")
            return
            
        # Start upload in separate thread
        self.is_processing = True
        self.status_var.set("Uploading as JSON...")
        
        thread = threading.Thread(target=self._upload_json_worker)
        thread.daemon = True
        thread.start()
        
    def _upload_json_worker(self):
        """Worker thread for JSON upload"""
        try:
            file_path = self.uploaded_file_path.get()
            
            # Use authenticated user or default
            uploaded_by = "GUI_User"
            if self.user_info and self.user_info.get('username'):
                uploaded_by = self.user_info['username']
            
            file_upload_id = self.file_processor.upload_file_as_json(file_path, uploaded_by)
            
            if file_upload_id:
                self.root.after(0, lambda: self._upload_json_completed(file_upload_id))
            else:
                self.root.after(0, lambda: self._upload_json_failed("Upload failed"))
                
        except Exception as e:
            self.root.after(0, lambda: self._upload_json_failed(str(e)))
            
    def _upload_json_completed(self, file_upload_id):
        """Handle successful JSON upload completion"""
        self.is_processing = False
        self.status_var.set(f"✅ File uploaded as JSON (ID: {file_upload_id})")
        
        # Check if auto-start is enabled (default to True if not set)
        auto_start_enabled = getattr(self, 'auto_start_var', tk.BooleanVar(value=True)).get()
        
        if auto_start_enabled:
            # Auto-start processing
            auto_start_success = self.auto_start_processing(file_upload_id)
            
            if auto_start_success:
                messagebox.showinfo("Success", 
                                   f"File uploaded and processing started!\n\n"
                                   f"Upload ID: {file_upload_id}\n"
                                   f"Status: Processing started automatically\n\n"
                                   f"Processing with 10-20 second timing for optimal success.\n"
                                   f"Monitor progress in the Processing Jobs tab.")
            else:
                messagebox.showinfo("Upload Success", 
                                   f"File uploaded successfully as JSON!\n\n"
                                   f"Upload ID: {file_upload_id}\n"
                                   f"Status: Pending processing\n\n"
                                   f"Auto-start failed - please manually start in Processing Jobs tab.")
        else:
            messagebox.showinfo("Upload Success", 
                               f"File uploaded successfully as JSON!\n\n"
                               f"Upload ID: {file_upload_id}\n"
                               f"Status: Pending processing\n\n"
                               f"Auto-processing is disabled. Go to Processing Jobs tab to start manually.")
        
        self.refresh_files_view()
        self.refresh_stats()
        self.refresh_jobs_view()  # Refresh jobs to show the started job
        
    def _upload_json_failed(self, error):
        """Handle JSON upload failure"""
        self.is_processing = False
        self.status_var.set("❌ Upload failed")
        messagebox.showerror("Upload Failed", f"Failed to upload file as JSON: {error}")
        
    def upload_and_process(self):
        """Upload file as JSON and immediately process it"""
        if self.df_preview is None:
            messagebox.showerror("Error", "Please select and analyze a file first")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Upload already in progress")
            return
            
        if not self.file_processor:
            messagebox.showerror("Error", "File processor not initialized")
            return
            
        # Start upload and process in separate thread
        self.is_processing = True
        self.status_var.set("Uploading and processing...")
        
        thread = threading.Thread(target=self._upload_and_process_worker)
        thread.daemon = True
        thread.start()
        
    def _upload_and_process_worker(self):
        """Worker thread for upload and immediate processing"""
        try:
            file_path = self.uploaded_file_path.get()
            
            # Use authenticated user or default
            uploaded_by = "GUI_User"
            if self.user_info and self.user_info.get('username'):
                uploaded_by = self.user_info['username']
            
            # First upload as JSON
            file_upload_id = self.file_processor.upload_file_as_json(file_path, uploaded_by)
            
            if file_upload_id:
                # Then immediately process it
                success = self.file_processor.process_uploaded_file(file_upload_id)
                if success:
                    self.root.after(0, lambda: self._upload_and_process_completed(file_upload_id))
                else:
                    self.root.after(0, lambda: self._upload_and_process_failed(f"Processing failed for ID {file_upload_id}"))
            else:
                self.root.after(0, lambda: self._upload_and_process_failed("Upload failed"))
                
        except Exception as e:
            self.root.after(0, lambda: self._upload_and_process_failed(str(e)))
            
    def _upload_and_process_completed(self, file_upload_id):
        """Handle successful upload and processing completion"""
        self.is_processing = False
        self.status_var.set(f"✅ File uploaded and processed (ID: {file_upload_id})")
        messagebox.showinfo("Success", 
                           f"File uploaded and processed successfully!\n\n"
                           f"Upload ID: {file_upload_id}\n"
                           f"Status: Completed\n\n"
                           f"Data has been extracted to company_data table.")
        self.refresh_files_view()
        self.refresh_data_view()
        self.refresh_stats()
        
    def _upload_and_process_failed(self, error):
        """Handle upload and processing failure"""
        self.is_processing = False
        self.status_var.set("❌ Upload/processing failed")
        messagebox.showerror("Processing Failed", f"Failed to upload and process file: {error}")
    
    def auto_start_processing(self, file_upload_id):
        """Automatically start processing for the uploaded file"""
        try:
            if not DATABASE_AVAILABLE:
                return False
                
            # Import the enhanced processor
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from enhanced_scheduled_processor import EnhancedScheduledProcessor
            
            processor = EnhancedScheduledProcessor()
            
            # Check if there's a pending job for this file
            jobs_query = """
                SELECT id, job_status FROM processing_jobs 
                WHERE file_upload_id = %s AND job_status = 'queued'
                ORDER BY created_at DESC LIMIT 1
            """
            
            # Execute query to find pending job
            import pandas as pd
            try:
                # Use a parameterized query with proper format
                formatted_query = f"""
                SELECT id, job_status FROM processing_jobs 
                WHERE file_upload_id = '{file_upload_id}' AND job_status = 'queued'
                ORDER BY scheduled_at DESC LIMIT 1
                """
                result = processor.db_connection.query_to_dataframe(formatted_query)
                    
                if result.empty:
                    return False
                    
                job_id = result.iloc[0]['id']  # Get UUID string directly
                
                # Start processing in a separate thread to avoid blocking GUI
                import threading
                
                def start_processing_thread():
                    try:
                        processor.process_pending_job(job_id)
                    except Exception as e:
                        print(f"Error in auto-processing: {e}")
                
                processing_thread = threading.Thread(target=start_processing_thread, daemon=True)
                processing_thread.start()
                
                return True
                
            except Exception as e:
                print(f"Database error in auto_start_processing: {e}")
                return False
                
        except Exception as e:
            print(f"Error in auto_start_processing: {e}")
            return False
        
    def clear_upload(self):
        """Clear upload form"""
        self.uploaded_file_path.set("")
        self.df_preview = None
        self.file_info_text.delete(1.0, tk.END)
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self.status_var.set("Ready")
        
    def refresh_files_view(self):
        """Refresh the uploaded files view"""
        try:
            # Clear existing data
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)
                
            if not self.db_connection:
                return
                
            # Get all uploaded files
            query = """
                SELECT id, file_name, upload_date, records_count, 
                       processing_status, uploaded_by, file_size
                FROM file_upload 
                ORDER BY upload_date DESC
            """
            df = self.db_connection.query_to_dataframe(query)
            
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    file_size_kb = int(row.get('file_size', 0)) // 1024 if row.get('file_size') else 0
                    values = [
                        str(row.get('id', '')),
                        str(row.get('file_name', '')),
                        str(row.get('upload_date', ''))[:19],  # Remove microseconds
                        str(row.get('records_count', '')),
                        str(row.get('processing_status', '')),
                        str(row.get('uploaded_by', '')),
                        f"{file_size_kb} KB"
                    ]
                    self.files_tree.insert("", tk.END, values=values)
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to refresh files view: {str(e)}")
            
    def refresh_data_view(self):
        """Refresh the processed data view and populate source file dropdown"""
        try:
            # First, populate the source file dropdown
            self.populate_source_file_dropdown()
            
            # Clear existing data
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
                
            if not self.db_connection:
                return
                
            # Get selected source file filter
            selected_source = self.source_file_var.get()
            
            # Build query based on filter
            if selected_source and selected_source != "All Files":
                # Filter by specific source file
                if selected_source.startswith("File ID:"):
                    # Extract file upload ID from the selection
                    file_id = selected_source.split("File ID: ")[1].split(" -")[0]
                    query = f"""
                        SELECT cd.id, cd.company_name, cd.linkedin_url, cd.company_website, 
                               cd.company_size, cd.industry, cd.revenue, cd.file_source,
                               fu.file_name, cd.file_upload_id
                        FROM company_data cd
                        LEFT JOIN file_upload fu ON cd.file_upload_id = fu.id
                        WHERE cd.file_upload_id = '{file_id}'
                        ORDER BY cd.upload_date DESC
                    """
                    df = self.db_connection.query_to_dataframe(query)
                else:
                    # Filter by file_source name
                    query = f"""
                        SELECT cd.id, cd.company_name, cd.linkedin_url, cd.company_website, 
                               cd.company_size, cd.industry, cd.revenue, cd.file_source,
                               fu.file_name, cd.file_upload_id
                        FROM company_data cd
                        LEFT JOIN file_upload fu ON cd.file_upload_id = fu.id
                        WHERE cd.file_source = '{selected_source.replace("'", "''")}'
                        ORDER BY cd.upload_date DESC
                    """
                    df = self.db_connection.query_to_dataframe(query)
            else:
                # Show all data
                query = """
                    SELECT cd.id, cd.company_name, cd.linkedin_url, cd.company_website, 
                           cd.company_size, cd.industry, cd.revenue, cd.file_source,
                           fu.file_name, cd.file_upload_id
                    FROM company_data cd
                    LEFT JOIN file_upload fu ON cd.file_upload_id = fu.id
                    ORDER BY cd.upload_date DESC
                    LIMIT 100
                """
                df = self.db_connection.query_to_dataframe(query)
            
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    # Use file_name from join if available, otherwise use file_source
                    source_display = row.get('file_name', row.get('file_source', ''))
                    if row.get('file_upload_id'):
                        source_display = f"{source_display} (ID: {row.get('file_upload_id')})"
                    
                    values = [
                        str(row.get('id', '')),
                        str(row.get('company_name', '')),
                        str(row.get('linkedin_url', '')),
                        str(row.get('company_website', '')),
                        str(row.get('company_size', '')),
                        str(row.get('industry', '')),
                        str(row.get('revenue', '')),
                        source_display
                    ]
                    self.data_tree.insert("", tk.END, values=values)
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to refresh data view: {str(e)}")
    
    def populate_source_file_dropdown(self):
        """Populate the source file dropdown with available files"""
        try:
            if not self.db_connection:
                return
                
            # Get unique source files with their upload IDs
            query = """
                SELECT DISTINCT 
                    fu.id as file_upload_id,
                    fu.file_name,
                    cd.file_source,
                    COUNT(cd.id) as company_count
                FROM file_upload fu
                LEFT JOIN company_data cd ON fu.id = cd.file_upload_id
                WHERE cd.file_upload_id IS NOT NULL  -- Only files that have been processed
                GROUP BY fu.id, fu.file_name, cd.file_source
                ORDER BY fu.id DESC
            """
            
            df = self.db_connection.query_to_dataframe(query)
            
            # Prepare dropdown values
            dropdown_values = ["All Files"]
            
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    file_name = row.get('file_name', 'Unknown File')
                    file_id = row.get('file_upload_id', '')
                    company_count = row.get('company_count', 0)
                    
                    # Create display text with file name, ID, and company count
                    display_text = f"File ID: {file_id} - {file_name} ({company_count} companies)"
                    dropdown_values.append(display_text)
            
            # Update dropdown values
            self.source_file_dropdown['values'] = dropdown_values
            
            # Set default selection if not already set
            if not self.source_file_var.get() or self.source_file_var.get() not in dropdown_values:
                self.source_file_var.set("All Files")
                
        except Exception as e:
            print(f"Error populating source file dropdown: {e}")
    
    def on_source_file_selected(self, event=None):
        """Handle source file selection change"""
        try:
            # Refresh the data view with the new filter
            self.refresh_data_view()
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to apply source file filter: {str(e)}")
            
    def refresh_jobs_view(self):
        """Refresh the processing jobs view"""
        try:
            # Clear existing data
            for item in self.jobs_tree.get_children():
                self.jobs_tree.delete(item)
                
            if not self.db_connection:
                return
                
            # Get all processing jobs
            query = """
                SELECT id, job_type, file_upload_id, job_status, 
                       scheduled_at, started_at, completed_at, retry_count
                FROM processing_jobs 
                ORDER BY scheduled_at DESC
            """
            df = self.db_connection.query_to_dataframe(query)
            
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    values = [
                        str(row.get('id', '')),
                        str(row.get('job_type', '')),
                        str(row.get('file_upload_id', '')),
                        str(row.get('job_status', '')),
                        str(row.get('scheduled_at', ''))[:19] if row.get('scheduled_at') else '',
                        str(row.get('started_at', ''))[:19] if row.get('started_at') else '',
                        str(row.get('completed_at', ''))[:19] if row.get('completed_at') else '',
                        str(row.get('retry_count', ''))
                    ]
                    self.jobs_tree.insert("", tk.END, values=values)
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to refresh jobs view: {str(e)}")
            
    def refresh_stats(self):
        """Refresh system statistics"""
        try:
            if not self.file_processor:
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, "❌ File processor not initialized")
                return
                
            stats = self.file_processor.get_upload_statistics()
            
            # Format stats display
            stats_text = f"📊 File Upload System Statistics\n"
            stats_text += f"{'='*60}\n\n"
            
            stats_text += f"📁 File Uploads:\n"
            stats_text += f"   • Total Uploads: {stats.get('total_uploads', 0)}\n"
            stats_text += f"   • Pending Processing: {stats.get('pending_uploads', 0)}\n"
            stats_text += f"   • Successfully Processed: {stats.get('completed_uploads', 0)}\n"
            stats_text += f"   • Failed Processing: {stats.get('failed_uploads', 0)}\n\n"
            
            stats_text += f"🏢 Processed Company Data:\n"
            stats_text += f"   • Total Records: {stats.get('total_processed_records', 0)}\n\n"
            
            # Processing efficiency
            total_files = stats.get('total_uploads', 0)
            if total_files > 0:
                success_rate = (stats.get('completed_uploads', 0) / total_files) * 100
                stats_text += f"📈 Processing Efficiency:\n"
                stats_text += f"   • Success Rate: {success_rate:.1f}%\n"
                stats_text += f"   • Pending Rate: {(stats.get('pending_uploads', 0) / total_files) * 100:.1f}%\n"
                stats_text += f"   • Failure Rate: {(stats.get('failed_uploads', 0) / total_files) * 100:.1f}%\n\n"
            
            stats_text += f"🔄 System Status:\n"
            stats_text += f"   • Database: {'✅ Connected' if self.db_connection and self.db_connection.test_connection() else '❌ Disconnected'}\n"
            stats_text += f"   • File Processor: {'✅ Ready' if self.file_processor else '❌ Not Available'}\n"
            stats_text += f"   • Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            stats_text += f"💡 System Workflow:\n"
            stats_text += f"   1. Files uploaded → Stored as JSON in 'file_upload' table\n"
            stats_text += f"   2. Processing jobs created automatically\n"
            stats_text += f"   3. Scheduled processors extract data → 'company_data' table\n"
            stats_text += f"   4. Monitor progress through GUI tabs"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"❌ Error loading stats: {str(e)}")
    
    def process_selected_files(self):
        """Process selected files from the files view"""
        selected_items = self.files_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select files to process")
            return
            
        if not messagebox.askyesno("Confirm Processing", 
                                  f"Process {len(selected_items)} selected files?"):
            return
            
        # Start processing in separate thread
        thread = threading.Thread(target=self._process_selected_worker, args=(selected_items,))
        thread.daemon = True
        thread.start()
        
    def _process_selected_worker(self, selected_items):
        """Worker thread for processing selected files"""
        try:
            success_count = 0
            failure_count = 0
            
            for item in selected_items:
                file_upload_id = int(self.files_tree.item(item)['values'][0])
                
                if self.file_processor.process_uploaded_file(file_upload_id):
                    success_count += 1
                else:
                    failure_count += 1
            
            # Update UI in main thread
            self.root.after(0, lambda: self._processing_completed(success_count, failure_count))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Processing Error", str(e)))
            
    def _processing_completed(self, success_count, failure_count):
        """Handle processing completion"""
        total = success_count + failure_count
        messagebox.showinfo("Processing Complete", 
                           f"Processing completed!\n\n"
                           f"✅ Successful: {success_count}\n"
                           f"❌ Failed: {failure_count}\n"
                           f"📋 Total: {total}")
        
        # Refresh all views
        self.refresh_files_view()
        self.refresh_data_view()
        self.refresh_jobs_view()
        self.refresh_stats()
        
    def process_all_pending(self):
        """Process all pending files"""
        if not messagebox.askyesno("Confirm Processing", 
                                  "Process all pending files?\n\n"
                                  "This may take some time depending on the number of files."):
            return
            
        # Start processing in separate thread
        thread = threading.Thread(target=self._process_all_pending_worker)
        thread.daemon = True
        thread.start()
        
    def _process_all_pending_worker(self):
        """Worker thread for processing all pending files"""
        try:
            from file_upload_processor import process_all_pending_files
            process_all_pending_files()
            
            # Update UI in main thread
            self.root.after(0, lambda: self._all_processing_completed())
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Processing Error", str(e)))
            
    def _all_processing_completed(self):
        """Handle all processing completion"""
        messagebox.showinfo("Batch Processing Complete", 
                           "All pending files have been processed!\n\n"
                           "Check the Statistics tab for updated counts.")
        
        # Refresh all views
        self.refresh_files_view()
        self.refresh_data_view()
        self.refresh_jobs_view()
        self.refresh_stats()
        
    def view_json_data(self):
        """View JSON data of selected file"""
        selected_items = self.files_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a file to view JSON data")
            return
            
        file_upload_id = int(self.files_tree.item(selected_items[0])['values'][0])
        
        try:
            upload_data = self.file_processor.get_upload_data(file_upload_id)
            if upload_data:
                # Create new window to display JSON
                json_window = tk.Toplevel(self.root)
                json_window.title(f"JSON Data - {upload_data['file_name']}")
                json_window.geometry("800x600")
                
                json_text = scrolledtext.ScrolledText(json_window, wrap=tk.WORD)
                json_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Format JSON for display
                json_str = json.dumps(upload_data['raw_data'], indent=2, ensure_ascii=False)
                json_text.insert(1.0, json_str)
                json_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Failed to retrieve JSON data")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view JSON data: {str(e)}")
            
    def show_processing_stats(self):
        """Show detailed processing statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Processing Statistics")
        stats_window.geometry("800x600")
        
        # Make window modal
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 Processing Statistics", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Stats text area
        stats_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20)
        stats_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh", 
                                command=lambda: self._refresh_stats_display(stats_text))
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = ttk.Button(button_frame, text="Close", 
                              command=stats_window.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        # Load initial stats
        self._refresh_stats_display(stats_text)
        
    def _refresh_stats_display(self, stats_text):
        """Refresh the statistics display"""
        try:
            # Clear existing text
            stats_text.config(state=tk.NORMAL)
            stats_text.delete(1.0, tk.END)
            
            # Get enhanced statistics
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from enhanced_scheduled_processor import EnhancedScheduledProcessor
            processor = EnhancedScheduledProcessor()
            
            # Capture log output
            import io
            import logging
            
            # Create string stream to capture log output
            log_stream = io.StringIO()
            log_handler = logging.StreamHandler(log_stream)
            log_handler.setLevel(logging.INFO)
            
            # Add handler temporarily
            logger = logging.getLogger('enhanced_scheduled_processor')
            original_handlers = logger.handlers[:]
            logger.handlers = [log_handler]
            
            # Get statistics (this will write to our stream)
            stats_data = processor.get_processing_statistics()
            
            # Restore original handlers
            logger.handlers = original_handlers
            
            # Get the logged output
            log_output = log_stream.getvalue()
            
            # Display the statistics
            if log_output:
                stats_text.insert(tk.END, log_output)
            else:
                stats_text.insert(tk.END, "📊 Processing Statistics:\n")
                stats_text.insert(tk.END, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if stats_data:
                    if 'file_stats' in stats_data and stats_data['file_stats']:
                        stats_text.insert(tk.END, "📁 File Upload Status:\n")
                        for stat in stats_data['file_stats']:
                            stats_text.insert(tk.END, f"   {stat['processing_status']}: {stat['count']} files\n")
                        stats_text.insert(tk.END, "\n")
                    
                    if 'company_stats' in stats_data and stats_data['company_stats']:
                        comp_stats = stats_data['company_stats']
                        total = comp_stats.get('total_companies', 0)
                        stats_text.insert(tk.END, "🏢 Company Data Extraction:\n")
                        stats_text.insert(tk.END, f"   Total Companies: {total}\n")
                        
                        if total > 0:
                            size_count = comp_stats.get('with_size', 0)
                            industry_count = comp_stats.get('with_industry', 0)
                            revenue_count = comp_stats.get('with_revenue', 0)
                            
                            stats_text.insert(tk.END, f"   Company Size: {size_count}/{total} ({(size_count/total)*100:.1f}%)\n")
                            stats_text.insert(tk.END, f"   Industry: {industry_count}/{total} ({(industry_count/total)*100:.1f}%)\n")
                            stats_text.insert(tk.END, f"   Revenue: {revenue_count}/{total} ({(revenue_count/total)*100:.1f}%)\n")
                        else:
                            stats_text.insert(tk.END, "   Company Size: 0/0\n")
                            stats_text.insert(tk.END, "   Industry: 0/0\n")
                            stats_text.insert(tk.END, "   Revenue: 0/0\n")
                else:
                    stats_text.insert(tk.END, "No statistics available")
            
            stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            stats_text.config(state=tk.NORMAL)
            stats_text.delete(1.0, tk.END)
            stats_text.insert(tk.END, f"Error loading statistics: {str(e)}")
            stats_text.config(state=tk.DISABLED)
    
    def create_processing_job(self):
        """Create a new processing job"""
        # Simple dialog to create a job - could be expanded
        messagebox.showinfo("Feature", "Job creation feature - to be implemented for advanced job scheduling")
        
    def export_processed_data(self):
        """Export processed company data"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Processed Data",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
                
            if not self.db_connection:
                messagebox.showerror("Error", "No database connection")
                return
                
            df = self.db_connection.get_all_records("company_data")
            if df is not None:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Processed data exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to retrieve data for export")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
            
    def delete_selected_data(self):
        """Delete selected processed data records"""
        selected_items = self.data_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select records to delete")
            return
            
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected_items)} selected records?"):
            return
            
        try:
            if not self.db_connection:
                messagebox.showerror("Error", "No database connection")
                return
                
            for item in selected_items:
                record_id = self.data_tree.item(item)['values'][0]
                query = f"DELETE FROM company_data WHERE id = '{record_id}'"
                self.db_connection.query_to_dataframe(query)
                
            messagebox.showinfo("Success", f"Deleted {len(selected_items)} records")
            self.refresh_data_view()
            self.refresh_stats()
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete records: {str(e)}")
            
    def export_all_data(self):
        """Export all system data to Excel"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export All System Data",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
                
            if not self.db_connection:
                messagebox.showerror("Error", "No database connection")
                return
                
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export all tables
                tables = ['file_upload', 'company_data', 'upload_history', 'processing_jobs']
                
                for table in tables:
                    try:
                        df = self.db_connection.get_all_records(table)
                        if df is not None and not df.empty:
                            # Handle JSON columns for file_upload table
                            if table == 'file_upload' and 'raw_data' in df.columns:
                                # Don't export raw JSON data - too large
                                df_export = df.drop('raw_data', axis=1)
                            else:
                                df_export = df
                                
                            df_export.to_excel(writer, sheet_name=table.replace('_', ' ').title(), index=False)
                    except Exception as e:
                        print(f"Error exporting table {table}: {e}")
            
            messagebox.showinfo("Success", f"All system data exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export all data: {str(e)}")
    def create_settings_tab(self, parent):
        """Create Settings tab for timing and API key configuration"""
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="⚙️ System Settings", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Load current settings
        self.load_current_settings()
        
        # Timing Settings Section
        timing_frame = ttk.LabelFrame(main_frame, text="🕒 Timing Settings (seconds)", padding="15")
        timing_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Current timing display
        current_frame = ttk.Frame(timing_frame)
        current_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(current_frame, text="Current Configuration:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.current_timing_label = ttk.Label(current_frame, text="Loading...", foreground="blue")
        self.current_timing_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Timing controls
        controls_frame = ttk.Frame(timing_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(controls_frame, text="Wait time between LinkedIn requests:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(controls_frame, text="Min:").grid(row=1, column=0, padx=(0, 5))
        self.min_delay_var = tk.IntVar(value=10)
        self.min_delay_spin = ttk.Spinbox(controls_frame, from_=5, to=60, textvariable=self.min_delay_var, width=8)
        self.min_delay_spin.grid(row=1, column=1, padx=(0, 20))
        
        ttk.Label(controls_frame, text="Max:").grid(row=1, column=2, padx=(0, 5))
        self.max_delay_var = tk.IntVar(value=20)
        self.max_delay_spin = ttk.Spinbox(controls_frame, from_=10, to=120, textvariable=self.max_delay_var, width=8)
        self.max_delay_spin.grid(row=1, column=3, padx=(0, 20))
        
        # Timing info
        timing_info = ttk.Label(controls_frame, text="💡 Recommended: 10-20 seconds for optimal success rate", 
                              foreground="green", font=('Arial', 9))
        timing_info.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        # Auto-Processing Settings Section
        auto_frame = ttk.LabelFrame(main_frame, text="🚀 Auto-Processing Settings", padding="15")
        auto_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Auto-start checkbox
        self.auto_start_var = tk.BooleanVar(value=True)  # Default to enabled
        auto_start_cb = ttk.Checkbutton(auto_frame, text="🔥 Auto-start processing after file upload", 
                                       variable=self.auto_start_var)
        auto_start_cb.pack(anchor=tk.W, pady=(0, 10))
        
        auto_info = ttk.Label(auto_frame, text="💡 When enabled, LinkedIn scraping starts automatically after file upload\n"
                                              "When disabled, you must manually start processing in the Processing Jobs tab", 
                            foreground="blue", font=('Arial', 9), justify=tk.LEFT)
        auto_info.pack(anchor=tk.W)
        
        # API Settings Section
        api_frame = ttk.LabelFrame(main_frame, text="🔑 OpenAI API Configuration", padding="15")
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Current API key display
        api_current_frame = ttk.Frame(api_frame)
        api_current_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(api_current_frame, text="Current API Key Status:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.api_status_label = ttk.Label(api_current_frame, text="Loading...", foreground="blue")
        self.api_status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # API key input
        api_input_frame = ttk.Frame(api_frame)
        api_input_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(api_input_frame, text="OpenAI API Key:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_input_frame, textvariable=self.api_key_var, width=60, show="*")
        self.api_key_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Show/Hide API key
        show_key_frame = ttk.Frame(api_input_frame)
        show_key_frame.pack(anchor=tk.W)
        
        self.show_api_key_var = tk.BooleanVar(value=False)
        show_key_cb = ttk.Checkbutton(show_key_frame, text="Show API Key", variable=self.show_api_key_var, 
                                     command=self.toggle_api_key_visibility)
        show_key_cb.pack(side=tk.LEFT)
        
        # API info
        api_info = ttk.Label(api_input_frame, text="💡 Required for OpenAI-enhanced scraping features", 
                           foreground="green", font=('Arial', 9))
        api_info.pack(anchor=tk.W, pady=(10, 0))
        
        # Buttons Section
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Left side buttons
        left_buttons = ttk.Frame(buttons_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="🔄 Refresh Current Settings", 
                  command=self.refresh_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(left_buttons, text="↩️ Reset to Defaults", 
                  command=self.reset_to_defaults).pack(side=tk.LEFT, padx=(0, 10))
        
        # Right side buttons
        right_buttons = ttk.Frame(buttons_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="💾 Save Settings", 
                  command=self.save_settings, style="Accent.TButton").pack(side=tk.LEFT, padx=(10, 0))
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="📊 Settings Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.settings_status_label = ttk.Label(status_frame, text="Ready to configure settings", 
                                             foreground="blue")
        self.settings_status_label.pack()
        
        # Initialize settings display
        self.refresh_settings()
    
    def load_current_settings(self):
        """Load current settings from config.json"""
        try:
            import json
            with open('config.json', 'r') as f:
                self.current_config = json.load(f)
        except Exception as e:
            self.current_config = {
                'scraper_settings': {
                    'delay_range': [10, 20],
                    'timeout': 30,
                    'max_retries': 3
                },
                'openai_settings': {
                    'api_key': ''
                }
            }
    
    def refresh_settings(self):
        """Refresh settings display"""
        try:
            self.load_current_settings()
            
            # Update timing display
            delay_range = self.current_config.get('scraper_settings', {}).get('delay_range', [10, 20])
            self.current_timing_label.config(text=f"Min: {delay_range[0]}s, Max: {delay_range[1]}s", 
                                           foreground="green")
            
            # Update form values
            self.min_delay_var.set(delay_range[0])
            self.max_delay_var.set(delay_range[1])
            
            # Update auto-start setting
            auto_start = self.current_config.get('gui_settings', {}).get('auto_start_processing', True)
            self.auto_start_var.set(auto_start)
            
            # Update API key status
            api_key = self.current_config.get('openai_settings', {}).get('api_key', '')
            if api_key and len(api_key) > 10:
                masked_key = f"sk-...{api_key[-4:]}" if api_key.startswith('sk-') else f"***...{api_key[-4:]}"
                self.api_status_label.config(text=f"✅ Configured: {masked_key}", foreground="green")
                self.api_key_var.set(api_key)
            else:
                self.api_status_label.config(text="❌ Not configured", foreground="red")
                self.api_key_var.set('')
            
            self.settings_status_label.config(text="✅ Settings loaded successfully", foreground="green")
            
        except Exception as e:
            self.settings_status_label.config(text=f"❌ Error loading settings: {str(e)}", foreground="red")
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.show_api_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def reset_to_defaults(self):
        """Reset settings to recommended defaults"""
        self.min_delay_var.set(10)
        self.max_delay_var.set(20)
        self.settings_status_label.config(text="🔄 Reset to defaults (not saved yet)", foreground="blue")
    
    def save_settings(self):
        """Save settings to config.json"""
        try:
            import json
            
            # Validate settings
            min_delay = self.min_delay_var.get()
            max_delay = self.max_delay_var.get()
            api_key = self.api_key_var.get().strip()
            
            if min_delay >= max_delay:
                messagebox.showerror("Invalid Settings", "Min delay must be less than Max delay")
                return
            
            if min_delay < 5:
                messagebox.showwarning("Warning", "Min delay less than 5 seconds may cause rate limiting")
            
            # Update config
            self.current_config['scraper_settings']['delay_range'] = [min_delay, max_delay]
            
            # Handle auto-start setting
            if 'gui_settings' not in self.current_config:
                self.current_config['gui_settings'] = {}
            self.current_config['gui_settings']['auto_start_processing'] = self.auto_start_var.get()
            
            # Handle OpenAI settings
            if 'openai_settings' not in self.current_config:
                self.current_config['openai_settings'] = {}
            self.current_config['openai_settings']['api_key'] = api_key
            
            # Save to file
            with open('config.json', 'w') as f:
                json.dump(self.current_config, f, indent=4)
            
            # Update display
            self.refresh_settings()
            
            messagebox.showinfo("Settings Saved", 
                              f"✅ Settings saved successfully!\n\n"
                              f"🕒 Timing: {min_delay}-{max_delay} seconds\n"
                              f"🔑 API Key: {'Configured' if api_key else 'Not set'}\n\n"
                              f"Changes will take effect for new processing jobs.")
            
            self.settings_status_label.config(text="✅ Settings saved successfully!", foreground="green")
            
        except Exception as e:
            error_msg = f"❌ Error saving settings: {str(e)}"
            self.settings_status_label.config(text=error_msg, foreground="red")
            messagebox.showerror("Save Error", error_msg)
    
    def load_session(self):
        """Load authentication session from file."""
        if not self.session_file_path or not os.path.exists(self.session_file_path):
            return
        
        try:
            with open(self.session_file_path, 'r') as f:
                self.session_data = json.load(f)
                self.user_info = self.session_data.get('user_info', {})
                print(f"✅ Session loaded for user: {self.user_info.get('username', 'Unknown')}")
        except Exception as e:
            print(f"❌ Error loading session: {str(e)}")
            self.session_data = None
            self.user_info = None
    
    def validate_session(self):
        """Validate current session with authentication server."""
        if not self.session_data:
            print("❌ No session data available")
            return False
        
        # Check if session file was created recently (within last 10 minutes)
        # This helps avoid immediate expiration for fresh sessions
        session_timestamp = self.session_data.get('timestamp', 0)
        current_time = time.time()
        session_age = current_time - session_timestamp
        
        if session_age < 600:  # Less than 10 minutes old
            print(f"✅ Session is fresh ({session_age:.0f}s old), skipping validation")
            return True
        
        try:
            import sys
            import os
            # Add auth directory to path
            auth_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'auth')
            if auth_path not in sys.path:
                sys.path.append(auth_path)
            
            from user_auth import UserAuthenticator
            auth = UserAuthenticator()
            
            token = self.session_data.get('token')
            if not token:
                print("❌ No session token found")
                return False
            
            validation_result = auth.validate_session(token)
            is_valid = validation_result and validation_result.get('valid', False)
            
            if is_valid:
                print(f"✅ Session validated successfully for {self.user_info.get('username', 'Unknown')}")
            else:
                print(f"❌ Session validation failed: {validation_result}")
            
            return is_valid
        except Exception as e:
            print(f"❌ Session validation error: {str(e)}")
            return False
    
    def start_session_monitoring(self):
        """Start periodic session validation."""
        # Give a grace period for initial startup - validate after 30 seconds
        self.root.after(30000, self.periodic_session_check)
    
    def periodic_session_check(self):
        """Periodic session validation check."""
        if self.validate_session():
            # Update user info display to show active session
            self.update_user_info_display()
            # Schedule next validation in 5 minutes
            self.root.after(300000, self.periodic_session_check)
        else:
            # Session expired - update display and close
            if hasattr(self, 'user_info_label'):
                self.user_info_label.config(text="🔴 Session Expired", foreground='red')
            messagebox.showwarning("Session Expired", 
                                 "Your session has expired. The application will now close.")
            self.cleanup_and_exit()
    
    def on_closing(self):
        """Handle window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """Clean up session and exit application."""
        try:
            # Close database connection
            if hasattr(self, 'db_connection') and self.db_connection:
                self.db_connection.close()
            
            # Clean up session file
            if self.session_file_path and os.path.exists(self.session_file_path):
                try:
                    os.remove(self.session_file_path)
                    print("✅ Session file cleaned up")
                except Exception as e:
                    print(f"⚠️ Could not remove session file: {str(e)}")
            
            # Close GUI
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"❌ Error during cleanup: {str(e)}")
        finally:
            # Force exit if needed
            import sys
            sys.exit(0)

def main():
    """Main function with authentication session support."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='File Upload & PostgreSQL Manager')
    parser.add_argument('--auth-session', type=str, help='Path to authentication session file')
    args = parser.parse_args()
    
    print("🚀 Starting File Upload & PostgreSQL GUI - JSON Storage...")
    if args.auth_session:
        print(f"🔐 Authentication session file: {args.auth_session}")
    print("📋 Look for window: 'File Upload & PostgreSQL Manager - JSON Storage'")
    
    # Check database requirements
    if not DATABASE_AVAILABLE:
        print("❌ Database dependencies not available")
        print("💡 Please install: pip install psycopg2-binary sqlalchemy")
        return
    
    root = tk.Tk()
    app = FileUploadJSONGUI(root, session_file_path=args.auth_session)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    print("✅ PostgreSQL JSON File Upload GUI Created - Window should be visible now")
    if args.auth_session:
        print("🔐 Authentication session loaded")
    print("🔧 Features: JSON File Storage + Scheduled Processing + Job Management")
    
    root.mainloop()
    
    print("🏁 PostgreSQL JSON File Upload GUI Closed")

if __name__ == "__main__":
    main()