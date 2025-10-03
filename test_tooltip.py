#!/usr/bin/env python3
"""
Test Tooltip Functionality
Demonstrates the info icon with hover tooltip
"""

import tkinter as tk
from tkinter import ttk

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
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 10, "normal"), wraplength=400)
        label.pack(ipadx=1)
        
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def test_tooltip():
    """Test the tooltip functionality"""
    root = tk.Tk()
    root.title("Tooltip Test")
    root.geometry("600x300")
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title with info icon (like in the actual GUI)
    title_frame = ttk.Frame(main_frame)
    title_frame.pack(fill=tk.X, pady=(0, 20))
    
    title_label = ttk.Label(title_frame, text="📁 File Upload - JSON Storage for Scheduled Processing", 
                           font=('Arial', 16, 'bold'))
    title_label.pack(side=tk.LEFT)
    
    # Info icon with tooltip
    info_icon = ttk.Label(title_frame, text=" ℹ️", font=('Arial', 14), 
                         cursor="question_arrow", foreground="#007ACC")
    info_icon.pack(side=tk.LEFT, padx=(10, 0))
    
    # Create tooltip for info icon
    info_text = """🔄 How It Works:

1. Upload Excel/CSV files → Stored as JSON in 'file_upload' table
2. Files remain in 'pending' status until processed  
3. Scheduled jobs process the JSON data → Extract to 'company_data' table
4. Monitor processing status and manage jobs through GUI tabs

💡 This workflow allows for better job management and processing control."""
    
    ToolTip(info_icon, info_text)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="🖱️ Hover over the ℹ️ icon next to the title to see the tooltip!",
                           font=('Arial', 12),
                           foreground="#666666")
    instructions.pack(pady=20)
    
    # Additional examples
    example_frame = ttk.LabelFrame(main_frame, text="Other Tooltip Examples", padding="10")
    example_frame.pack(fill=tk.X, pady=20)
    
    # Example buttons with tooltips
    btn1 = ttk.Button(example_frame, text="🔄 Process Files")
    btn1.pack(side=tk.LEFT, padx=(0, 10))
    ToolTip(btn1, "Click to start processing uploaded files\nThis will run the LinkedIn scraper on pending files")
    
    btn2 = ttk.Button(example_frame, text="📊 View Stats")
    btn2.pack(side=tk.LEFT, padx=(0, 10))
    ToolTip(btn2, "View processing statistics\nShows success rates, timing, and errors")
    
    btn3 = ttk.Button(example_frame, text="⚙️ Settings")
    btn3.pack(side=tk.LEFT)
    ToolTip(btn3, "Configure scraper settings\nAdjust delays, API keys, and processing options")
    
    print("🧪 Tooltip Test Window Opened")
    print("📋 Instructions:")
    print("1. Hover over the ℹ️ icon next to the title")
    print("2. See the detailed tooltip appear")
    print("3. Try hovering over other buttons for examples")
    print("4. Close window when done testing")
    
    root.mainloop()

if __name__ == "__main__":
    print("🚀 Testing Tooltip Functionality")
    print("=" * 50)
    test_tooltip()
    print("✅ Tooltip test completed")