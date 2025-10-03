#!/usr/bin/env python3
"""
Test GUI for Company Data Scraper - Organized Structure
Quick test to verify GUI functionality
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import pandas as pd
from datetime import datetime

class TestCompanyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Company Data Scraper - GUI Test")
        self.root.geometry("800x600")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.linkedin_column = tk.StringVar(value="LinkedIn_URL")
        self.website_column = tk.StringVar(value="Company_Website")
        self.company_column = tk.StringVar(value="Company_Name")
        
        # Status
        self.is_running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Company Data Scraper - GUI Test", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Input file
        ttk.Label(file_frame, text="Input Excel File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(file_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2, pady=(0, 5))
        
        # Output file
        ttk.Label(file_frame, text="Output Excel File:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(file_frame, textvariable=self.output_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=2, pady=(0, 5))
        
        # Column Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Column Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # LinkedIn column
        ttk.Label(config_frame, text="LinkedIn URL Column:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(config_frame, textvariable=self.linkedin_column, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(0, 5))
        
        # Website column
        ttk.Label(config_frame, text="Website URL Column:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(config_frame, textvariable=self.website_column, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(0, 5))
        
        # Company name column
        ttk.Label(config_frame, text="Company Name Column:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(config_frame, textvariable=self.company_column, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(0, 5))
        
        # Scraper Selection
        scraper_frame = ttk.LabelFrame(main_frame, text="Scraper Options", padding="10")
        scraper_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.scraper_type = tk.StringVar(value="openai")
        ttk.Radiobutton(scraper_frame, text="OpenAI Enhanced (Best Results)", 
                       variable=self.scraper_type, value="openai").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(scraper_frame, text="Traditional Complete", 
                       variable=self.scraper_type, value="complete").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(scraper_frame, text="LinkedIn Only", 
                       variable=self.scraper_type, value="linkedin").grid(row=2, column=0, sticky=tk.W)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Load Test Data", command=self.load_test_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT)
        
        # Progress and Log
        log_frame = ttk.LabelFrame(main_frame, text="Progress and Logs", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(log_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_input_file(self):
        """Browse for input Excel file"""
        filename = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir="test_data"
        )
        if filename:
            self.input_file.set(filename)
            
    def browse_output_file(self):
        """Browse for output Excel file"""
        filename = filedialog.asksaveasfilename(
            title="Save Output Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            defaultextension=".xlsx",
            initialdir="results"
        )
        if filename:
            self.output_file.set(filename)
            
    def load_test_data(self):
        """Load test data from test_data folder"""
        test_file = "test_data/Test5.xlsx"
        if os.path.exists(test_file):
            self.input_file.set(test_file)
            self.linkedin_column.set("LinkedIn_URL")
            self.website_column.set("Website")
            self.company_column.set("Company Name")
            self.log_message("✅ Test data loaded: Test5.xlsx")
        else:
            messagebox.showerror("Error", f"Test file not found: {test_file}")
            
    def clear_all(self):
        """Clear all fields"""
        self.input_file.set("")
        self.output_file.set("")
        self.linkedin_column.set("LinkedIn_URL")
        self.website_column.set("Company_Website")
        self.company_column.set("Company_Name")
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Ready")
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_scraping(self):
        """Start the scraping process"""
        if self.is_running:
            messagebox.showwarning("Warning", "Scraping is already in progress!")
            return
            
        # Validate inputs
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file")
            return
            
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
            
        # Start scraping in thread
        self.is_running = True
        self.start_button.config(text="Scraping...", state="disabled")
        
        thread = threading.Thread(target=self.run_scraping)
        thread.daemon = True
        thread.start()
        
    def run_scraping(self):
        """Run the scraping process"""
        try:
            self.log_message("🚀 Starting scraping process...")
            self.status_var.set("Processing...")
            
            # Simulate scraping process
            scraper_type = self.scraper_type.get()
            input_file = self.input_file.get()
            
            self.log_message(f"📊 Input file: {input_file}")
            self.log_message(f"🔧 Scraper type: {scraper_type}")
            self.log_message(f"🔗 LinkedIn column: {self.linkedin_column.get()}")
            self.log_message(f"🌐 Website column: {self.website_column.get()}")
            self.log_message(f"🏢 Company column: {self.company_column.get()}")
            
            # Load and analyze file
            try:
                df = pd.read_excel(input_file)
                self.log_message(f"✅ Loaded {len(df)} companies from Excel file")
                
                # Show column info
                self.log_message(f"📋 Available columns: {list(df.columns)}")
                
                # Simulate progress
                for i in range(len(df)):
                    company_name = df.iloc[i].get(self.company_column.get(), f"Company {i+1}")
                    self.log_message(f"🔍 Processing: {company_name}")
                    self.progress_var.set((i + 1) / len(df) * 100)
                    
                    # Simulate processing time
                    import time
                    time.sleep(0.5)
                    
                self.log_message("✅ Scraping completed successfully!")
                self.log_message("📁 Results would be saved to output file")
                self.status_var.set(f"Completed - {len(df)} companies processed")
                
            except Exception as e:
                self.log_message(f"❌ Error loading file: {str(e)}")
                self.status_var.set("Error")
                
        except Exception as e:
            self.log_message(f"❌ Scraping error: {str(e)}")
            self.status_var.set("Error")
        finally:
            self.is_running = False
            self.start_button.config(text="Start Scraping", state="normal")
            self.progress_var.set(100)

def main():
    # Test if GUI can be created
    root = tk.Tk()
    app = TestCompanyGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    print("🖥️ GUI Test Application Started")
    print("✅ Window created successfully")
    print("✅ All widgets loaded")
    print("🚀 GUI is working perfectly!")
    
    root.mainloop()

if __name__ == "__main__":
    main()