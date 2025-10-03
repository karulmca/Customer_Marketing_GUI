"""
Authenticated File Upload GUI
Main application with user authentication and session management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.user_auth import auth_manager

class AuthenticatedFileUploadGUI:
    """Main file upload GUI with authentication"""
    
    def __init__(self, session_token=None, user_info=None):
        self.session_token = session_token
        self.user_info = user_info
        self.root = None
        
        # Validate session
        if not self.validate_session():
            messagebox.showerror("Authentication Error", "Invalid or expired session. Please login again.")
            return
            
        self.setup_main_window()
        self.create_authenticated_interface()
        
    def validate_session(self):
        """Validate current session"""
        if not self.session_token:
            return False
            
        validation_result = auth_manager.validate_session(self.session_token)
        if not validation_result["valid"]:
            return False
            
        # Update user info if session is valid
        self.user_info = validation_result["user"]
        return True
    
    def setup_main_window(self):
        """Setup main authenticated window"""
        self.root = tk.Tk()
        self.root.title(f"Company Data Scraper - Welcome {self.user_info['username']}")
        self.root.geometry("1200x800")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_authenticated_interface(self):
        """Create the main authenticated interface"""
        
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header with user info and logout
        self.create_header(main_frame)
        
        # Create main content area
        self.create_main_content(main_frame)
        
        # Start session validation timer
        self.start_session_timer()
    
    def create_header(self, parent):
        """Create header with user info and navigation"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side - Application title
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(left_frame, text="Company Data Scraper", 
                               font=("Arial", 18, "bold"))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(left_frame, text="LinkedIn Data Extraction Platform", 
                                  font=("Arial", 10), foreground="gray")
        subtitle_label.pack(anchor=tk.W)
        
        # Right side - User info and logout
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # User info
        user_frame = ttk.LabelFrame(right_frame, text="User Session", padding=5)
        user_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(user_frame, text=f"👤 {self.user_info['username']}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.E)
        ttk.Label(user_frame, text=f"Role: {self.user_info['role']}", 
                 font=("Arial", 9)).pack(anchor=tk.E)
        
        # Login time
        login_time = datetime.now().strftime("%H:%M:%S")
        ttk.Label(user_frame, text=f"Login: {login_time}", 
                 font=("Arial", 8), foreground="gray").pack(anchor=tk.E)
        
        # Logout button
        logout_btn = ttk.Button(user_frame, text="Logout", 
                               command=self.logout, width=8)
        logout_btn.pack(anchor=tk.E, pady=(5, 0))
        
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
    
    def create_main_content(self, parent):
        """Create main content area with file processing"""
        
        # Check if user has permission to access file processing
        if not self.check_file_processing_permission():
            self.create_access_denied_content(parent)
            return
        
        # Create notebook for different sections
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # File Upload Tab
        upload_frame = ttk.Frame(notebook)
        notebook.add(upload_frame, text="📁 File Upload")
        self.create_file_upload_tab(upload_frame)
        
        # Processing Status Tab  
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="⚙️ Processing Status")
        self.create_status_tab(status_frame)
        
        # Settings Tab (Admin only)
        if self.user_info['role'] == 'admin':
            settings_frame = ttk.Frame(notebook)
            notebook.add(settings_frame, text="⚙️ Settings")
            self.create_settings_tab(settings_frame)
        
        # User Management Tab (Admin only)
        if self.user_info['role'] == 'admin':
            users_frame = ttk.Frame(notebook)
            notebook.add(users_frame, text="👥 User Management")
            self.create_user_management_tab(users_frame)
    
    def check_file_processing_permission(self):
        """Check if user has permission to access file processing"""
        # For now, all authenticated users have access
        # You can implement role-based access control here
        return True
    
    def create_access_denied_content(self, parent):
        """Create access denied message"""
        denied_frame = ttk.Frame(parent)
        denied_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center the message
        center_frame = ttk.Frame(denied_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(center_frame, text="🚫", font=("Arial", 48)).pack()
        ttk.Label(center_frame, text="Access Denied", 
                 font=("Arial", 24, "bold"), foreground="red").pack(pady=10)
        ttk.Label(center_frame, text="You don't have permission to access file processing.", 
                 font=("Arial", 12)).pack()
        ttk.Label(center_frame, text="Please contact your administrator.", 
                 font=("Arial", 10), foreground="gray").pack(pady=5)
    
    def create_file_upload_tab(self, parent):
        """Create file upload interface"""
        
        # Instructions
        instructions_frame = ttk.LabelFrame(parent, text="Instructions", padding=10)
        instructions_frame.pack(fill=tk.X, pady=(0, 10))
        
        instructions_text = """
        📋 File Upload Instructions:
        1. Select an Excel file (.xlsx) containing company data
        2. Ensure your file has columns: Company Name, Website, LinkedIn_URL
        3. Enable auto-processing if you want automatic LinkedIn scraping
        4. Click 'Upload and Process' to start data extraction
        """
        
        ttk.Label(instructions_frame, text=instructions_text, 
                 font=("Arial", 10), justify=tk.LEFT).pack(anchor=tk.W)
        
        # File selection
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File path
        self.file_path_var = tk.StringVar()
        file_path_frame = ttk.Frame(file_frame)
        file_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_path_frame, text="Selected File:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        file_path_entry = ttk.Entry(file_path_frame, textvariable=self.file_path_var, 
                                   state="readonly", font=("Arial", 10))
        file_path_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Browse button
        browse_btn = ttk.Button(file_frame, text="📁 Browse Files", 
                               command=self.browse_file)
        browse_btn.pack(anchor=tk.W, pady=(10, 0))
        
        # Processing options
        options_frame = ttk.LabelFrame(parent, text="Processing Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_process_var = tk.BooleanVar(value=True)
        auto_process_cb = ttk.Checkbutton(options_frame, text="Enable Auto-Processing (LinkedIn Scraping)", 
                                         variable=self.auto_process_var)
        auto_process_cb.pack(anchor=tk.W)
        
        # Upload button
        upload_frame = ttk.Frame(parent)
        upload_frame.pack(fill=tk.X, pady=10)
        
        self.upload_btn = ttk.Button(upload_frame, text="🚀 Upload and Process", 
                                    command=self.upload_file, 
                                    style="Upload.TButton")
        self.upload_btn.pack(anchor=tk.W)
        
        # Configure button style
        style = ttk.Style()
        style.configure("Upload.TButton", font=("Arial", 12, "bold"), padding=10)
        
        # Status
        self.upload_status_var = tk.StringVar()
        self.upload_status_label = ttk.Label(upload_frame, textvariable=self.upload_status_var, 
                                            font=("Arial", 10))
        self.upload_status_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Progress bar
        self.upload_progress_var = tk.DoubleVar()
        self.upload_progress_bar = ttk.Progressbar(upload_frame, 
                                                  variable=self.upload_progress_var, 
                                                  mode='determinate')
    
    def create_status_tab(self, parent):
        """Create processing status interface"""
        
        # Recent jobs
        jobs_frame = ttk.LabelFrame(parent, text="Recent Processing Jobs", padding=10)
        jobs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text area
        status_text_frame = ttk.Frame(jobs_frame)
        status_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_text_frame, wrap=tk.WORD, 
                                  font=("Consolas", 10), state=tk.DISABLED)
        status_scrollbar = ttk.Scrollbar(status_text_frame, orient=tk.VERTICAL, 
                                        command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_btn = ttk.Button(jobs_frame, text="🔄 Refresh Status", 
                                command=self.refresh_status)
        refresh_btn.pack(pady=(10, 0))
        
        # Load initial status
        self.refresh_status()
    
    def create_settings_tab(self, parent):
        """Create settings interface (Admin only)"""
        
        settings_label = ttk.Label(parent, text="⚙️ System Settings", 
                                  font=("Arial", 16, "bold"))
        settings_label.pack(pady=20)
        
        # Auto-processing settings
        auto_frame = ttk.LabelFrame(parent, text="Auto-Processing Configuration", padding=10)
        auto_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttk.Label(auto_frame, text="Configure automatic processing settings here.", 
                 font=("Arial", 10)).pack(anchor=tk.W)
        
        # Placeholder for future settings
        ttk.Label(parent, text="Additional settings will be added here.", 
                 font=("Arial", 10), foreground="gray").pack(pady=20)
    
    def create_user_management_tab(self, parent):
        """Create user management interface (Admin only)"""
        
        users_label = ttk.Label(parent, text="👥 User Management", 
                               font=("Arial", 16, "bold"))
        users_label.pack(pady=20)
        
        # User creation
        create_frame = ttk.LabelFrame(parent, text="Create New User", padding=10)
        create_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # New user form
        form_frame = ttk.Frame(create_frame)
        form_frame.pack(fill=tk.X)
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_username_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_password_var, show="*", width=20).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.new_email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_email_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Role
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.new_role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(form_frame, textvariable=self.new_role_var, 
                                 values=["user", "admin"], state="readonly", width=17)
        role_combo.grid(row=3, column=1, sticky=tk.W, padx=10)
        
        # Create button
        create_btn = ttk.Button(form_frame, text="Create User", 
                               command=self.create_user)
        create_btn.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Recent login attempts
        attempts_frame = ttk.LabelFrame(parent, text="Recent Login Attempts", padding=10)
        attempts_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        self.attempts_text = tk.Text(attempts_frame, wrap=tk.WORD, 
                                    font=("Consolas", 9), state=tk.DISABLED, height=8)
        attempts_scrollbar = ttk.Scrollbar(attempts_frame, orient=tk.VERTICAL, 
                                          command=self.attempts_text.yview)
        self.attempts_text.configure(yscrollcommand=attempts_scrollbar.set)
        
        self.attempts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attempts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load login attempts
        self.refresh_login_attempts()
    
    def browse_file(self):
        """Browse for file to upload"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.upload_status_var.set(f"File selected: {os.path.basename(file_path)}")
    
    def upload_file(self):
        """Upload and process file"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showwarning("No File Selected", "Please select a file to upload.")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", "The selected file does not exist.")
            return
        
        # Disable upload button
        self.upload_btn.configure(state="disabled", text="Processing...")
        self.upload_progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.upload_progress_bar.start(10)
        
        self.upload_status_var.set("Uploading file...")
        
        # Start upload in separate thread
        threading.Thread(target=self.process_file_upload, args=(file_path,), daemon=True).start()
    
    def process_file_upload(self, file_path):
        """Process file upload in background"""
        try:
            # Here you would integrate with your existing file upload logic
            # For now, simulate the process
            
            import time
            time.sleep(2)  # Simulate processing
            
            # Update UI in main thread
            self.root.after(0, self.upload_complete, True, "File uploaded and processing started!")
            
        except Exception as e:
            self.root.after(0, self.upload_complete, False, f"Upload failed: {str(e)}")
    
    def upload_complete(self, success, message):
        """Handle upload completion"""
        # Re-enable upload button
        self.upload_btn.configure(state="normal", text="🚀 Upload and Process")
        self.upload_progress_bar.stop()
        self.upload_progress_bar.pack_forget()
        
        if success:
            self.upload_status_var.set(f"✅ {message}")
            messagebox.showinfo("Upload Successful", message)
        else:
            self.upload_status_var.set(f"❌ {message}")
            messagebox.showerror("Upload Failed", message)
    
    def refresh_status(self):
        """Refresh processing status"""
        try:
            # Clear existing text
            self.status_text.configure(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            
            # Add sample status (replace with actual status logic)
            status_info = f"""
Processing Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}

Recent Jobs:
• Job #14: Completed successfully (4 companies processed)
• Job #13: Processing (LinkedIn scraping in progress)
• Job #12: Queued (Waiting to start)

System Status:
• Auto-processing: Enabled
• LinkedIn Scraper: Active
• Database: Connected
• User: {self.user_info['username']} ({self.user_info['role']})

Total Companies Processed Today: 12
Success Rate: 95%
"""
            
            self.status_text.insert(tk.END, status_info)
            self.status_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Status Error", f"Failed to refresh status: {str(e)}")
    
    def create_user(self):
        """Create new user account"""
        username = self.new_username_var.get().strip()
        password = self.new_password_var.get()
        email = self.new_email_var.get().strip()
        role = self.new_role_var.get()
        
        if not username or not password:
            messagebox.showwarning("Invalid Input", "Username and password are required.")
            return
        
        result = auth_manager.create_user(username, password, email, role)
        
        if result["success"]:
            messagebox.showinfo("User Created", f"User '{username}' created successfully!")
            # Clear form
            self.new_username_var.set("")
            self.new_password_var.set("")
            self.new_email_var.set("")
            self.new_role_var.set("user")
        else:
            messagebox.showerror("User Creation Failed", result["message"])
    
    def refresh_login_attempts(self):
        """Refresh login attempts display"""
        try:
            attempts = auth_manager.get_login_attempts(20)
            
            self.attempts_text.configure(state=tk.NORMAL)
            self.attempts_text.delete(1.0, tk.END)
            
            self.attempts_text.insert(tk.END, f"Recent Login Attempts ({len(attempts)} entries)\\n")
            self.attempts_text.insert(tk.END, "=" * 70 + "\\n\\n")
            
            for attempt in attempts:
                status = "✅ SUCCESS" if attempt["success"] else "❌ FAILED"
                line = f"{attempt['attempt_time']} | {attempt['username']} | {attempt['ip_address']} | {status}\\n"
                self.attempts_text.insert(tk.END, line)
            
            self.attempts_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error refreshing login attempts: {e}")
    
    def start_session_timer(self):
        """Start session validation timer"""
        def check_session():
            if not self.validate_session():
                messagebox.showwarning("Session Expired", 
                                     "Your session has expired. Please login again.")
                self.logout()
            else:
                # Schedule next check in 5 minutes
                self.root.after(300000, check_session)
        
        # Start first check in 5 minutes
        self.root.after(300000, check_session)
    
    def logout(self):
        """Logout user and return to login screen"""
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        
        if result:
            # Logout from auth manager
            auth_manager.logout(self.session_token)
            
            # Close main window
            self.root.quit()
            
            # Show login window again
            from gui.login_gui import LoginWindow
            login_app = LoginWindow()
            login_app.run()
    
    def on_closing(self):
        """Handle window closing"""
        result = messagebox.askyesno("Exit Application", 
                                   "Are you sure you want to exit?\\n\\nThis will end your session.")
        
        if result:
            # Logout
            auth_manager.logout(self.session_token)
            self.root.quit()
    
    def run(self):
        """Start the authenticated application"""
        if self.root:
            self.root.mainloop()

def main():
    """Main entry point"""
    # This should normally be called from login_gui
    print("⚠️  This application requires authentication.")
    print("Please run login_gui.py to access the application.")

if __name__ == "__main__":
    main()