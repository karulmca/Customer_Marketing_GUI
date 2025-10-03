#!/usr/bin/env python3
"""
Simple test GUI to verify tkinter is working
"""

import tkinter as tk
from tkinter import ttk, messagebox

class SimpleTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Test GUI - Verify Working")
        self.root.geometry("400x300")
        
        # Make window stay on top initially
        self.root.attributes('-topmost', True)
        self.root.after(2000, lambda: self.root.attributes('-topmost', False))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 GUI Test Successful!", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=20)
        
        # Info
        info_label = ttk.Label(main_frame, text="If you can see this window,\nthe GUI system is working correctly!")
        info_label.grid(row=1, column=0, pady=10)
        
        # Test button
        test_button = ttk.Button(main_frame, text="Click Me to Test", 
                                command=self.test_click)
        test_button.grid(row=2, column=0, pady=20)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready to test...")
        self.status_label.grid(row=3, column=0, pady=10)
        
    def test_click(self):
        self.status_label.config(text="✅ Button click works!")
        messagebox.showinfo("Success", "GUI is functioning properly!")

if __name__ == "__main__":
    print("🚀 Starting Simple Test GUI...")
    print("📋 Look for a window titled 'Simple Test GUI - Verify Working'")
    
    root = tk.Tk()
    app = SimpleTestGUI(root)
    
    print("✅ GUI Created - Window should be visible now")
    print("🔄 Starting GUI main loop...")
    
    root.mainloop()
    
    print("🏁 GUI Closed")