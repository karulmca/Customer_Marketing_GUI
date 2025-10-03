"""
Debug Login GUI - Simplified version to ensure registration button is visible
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_debug_login():
    """Create a simplified login GUI to debug the registration button"""
    
    root = tk.Tk()
    root.title("DEBUG: Company Data Scraper - Login")
    root.geometry("500x750")
    root.configure(bg='#f0f0f0')
    
    # Create main container with scrollbar
    canvas = tk.Canvas(root, bg='#f0f0f0')
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack scrollbar and canvas
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Main content frame
    main_frame = ttk.Frame(scrollable_frame, padding=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header section
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill=tk.X, pady=(0, 30))
    
    # Logo
    logo_frame = ttk.Frame(header_frame)
    logo_frame.pack(pady=(0, 10))
    logo_label = ttk.Label(logo_frame, text="🏢", font=("Arial", 48))
    logo_label.pack()
    
    # Title
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
    form_frame = ttk.LabelFrame(main_frame, text="Login", padding=25)
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
    login_button.pack(fill=tk.X, pady=(0, 15))
    
    # === REGISTRATION SECTION ===
    print("🔧 Creating registration section...")
    
    # Large separator for visibility
    separator = ttk.Separator(form_frame, orient='horizontal')
    separator.pack(fill=tk.X, pady=(15, 15))
    
    # Registration header
    reg_header = ttk.Label(form_frame, text="New User?", 
                          font=("Arial", 12, "bold"), foreground="blue")
    reg_header.pack(pady=(5, 5))
    
    # "Don't have an account?" text
    no_account_label = ttk.Label(form_frame, text="Don't have an account?", 
                                font=("Arial", 10), foreground="gray")
    no_account_label.pack(pady=(0, 10))
    
    # BIG VISIBLE REGISTRATION BUTTON
    register_button = ttk.Button(form_frame, 
                                text="REGISTER NEW USER", 
                                command=lambda: handle_registration(),
                                style="BigRegister.TButton")
    register_button.pack(fill=tk.X, pady=(5, 15))
    
    # Debug button info
    debug_label = ttk.Label(form_frame, 
                           text="👆 REGISTRATION BUTTON ABOVE 👆", 
                           font=("Arial", 9, "bold"), 
                           foreground="red", 
                           background="yellow")
    debug_label.pack(pady=5)
    
    # Configure button styles
    style = ttk.Style()
    style.configure("Login.TButton", font=("Arial", 12, "bold"), padding=12)
    style.configure("BigRegister.TButton", 
                   font=("Arial", 14, "bold"), 
                   padding=15,
                   relief="raised",
                   borderwidth=3)
    
    # Status area
    status_label = ttk.Label(form_frame, text="", font=("Arial", 10))
    status_label.pack(pady=(10, 0))
    
    # Footer
    footer_frame = ttk.Frame(main_frame)
    footer_frame.pack(fill=tk.X, pady=(20, 0))
    
    info_frame = ttk.LabelFrame(footer_frame, text="Demo Credentials", padding=15)
    info_frame.pack(fill=tk.X)
    
    ttk.Label(info_frame, text="Default Login:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
    ttk.Label(info_frame, text="Username: admin", font=("Arial", 9)).pack(anchor=tk.W)
    ttk.Label(info_frame, text="Password: admin123", font=("Arial", 9)).pack(anchor=tk.W)
    
    def handle_registration():
        """Handle registration button click"""
        messagebox.showinfo("Registration", 
                          "✅ REGISTRATION BUTTON CLICKED!\n\n"
                          "This confirms the button is working.\n"
                          "In the actual GUI, this opens the\n"
                          "registration form window.")
        print("🎯 Registration button clicked successfully!")
    
    # Bind mousewheel to canvas for scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    print("✅ DEBUG LOGIN GUI CREATED")
    print("=" * 50)
    print("🔍 REGISTRATION BUTTON FEATURES:")
    print("   • Text: 'REGISTER NEW USER'")
    print("   • Large size with bold font")
    print("   • Full width button")
    print("   • Raised border style")
    print("   • Located below login form")
    print("   • Red debug label below it")
    print("")
    print("📍 BUTTON LOCATION:")
    print("   1. Below 'Sign In' button")
    print("   2. After horizontal separator")
    print("   3. Below 'Don't have an account?' text")
    print("   4. Above footer section")
    print("")
    print("🖼️ Window is resizable and scrollable")
    print("💡 Click the button to test functionality!")
    
    root.mainloop()

if __name__ == "__main__":
    create_debug_login()