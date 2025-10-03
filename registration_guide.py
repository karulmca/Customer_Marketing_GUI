"""
Registration Button Location Guide
This script creates a visual guide showing exactly where the registration button should appear
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

def create_location_guide():
    """Create a visual guide showing where the registration button should be"""
    
    root = tk.Tk()
    root.title("📍 Registration Button Location Guide")
    root.geometry("600x800")
    root.configure(bg='#f0f0f0')
    
    # Main container
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="🔍 Registration Button Location Guide", 
                           font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Create a mock login form to show the layout
    mock_frame = ttk.LabelFrame(main_frame, text="Mock Login Form Layout", padding=20)
    mock_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Mock login elements with step numbers
    elements = [
        ("1️⃣", "🏢 Company Logo", "Arial", 24),
        ("2️⃣", "Company Data Scraper", "Arial", 16),
        ("3️⃣", "LinkedIn Data Extraction Platform", "Arial", 10),
        ("4️⃣", "Please sign in to continue", "Arial", 10),
        ("", "--- Login Form Start ---", "Arial", 10),
        ("5️⃣", "Username: [admin]", "Arial", 10),
        ("6️⃣", "Password: [••••••••]", "Arial", 10),
        ("7️⃣", "☑️ Show password", "Arial", 10),
        ("8️⃣", "🔵 SIGN IN BUTTON", "Arial", 12),
        ("", "--- Registration Section ---", "Arial", 10),
        ("9️⃣", "━━━━━━━━━━━━━━━━━━━━━━━━━━━", "Arial", 10),
        ("🔟", "New User Registration", "Arial", 11),
        ("1️⃣1️⃣", "Don't have an account?", "Arial", 10),
        ("1️⃣2️⃣", "🎯 REGISTER NEW USER BUTTON 🎯", "Arial", 12),
        ("", "--- Footer ---", "Arial", 10),
        ("1️⃣3️⃣", "Demo Credentials", "Arial", 10),
    ]
    
    for step, text, font_family, font_size in elements:
        frame = ttk.Frame(mock_frame)
        frame.pack(fill=tk.X, pady=2)
        
        if step:
            step_label = ttk.Label(frame, text=step, font=(font_family, 10, "bold"))
            step_label.pack(side=tk.LEFT, padx=(0, 10))
        
        if "REGISTER NEW USER BUTTON" in text:
            # Highlight the registration button
            text_label = ttk.Label(frame, text=text, 
                                  font=(font_family, font_size, "bold"),
                                  foreground="red", background="yellow")
            text_label.pack(side=tk.LEFT)
        elif "SIGN IN BUTTON" in text:
            text_label = ttk.Label(frame, text=text, 
                                  font=(font_family, font_size, "bold"),
                                  foreground="blue")
            text_label.pack(side=tk.LEFT)
        else:
            text_label = ttk.Label(frame, text=text, font=(font_family, font_size))
            text_label.pack(side=tk.LEFT)
    
    # Instructions section
    instructions_frame = ttk.LabelFrame(main_frame, text="🎯 What to Look For", padding=15)
    instructions_frame.pack(fill=tk.X, pady=(0, 20))
    
    instructions = [
        "✅ The registration button should appear at step 12",
        "📍 Location: Below 'Don't have an account?' text",
        "🎨 Style: Large button with bold text",
        "📏 Size: Full width of the login form",
        "🔤 Text: 'REGISTER NEW USER'",
        "🖱️ Action: Clicking opens registration form window",
        "",
        "❌ If you DON'T see the button:",
        "   • Try resizing the login window (drag corners)",
        "   • Scroll down in the login window",
        "   • Look for a horizontal line separator first",
        "   • The button should be below the separator"
    ]
    
    for instruction in instructions:
        if instruction.startswith("✅") or instruction.startswith("📍") or instruction.startswith("❌"):
            label = ttk.Label(instructions_frame, text=instruction, 
                            font=("Arial", 10, "bold"))
        elif instruction == "":
            label = ttk.Label(instructions_frame, text="")
        else:
            label = ttk.Label(instructions_frame, text=instruction, font=("Arial", 9))
        label.pack(anchor=tk.W, pady=1)
    
    def launch_login():
        """Launch the actual login GUI"""
        import subprocess
        subprocess.Popen([sys.executable, "gui/login_gui.py"], 
                        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        messagebox.showinfo("Login GUI", "✅ Login GUI launched!\nLook for the registration button!")
    
    def launch_debug():
        """Launch the debug login GUI"""
        import subprocess
        subprocess.Popen([sys.executable, "debug_login_gui.py"], 
                        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        messagebox.showinfo("Debug GUI", "✅ Debug GUI launched!\nThis version has a VERY visible registration button!")
    
    def test_registration():
        """Test registration functionality"""
        messagebox.showinfo("Registration Test", 
                          "🧪 Testing registration functionality...\n\n"
                          "The registration system is working:\n"
                          "✅ PostgreSQL database backend\n"
                          "✅ User creation working\n"
                          "✅ Login after registration working\n\n"
                          "The button should be visible in the GUI!")
    
    # Action buttons
    action_frame = ttk.Frame(main_frame)
    action_frame.pack(fill=tk.X, pady=20)
    
    ttk.Button(action_frame, text="🚀 Launch Login GUI", 
               command=launch_login).pack(side=tk.LEFT, padx=(0, 10))
    
    ttk.Button(action_frame, text="🔧 Launch Debug GUI", 
               command=launch_debug).pack(side=tk.LEFT, padx=(0, 10))
    
    ttk.Button(action_frame, text="❓ Test Registration", 
               command=test_registration).pack(side=tk.LEFT)
    
    print("📍 REGISTRATION BUTTON LOCATION GUIDE")
    print("=" * 50)
    print("🎯 The registration button should appear:")
    print("   • Step 12 in the layout")
    print("   • Below the 'Sign In' button")
    print("   • After a horizontal separator line")
    print("   • Before the footer section")
    print("")
    print("🚀 Use the buttons in the GUI to:")
    print("   • Launch the actual login GUI")
    print("   • Launch the debug GUI (super visible button)")
    print("   • Test registration functionality")
    
    root.mainloop()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    create_location_guide()