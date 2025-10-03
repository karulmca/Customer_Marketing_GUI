"""
Registration Button Verification Script
This script will help verify that the registration functionality is working
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_registration_visibility():
    """Test and demonstrate registration button visibility"""
    
    print("🔍 REGISTRATION BUTTON VISIBILITY TEST")
    print("=" * 50)
    
    root = tk.Tk()
    root.title("Registration Test - Look for the Button!")
    root.geometry("500x400")
    root.configure(bg='#f0f0f0')
    
    # Main instructions
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header
    ttk.Label(main_frame, text="🔍 Registration Button Location Test", 
              font=("Arial", 16, "bold")).pack(pady=(0, 20))
    
    # Instructions
    instructions = [
        "✅ The login GUI should show these elements in order:",
        "",  
        "1. 🏢 Company logo and title at the top",
        "2. 📝 Username field (default: admin)",
        "3. 🔒 Password field (default: admin123)", 
        "4. ☑️ Show password checkbox",
        "5. 🔵 'Sign In' button (blue, prominent)",
        "6. ➖ Horizontal separator line",
        "7. 💭 Text: 'Don't have an account?'",
        "8. 🆕 'Register New User' button (BLUE TEXT, with icon)",
        "9. 📄 Footer with demo credentials",
        "",
        "📍 LOCATION: The registration button is BETWEEN",
        "   the login button and the footer section!",
        "",
        "🎯 WHAT TO LOOK FOR:",
        "   • Blue text button with emoji: '🆕 Register New User'",
        "   • Located below the login form",
        "   • Above the 'Demo Credentials' section"
    ]
    
    for instruction in instructions:
        if instruction.startswith("✅") or instruction.startswith("📍") or instruction.startswith("🎯"):
            ttk.Label(main_frame, text=instruction, font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        elif instruction == "":
            ttk.Label(main_frame, text="").pack(pady=2)
        else:
            ttk.Label(main_frame, text=instruction, font=("Arial", 9)).pack(anchor=tk.W, padx=20, pady=1)
    
    # Test button
    ttk.Button(main_frame, text="🚀 Launch Actual Login GUI", 
               command=lambda: launch_login_gui()).pack(pady=20)
    
    def launch_login_gui():
        """Launch the actual login GUI"""
        import subprocess
        import os
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        subprocess.Popen([sys.executable, "gui/login_gui.py"])
        messagebox.showinfo("Login GUI Launched", 
                          "✅ Login GUI launched!\n\n"
                          "🔍 Look for the '🆕 Register New User' button\n"
                          "📍 It should be below the login form")
    
    print("📋 Instructions displayed in GUI window")
    print("🚀 Click 'Launch Actual Login GUI' to test")
    print("🔍 Look for the blue '🆕 Register New User' button!")
    
    root.mainloop()

if __name__ == "__main__":
    test_registration_visibility()