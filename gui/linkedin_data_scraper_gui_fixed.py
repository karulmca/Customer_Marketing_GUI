#!/usr/bin/env python3
"""
Enhanced GUI for LinkedIn Company Data Scraper - Organized Structure
Extracts both Company Size AND Industry from LinkedIn + Revenue from websites
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import pandas as pd
import logging
from datetime import datetime
import subprocess

# Setup logging for GUI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedLinkedInGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Company Data Scraper - Enhanced (Size + Industry + Revenue)")
        self.root.geometry("1000x800")
        
        # Force window to be visible and on top initially
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        # Remove topmost after 3 seconds
        self.root.after(3000, lambda: self.root.attributes('-topmost', False))
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.linkedin_column = tk.StringVar(value="LinkedIn_URL")
        self.website_column = tk.StringVar(value="Company_Website")
        self.company_column = tk.StringVar(value="Company_Name")
        self.wait_min = tk.IntVar(value=10)
        self.wait_max = tk.IntVar(value=20)
        
        # Status variables
        self.is_running = False
        self.current_process = None
        
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
        title_label = ttk.Label(main_frame, text="Company Data Scraper - Enhanced", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="LinkedIn: Size + Industry | Website: Revenue Data", 
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Input file
        ttk.Label(file_frame, text="Input Excel File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(file_frame, textvariable=self.input_file, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2, pady=(0, 5))
        
        # Output file
        ttk.Label(file_frame, text="Output Excel File:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(file_frame, textvariable=self.output_file, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=2, pady=(0, 5))
        
        # Column Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Column Configuration", padding="10")
        config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
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
        
        # Scraper Options
        scraper_frame = ttk.LabelFrame(main_frame, text="Scraper Options", padding="10")
        scraper_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.scraper_type = tk.StringVar(value="openai")
        ttk.Radiobutton(scraper_frame, text="🤖 OpenAI Enhanced (Best Results - LinkedIn + AI Revenue)", 
                       variable=self.scraper_type, value="openai").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(scraper_frame, text="🔧 Complete Traditional (LinkedIn + Website Revenue)", 
                       variable=self.scraper_type, value="complete").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(scraper_frame, text="🔗 LinkedIn Only (Size + Industry Only)", 
                       variable=self.scraper_type, value="linkedin").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Timing Settings
        timing_frame = ttk.LabelFrame(main_frame, text="Timing Settings (seconds)", padding="10")
        timing_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(timing_frame, text="Wait time between requests:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(timing_frame, text="Min:").grid(row=0, column=1, padx=(10, 5))
        ttk.Spinbox(timing_frame, from_=5, to=60, textvariable=self.wait_min, width=8).grid(row=0, column=2)
        ttk.Label(timing_frame, text="Max:").grid(row=0, column=3, padx=(10, 5))
        ttk.Spinbox(timing_frame, from_=10, to=120, textvariable=self.wait_max, width=8).grid(row=0, column=4)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop", command=self.stop_scraping, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 Load Test Data", command=self.load_test_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ Clear All", command=self.clear_all).pack(side=tk.LEFT)
        
        # Progress and Log
        log_frame = ttk.LabelFrame(main_frame, text="Progress and Logs", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(log_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=90)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Select file and scraper type")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_input_file(self):
        """Browse for input Excel file"""
        initialdir = "test_data" if os.path.exists("test_data") else "."
        filename = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir=initialdir
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            base_name = os.path.splitext(filename)[0]
            scraper_suffix = self.scraper_type.get()
            output_name = f"{base_name}_{scraper_suffix}_results.xlsx"
            self.output_file.set(output_name)
            
    def browse_output_file(self):
        """Browse for output Excel file"""
        initialdir = "results" if os.path.exists("results") else "."
        filename = filedialog.asksaveasfilename(
            title="Save Output Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            defaultextension=".xlsx",
            initialdir=initialdir
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
            self.output_file.set("test_data/Test5_gui_results.xlsx")
            self.log_message("✅ Test data loaded: Test5.xlsx with correct column names")
            self.status_var.set("Test data loaded - Ready to scrape")
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
        self.status_var.set("Ready - Select file and scraper type")
        
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
        self.start_button.config(text="🔄 Scraping...", state="disabled")
        self.stop_button.config(state="normal")
        
        thread = threading.Thread(target=self.run_scraping)
        thread.daemon = True
        thread.start()
        
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.log_message("⏹️ Scraping stopped by user")
            except:
                pass
        self.reset_buttons()
        
    def reset_buttons(self):
        """Reset button states"""
        self.is_running = False
        self.start_button.config(text="🚀 Start Scraping", state="normal")
        self.stop_button.config(state="disabled")
        
    def run_scraping(self):
        """Run the scraping process"""
        try:
            self.log_message("🚀 Starting scraping process...")
            self.status_var.set("Processing...")
            
            scraper_type = self.scraper_type.get()
            input_file = self.input_file.get()
            output_file = self.output_file.get()
            
            self.log_message(f"📊 Input file: {input_file}")
            self.log_message(f"🔧 Scraper type: {scraper_type}")
            self.log_message(f"📁 Output file: {output_file}")
            
            # Build command based on scraper type
            if scraper_type == "openai":
                script_path = "scrapers/linkedin_openai_scraper.py"
                cmd = [
                    "python", script_path, input_file,
                    "--use-openai",
                    "--linkedin-column", self.linkedin_column.get(),
                    "--website-column", self.website_column.get(),
                    "--company-column", self.company_column.get(),
                    "--wait-min", str(self.wait_min.get()),
                    "--wait-max", str(self.wait_max.get())
                ]
                if output_file:
                    cmd.extend(["--output-file", output_file])
                    
            elif scraper_type == "complete":
                script_path = "scrapers/linkedin_company_complete_scraper.py"
                cmd = [
                    "python", script_path, input_file,
                    "--linkedin-column", self.linkedin_column.get(),
                    "--website-column", self.website_column.get(),
                    "--company-column", self.company_column.get(),
                    "--wait-min", str(self.wait_min.get()),
                    "--wait-max", str(self.wait_max.get())
                ]
                if output_file:
                    cmd.extend(["--output-file", output_file])
                    
            else:  # linkedin only
                script_path = "scrapers/linkedin_company_scraper_enhanced.py"
                cmd = [
                    "python", script_path, input_file,
                    "--linkedin-column", self.linkedin_column.get(),
                    "--wait-min", str(self.wait_min.get()),
                    "--wait-max", str(self.wait_max.get())
                ]
                if output_file:
                    cmd.extend(["--output-file", output_file])
            
            self.log_message(f"🔧 Command: {' '.join(cmd)}")
            
            # Check if script exists
            if not os.path.exists(script_path):
                self.log_message(f"❌ Error: Script not found: {script_path}")
                self.status_var.set("Error - Script not found")
                return
            
            # Run the scraper
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            for line in iter(self.current_process.stdout.readline, ''):
                if not self.is_running:
                    break
                line = line.strip()
                if line:
                    self.log_message(f"📝 {line}")
                    
                    # Update progress based on log messages
                    if "Processing company" in line:
                        try:
                            # Extract progress from "Processing company X/Y"
                            parts = line.split("Processing company ")[1].split("/")
                            if len(parts) == 2:
                                current = int(parts[0])
                                total = int(parts[1].split(":")[0])
                                progress = (current / total) * 100
                                self.progress_var.set(progress)
                        except:
                            pass
            
            # Wait for completion
            self.current_process.wait()
            
            if self.current_process.returncode == 0:
                self.log_message("✅ Scraping completed successfully!")
                self.status_var.set("Completed successfully")
                self.progress_var.set(100)
                
                # Show results
                if output_file and os.path.exists(output_file):
                    self.log_message(f"📁 Results saved to: {output_file}")
                    if messagebox.askyesno("Success", f"Scraping completed!\n\nResults saved to:\n{output_file}\n\nOpen results folder?"):
                        import webbrowser
                        webbrowser.open(os.path.dirname(output_file))
            else:
                self.log_message("❌ Scraping failed - check logs for details")
                self.status_var.set("Failed")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.status_var.set("Error")
        finally:
            self.reset_buttons()
            self.current_process = None

def main():
    # Check if we're in the right directory
    if not os.path.exists("scrapers"):
        print("❌ Error: Not in CompanyDataScraper directory")
        print("Please navigate to: C:\\Viji\\Automation\\NewCode\\CompanyDataScraper")
        print("Then run: python gui\\linkedin_data_scraper_gui_fixed.py")
        messagebox.showerror("Error", "Please run from CompanyDataScraper directory")
        return
    
    # Create GUI
    root = tk.Tk()
    app = EnhancedLinkedInGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    print("🖥️ Enhanced LinkedIn GUI Started")
    print("✅ GUI is working perfectly!")
    print("🔧 Features: LinkedIn (Size+Industry) + Website Revenue")
    print("🤖 OpenAI integration available")
    
    root.mainloop()

if __name__ == "__main__":
    main()