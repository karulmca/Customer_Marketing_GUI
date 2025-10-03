"""
Test script to debug registration button visibility in login GUI
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_login_layout():
    """Test login layout to see registration button"""
    root = tk.Tk()
    root.title("Login Layout Test")
    root.geometry("450x600")
    root.configure(bg='#f0f0f0')
    
    # Main container
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    # Header section
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill=tk.X, pady=(0, 30))
    
    # Logo and title
    logo_frame = ttk.Frame(header_frame)
    logo_frame.pack(pady=(0, 10))
    
    logo_label = ttk.Label(logo_frame, text="🏢", font=("Arial", 48))
    logo_label.pack()
    
    title_label = ttk.Label(header_frame, text="Company Data Scraper", 
                           font=("Arial", 24, "bold"))
    title_label.pack()
    
    subtitle_label = ttk.Label(header_frame, text="LinkedIn Data Extraction Platform", 
                              font=("Arial", 12), foreground="gray")
    subtitle_label.pack(pady=(5, 0))
    
    instruction_label = ttk.Label(header_frame, text="Please sign in to continue", 
                                 font=("Arial", 10), foreground="gray")
    instruction_label.pack(pady=(20, 0))
    
    # Login form section
    form_frame = ttk.LabelFrame(main_frame, text="Login", padding=20)
    form_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Username field
    ttk.Label(form_frame, text="Username:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
    username_entry = ttk.Entry(form_frame, font=("Arial", 12), width=30)
    username_entry.pack(fill=tk.X, pady=(0, 15))
    username_entry.insert(0, "admin")
    
    # Password field
    ttk.Label(form_frame, text="Password:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
    password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 12), width=30)
    password_entry.pack(fill=tk.X, pady=(0, 15))
    password_entry.insert(0, "admin123")
    
    # Show password checkbox
    show_password_var = tk.BooleanVar()
    show_password_cb = ttk.Checkbutton(form_frame, text="Show password", 
                                      variable=show_password_var)
    show_password_cb.pack(anchor=tk.W, pady=(0, 20))
    
    # Login button
    login_button = ttk.Button(form_frame, text="Sign In", 
                             style="Login.TButton")
    login_button.pack(fill=tk.X, pady=(0, 10))
    
    # === REGISTRATION SECTION (This is what you should see!) ===
    register_frame = ttk.Frame(form_frame)
    register_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Separator line
    separator = ttk.Separator(register_frame, orient='horizontal')
    separator.pack(fill=tk.X, pady=(0, 10))
    
    # "Don't have an account?" text
    no_account_label = ttk.Label(register_frame, text="Don't have an account?", 
                                font=("Arial", 10), foreground="gray")
    no_account_label.pack()
    
    # Register button - THIS IS THE BUTTON YOU'RE LOOKING FOR!
    register_button = ttk.Button(register_frame, text="Register New User", 
                                command=lambda: print("🎯 REGISTRATION BUTTON CLICKED!"))
    register_button.pack(pady=(5, 0))
    
    # Configure styles
    style = ttk.Style()
    style.configure("Login.TButton", font=("Arial", 12, "bold"), padding=10)
    
    # Status label
    status_label = ttk.Label(form_frame, text="", font=("Arial", 10), foreground="red")
    status_label.pack(pady=(10, 0))
    
    # Footer section
    footer_frame = ttk.Frame(main_frame)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    info_frame = ttk.LabelFrame(footer_frame, text="Demo Credentials", padding=10)
    info_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(info_frame, text="Default Login:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
    ttk.Label(info_frame, text="Username: admin", font=("Arial", 9)).pack(anchor=tk.W)
    ttk.Label(info_frame, text="Password: admin123", font=("Arial", 9)).pack(anchor=tk.W)
    
    print("🔍 LOGIN LAYOUT TEST")
    print("=" * 50)
    print("✅ Window size: 450x600")
    print("✅ Main sections created:")
    print("   📋 Header with logo and title")
    print("   🔐 Login form with username/password")
    print("   🎯 REGISTRATION SECTION with button")
    print("   📄 Footer with demo credentials")
    print("")
    print("🔎 LOOK FOR:")
    print("   1. A horizontal line separator")
    print("   2. Text: 'Don't have an account?'")
    print("   3. Button: 'Register New User'")
    print("")
    print("📍 The registration button should be BELOW the login button")
    print("   and ABOVE the footer section!")
    
    root.mainloop()

if __name__ == "__main__":
    test_login_layout()