"""
Login GUI Application
Secure login interface with authentication
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import time
from datetime import datetime

# Optional PIL import for image support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.user_auth import UserAuthenticator

class LoginWindow:
    """Secure login window with authentication"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.session_token = None
        self.user_info = None
        
        # Initialize authentication system
        self.auth = UserAuthenticator()
        
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Company Data Scraper - Login")
        self.root.geometry("500x800")  # Further increased height to show registration button
        self.root.resizable(True, True)  # Allow resizing to see all content
        self.root.minsize(480, 750)  # Set minimum size to ensure button visibility
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"500x800+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.root.configure(bg='#f0f0f0')
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Debug: Print window creation
        print("🔍 Login window created with registration section")
        print("📍 Look for the 'REGISTER NEW USER' button below!")
        print(f"🖼️ Window size: 500x800 (resizable)")
        print("🎯 Registration button should now be fully visible")
    
    def create_widgets(self):
        """Create and layout all widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header section
        self.create_header(main_frame)
        
        # Login form section
        self.create_login_form(main_frame)
        
        # Footer section
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Create header section with logo and title"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Company logo placeholder
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(pady=(0, 20))
        
        # Try to load logo image if PIL is available
        if PIL_AVAILABLE:
            try:
                logo_img = Image.open("assets/logo.png")
                logo_img = logo_img.resize((80, 80), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(logo_frame, image=self.logo_photo)
                logo_label.pack()
            except:
                # Fallback to text logo
                logo_label = ttk.Label(logo_frame, text="🏢", font=("Arial", 48))
                logo_label.pack()
        else:
            # Text logo when PIL is not available
            logo_label = ttk.Label(logo_frame, text="🏢", font=("Arial", 48))
            logo_label.pack()
        
        # Title
        title_label = ttk.Label(header_frame, text="Company Data Scraper", 
                               font=("Arial", 24, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="LinkedIn Data Extraction Platform", 
                                  font=("Arial", 12), foreground="gray")
        subtitle_label.pack(pady=(5, 0))
        
        # Login instruction
        instruction_label = ttk.Label(header_frame, text="Please sign in to continue", 
                                     font=("Arial", 10), foreground="gray")
        instruction_label.pack(pady=(20, 0))
    
    def create_login_form(self, parent):
        """Create login form with username and password fields"""
        form_frame = ttk.LabelFrame(parent, text="Login", padding=20)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Username field
        ttk.Label(form_frame, text="Username:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.username_var = tk.StringVar(value="admin")  # Default for demo
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, 
                                       font=("Arial", 12), width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar(value="admin123")  # Default for demo
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                       show="*", font=("Arial", 12), width=30)
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Show/Hide password checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_cb = ttk.Checkbutton(form_frame, text="Show password", 
                                          variable=self.show_password_var,
                                          command=self.toggle_password_visibility)
        show_password_cb.pack(anchor=tk.W, pady=(0, 20))
        
        # Login button
        self.login_button = ttk.Button(form_frame, text="Sign In", 
                                      command=self.login_clicked, 
                                      style="Login.TButton")
        self.login_button.pack(fill=tk.X, pady=(0, 10))
        
        # Registration section - Make it very visible
        register_frame = ttk.Frame(form_frame)
        register_frame.pack(fill=tk.X, pady=(15, 10))
        
        # Large separator for better visibility
        separator = ttk.Separator(register_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 15))
        
        # Registration header
        reg_header_label = ttk.Label(register_frame, text="New User Registration", 
                                    font=("Arial", 11, "bold"), foreground="blue")
        reg_header_label.pack(pady=(0, 5))
        
        # "Don't have an account?" text
        no_account_label = ttk.Label(register_frame, text="Don't have an account?", 
                                    font=("Arial", 10), foreground="gray")
        no_account_label.pack(pady=(0, 8))
        
        # Register button - Make it VERY prominent and visible
        self.register_button = ttk.Button(register_frame, 
                                         text="REGISTER NEW USER", 
                                         command=self.show_registration_form,
                                         style="Register.TButton")
        self.register_button.pack(pady=(8, 20), fill=tk.X, ipady=8)
        
        # Debug label to confirm button is created
        debug_label = ttk.Label(register_frame, 
                               text="👆 Click above button to register 👆", 
                               font=("Arial", 8), foreground="gray")
        debug_label.pack(pady=(0, 10))
        
        # Configure button styles
        style = ttk.Style()
        style.configure("Login.TButton", font=("Arial", 12, "bold"), padding=10)
        
        # Make register button VERY visible with custom styling
        style.configure("Register.TButton", 
                       font=("Arial", 12, "bold"), 
                       padding=12,
                       relief="raised",
                       borderwidth=3)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(form_frame, textvariable=self.status_var, 
                                     font=("Arial", 10), foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # Progress bar (hidden initially)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(form_frame, variable=self.progress_var, 
                                           mode='indeterminate')
        
    def create_footer(self, parent):
        """Create compact footer with essential information"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))
        
        # Compact credentials info
        info_frame = ttk.LabelFrame(footer_frame, text="Demo Credentials", padding=8)
        info_frame.pack(fill=tk.X)
        
        # Single line for credentials
        cred_text = "Default: admin / admin123"
        ttk.Label(info_frame, text=cred_text, font=("Arial", 9, "bold")).pack()
        
        # Small warning
        ttk.Label(info_frame, text="⚠️ Change in production", 
                 font=("Arial", 8), foreground="orange").pack(pady=(2, 0))
    
    def setup_bindings(self):
        """Setup keyboard bindings"""
        self.root.bind('<Return>', lambda e: self.login_clicked())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Focus on username field
        self.username_entry.focus()
    
    def toggle_password_visibility(self):
        """Toggle password field visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
    
    def login_clicked(self):
        """Handle login button click"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.show_status("Please enter both username and password", "error")
            return
        
        # Disable login button and show progress
        self.login_button.configure(state="disabled", text="Signing In...")
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.progress_bar.start(10)
        self.show_status("Authenticating...", "info")
        
        # Perform authentication in separate thread
        threading.Thread(target=self.authenticate_user, args=(username, password), daemon=True).start()
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        try:
            # Authenticate user
            auth_result = self.auth.authenticate_user(username, password)
            
            # Update UI in main thread
            self.root.after(0, self.handle_auth_result, auth_result)
            
        except Exception as e:
            self.root.after(0, self.handle_auth_error, str(e))
    
    def handle_auth_result(self, auth_result):
        """Handle authentication result"""
        # Stop progress and re-enable button
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.login_button.configure(state="normal", text="Sign In")
        
        if auth_result["success"]:
            self.session_token = auth_result["session_token"]
            self.user_info = auth_result["user"]
            
            self.show_status(f"Welcome, {self.user_info['username']}!", "success")
            
            # Show success message
            messagebox.showinfo("Login Successful", 
                              f"Welcome, {self.user_info['username']}!\n"
                              f"Role: {self.user_info['role']}\n\n"
                              "Opening main application...")
            
            # Launch main application
            self.launch_main_application()
            
        else:
            self.show_status(auth_result["message"], "error")
            self.password_entry.select_range(0, tk.END)
            self.password_entry.focus()
    
    def handle_auth_error(self, error_message):
        """Handle authentication error"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.login_button.configure(state="normal", text="Sign In")
        self.show_status(f"Authentication error: {error_message}", "error")
    
    def show_status(self, message, status_type="info"):
        """Show status message with appropriate color"""
        colors = {
            "info": "blue",
            "success": "green", 
            "error": "red",
            "warning": "orange"
        }
        
        self.status_var.set(message)
        self.status_label.configure(foreground=colors.get(status_type, "black"))
    
    def show_registration_form(self):
        """Show user registration dialog"""
        self.create_registration_window()
    
    def create_registration_window(self):
        """Create registration window"""
        # Create new window
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Register New User")
        reg_window.geometry("480x600")  # Increased height to ensure submit button is visible
        reg_window.resizable(True, True)  # Allow resizing
        reg_window.minsize(450, 550)  # Set minimum size
        reg_window.transient(self.root)
        reg_window.grab_set()
        
        # Center the window
        reg_window.update_idletasks()
        x = (reg_window.winfo_screenwidth() // 2) - (480 // 2)
        y = (reg_window.winfo_screenheight() // 2) - (600 // 2)
        reg_window.geometry(f"480x600+{x}+{y}")
        
        print("🎯 Registration form window created - size: 480x600")
        print("📝 Look for 'Create Account' button at the bottom!")
        
        # Main frame
        main_frame = ttk.Frame(reg_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="Create New Account", 
                                font=("Arial", 18, "bold"))
        header_label.pack(pady=(0, 20))
        
        # Registration form
        form_frame = ttk.LabelFrame(main_frame, text="User Information", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Username field
        ttk.Label(form_frame, text="Username:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=username_var, font=("Arial", 12))
        username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Email field
        ttk.Label(form_frame, text="Email:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=email_var, font=("Arial", 12))
        email_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=password_var, show="*", font=("Arial", 12))
        password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Confirm password field
        ttk.Label(form_frame, text="Confirm Password:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(form_frame, textvariable=confirm_password_var, show="*", font=("Arial", 12))
        confirm_password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Role selection
        ttk.Label(form_frame, text="Role:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        role_var = tk.StringVar(value="user")
        role_frame = ttk.Frame(form_frame)
        role_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Radiobutton(role_frame, text="User", variable=role_var, value="user").pack(side=tk.LEFT)
        ttk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin").pack(side=tk.LEFT, padx=(20, 0))
        
        # Status label for registration
        reg_status_var = tk.StringVar()
        reg_status_label = ttk.Label(form_frame, textvariable=reg_status_var, 
                                    font=("Arial", 10), foreground="red")
        reg_status_label.pack(pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 10))
        
        # Register button (SUBMIT button)
        register_btn = ttk.Button(button_frame, text="✅ CREATE ACCOUNT", 
                                 command=lambda: self.process_registration(
                                     reg_window, username_var.get(), email_var.get(),
                                     password_var.get(), confirm_password_var.get(),
                                     role_var.get(), reg_status_var),
                                 style="Register.TButton")
        register_btn.pack(side=tk.LEFT, padx=(0, 15), fill=tk.X, expand=True, ipady=8)
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="❌ CANCEL", 
                               command=reg_window.destroy)
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        # Debug label to confirm buttons are visible
        debug_frame = ttk.Frame(main_frame)
        debug_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(debug_frame, text="👆 SUBMIT BUTTON ABOVE (CREATE ACCOUNT) 👆", 
                 font=("Arial", 9, "bold"), foreground="blue").pack()
        
        # Focus on username field
        username_entry.focus()
        
        # Bind Enter key
        reg_window.bind('<Return>', lambda e: register_btn.invoke())
        reg_window.bind('<Escape>', lambda e: reg_window.destroy())
    
    def process_registration(self, window, username, email, password, confirm_password, role, status_var):
        """Process user registration"""
        # Validation
        if not username or not email or not password:
            status_var.set("All fields are required")
            return
        
        if password != confirm_password:
            status_var.set("Passwords do not match")
            return
        
        if len(password) < 6:
            status_var.set("Password must be at least 6 characters")
            return
        
        if "@" not in email:
            status_var.set("Please enter a valid email address")
            return
        
        try:
            # Create user account (note: method signature is username, password, email, role)
            result = self.auth.create_user(username, password, email, role)
            
            if result.get("success"):
                messagebox.showinfo("Registration Successful", 
                                  f"Account created successfully!\n\n"
                                  f"Username: {username}\n"
                                  f"Email: {email}\n"
                                  f"Role: {role.title()}\n\n"
                                  "You can now login with your credentials.")
                window.destroy()
                
                # Pre-fill login form with new username
                self.username_var.set(username)
                self.password_var.set("")  # Clear password for security
                self.password_entry.focus()
                
            else:
                status_var.set(result.get("message", "Registration failed"))
                
        except Exception as e:
            status_var.set(f"Registration error: {str(e)}")
    
    def launch_main_application(self):
        """Launch the main file processing application"""
        try:
            # Close login window
            self.root.withdraw()
            
            # Launch your existing GUI with authentication context
            self.launch_existing_gui_with_auth()
            
        except Exception as e:
            messagebox.showerror("Application Error", 
                               f"Failed to launch main application:\n{str(e)}")
            self.root.deiconify()  # Show login window again
    
    def launch_existing_gui_with_auth(self):
        """Launch the existing file_upload_json_gui.py with authentication"""
        try:
            # Store session info in a temporary file for the GUI to read
            import tempfile
            import json
            
            session_data = {
                "token": self.session_token,
                "session_token": self.session_token,  # Keep for backward compatibility
                "user_info": self.user_info,
                "login_time": datetime.now().isoformat(),
                "timestamp": time.time()
            }
            
            # Create temporary session file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(session_data, f)
                session_file_path = f.name
            
            # Store session file path for cleanup
            self.session_file_path = session_file_path
            
            # Launch existing GUI as subprocess with session file
            import subprocess
            self.gui_process = subprocess.Popen([
                sys.executable, 
                "gui/file_upload_json_gui.py", 
                "--auth-session", 
                session_file_path
            ])
            
            print(f"🚀 Launched authenticated GUI for user: {self.user_info['username']}")
            
            # Monitor the GUI process
            self.monitor_gui_process()
            
        except Exception as e:
            print(f"❌ Error launching GUI: {e}")
            messagebox.showerror("Launch Error", f"Failed to launch GUI:\n{str(e)}")
            self.root.deiconify()
    
    def monitor_gui_process(self):
        """Monitor the GUI process and handle when it closes"""
        def check_process():
            if hasattr(self, 'gui_process') and self.gui_process:
                # Check if process is still running
                poll_result = self.gui_process.poll()
                if poll_result is not None:
                    # Process has ended
                    print(f"📋 Main GUI closed (exit code: {poll_result})")
                    self.cleanup_and_exit()
                else:
                    # Process still running, check again in 1 second
                    self.root.after(1000, check_process)
            else:
                # No process to monitor
                self.cleanup_and_exit()
        
        # Start monitoring
        self.root.after(1000, check_process)
    
    def cleanup_and_exit(self):
        """Cleanup session and exit application"""
        try:
            # Logout from auth system
            if hasattr(self, 'session_token') and self.session_token:
                # Clean up session (UserAuthenticator handles session cleanup automatically)
                print(f"🔐 Logged out user: {self.user_info['username'] if self.user_info else 'Unknown'}")
            
            # Clean up session file
            if hasattr(self, 'session_file_path') and os.path.exists(self.session_file_path):
                os.unlink(self.session_file_path)
                print("🗑️ Session file cleaned up")
            
            # Terminate GUI process if still running
            if hasattr(self, 'gui_process') and self.gui_process:
                try:
                    self.gui_process.terminate()
                    print("🔒 GUI process terminated")
                except:
                    pass
            
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
        
        finally:
            # Exit login application
            print("👋 Session ended, closing login application")
            self.root.quit()
    
    def run(self):
        """Start the login application"""
        try:
            print("🔐 Starting login application...")
            print("📋 Default credentials: admin / admin123")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Login application closed by user")
        except Exception as e:
            print(f"❌ Error running login application: {e}")
            messagebox.showerror("Application Error", f"Login application error:\n{str(e)}")

def main():
    """Main entry point"""
    try:
        # Create and run login application
        login_app = LoginWindow()
        login_app.run()
        
    except Exception as e:
        print(f"❌ Failed to start login application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()