#!/usr/bin/env python3
"""
Enhanced GUI for LinkedIn Company Data Scraper
Extracts both Company Size AND Industry from LinkedIn
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import pandas as pd
import logging
from datetime import datetime

# Setup logging for GUI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedLinkedInGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Company Data Scraper - Enhanced (Size + Industry)")
        self.root.geometry("950x750")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.url_column = tk.StringVar(value="LinkedIn_URL")
        self.size_column = tk.StringVar(value="Company_Size")
        self.industry_column = tk.StringVar(value="Industry")
        self.wait_min = tk.IntVar(value=45)
        self.wait_max = tk.IntVar(value=75)
        
        # Status variables
        self.is_running = False
        self.current_thread = None
        
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
        title_label = ttk.Label(main_frame, text="LinkedIn Company Data Scraper", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Extracts Company Size + Industry from LinkedIn", 
                                  font=('Arial', 12), foreground='blue')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        example_label = ttk.Label(main_frame, text='Example: "201-500 employees" + "Financial Services"', 
                                 font=('Arial', 10), foreground='green')
        example_label.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        # Input file
        ttk.Label(file_frame, text="Input Excel File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2)
        
        # Output file
        ttk.Label(file_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.output_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=2, pady=(10, 0))
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Column Configuration", padding="10")
        config_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # Column names - Row 1
        ttk.Label(config_frame, text="LinkedIn URL Column:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(config_frame, textvariable=self.url_column, width=25).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(config_frame, text="Company Size Column:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Entry(config_frame, textvariable=self.size_column, width=25).grid(row=0, column=3, sticky=tk.W)
        
        # Column names - Row 2
        ttk.Label(config_frame, text="Industry Column:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(config_frame, textvariable=self.industry_column, width=25).grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Wait times
        ttk.Label(config_frame, text="Wait Time (Min):").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Spinbox(config_frame, from_=30, to=180, textvariable=self.wait_min, width=10).grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(config_frame, text="Wait Time (Max):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Spinbox(config_frame, from_=60, to=300, textvariable=self.wait_max, width=10).grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 15))
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_scraping, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Create Sample File", command=self.create_sample_file).pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress & Results", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to scrape Company Size + Industry")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure main frame row weights
        main_frame.rowconfigure(6, weight=1)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Excel file with LinkedIn URLs",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            base_name = os.path.splitext(filename)[0]
            self.output_file.set(f"{base_name}_enhanced_results.xlsx")
            
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save results as",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            
    def create_sample_file(self):
        """Create a sample Excel file with Industry column"""
        try:
            sample_data = {
                'Company_Name': ['Microsoft Corporation', 'Google LLC', 'Apple Inc.', 'Amazon.com Inc.'],
                'LinkedIn_URL': [
                    'https://www.linkedin.com/company/microsoft/',
                    'https://www.linkedin.com/company/google/',
                    'https://www.linkedin.com/company/apple/',
                    'https://www.linkedin.com/company/amazon/'
                ],
                'Company_Size': ['', '', '', ''],
                'Industry': ['', '', '', '']
            }
            
            df = pd.DataFrame(sample_data)
            sample_file = "sample_companies_enhanced.xlsx"
            df.to_excel(sample_file, index=False)
            
            messagebox.showinfo("Sample Created", f"Enhanced sample file created: {sample_file}\n\nColumns included:\n- Company_Name\n- LinkedIn_URL\n- Company_Size (will be filled)\n- Industry (will be filled)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create sample file: {str(e)}")
            
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_scraping(self):
        """Start the scraping process"""
        # Validate inputs
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input Excel file")
            return
            
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
            
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file")
            return
            
        # Update UI
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress.start()
        self.status_var.set("Scraping in progress...")
        self.log_text.delete(1.0, tk.END)
        
        # Start scraping in separate thread
        self.current_thread = threading.Thread(target=self.run_scraping, daemon=True)
        self.current_thread.start()
        
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        self.log_message("Stopping scraper...")
        self.status_var.set("Stopping...")
        
    def run_scraping(self):
        """Run the actual scraping process"""
        try:
            from linkedin_data_scraper import LinkedInDataScraper
            
            self.log_message("🚀 Starting Enhanced LinkedIn Data Scraper")
            self.log_message(f"📁 Input file: {self.input_file.get()}")
            self.log_message(f"💾 Output file: {self.output_file.get()}")
            self.log_message(f"⏱️  Wait time: {self.wait_min.get()}-{self.wait_max.get()} seconds")
            self.log_message(f"📊 Extracting: Company Size + Industry")
            self.log_message("-" * 60)
            
            # Load Excel file
            df = pd.read_excel(self.input_file.get())
            total_companies = len(df)
            
            # Ensure industry column exists
            if self.industry_column.get() not in df.columns:
                df[self.industry_column.get()] = ''
                self.log_message(f"✅ Added new column: {self.industry_column.get()}")
            
            self.log_message(f"📋 Loaded {total_companies} companies from Excel file")
            
            processed = 0
            size_successful = 0
            industry_successful = 0
            
            for index, row in df.iterrows():
                if not self.is_running:
                    self.log_message("⛔ Scraping stopped by user")
                    break
                    
                linkedin_url = row[self.url_column.get()]
                
                # Skip empty URLs
                if pd.isna(linkedin_url) or linkedin_url.strip() == '':
                    self.log_message(f"⚠️  Row {index + 1}: Skipping empty URL")
                    continue
                
                # Check if both size and industry already exist
                current_size = str(row[self.size_column.get()]).strip()
                current_industry = str(row[self.industry_column.get()]).strip()
                
                if (current_size and current_size not in ['', 'nan', 'None'] and 
                    current_industry and current_industry not in ['', 'nan', 'None']):
                    self.log_message(f"✅ Row {index + 1}: Both size and industry already exist, skipping")
                    continue
                
                self.log_message(f"🔍 Row {index + 1}: Processing {linkedin_url}")
                
                # Create fresh scraper
                scraper = LinkedInDataScraper()
                data = scraper.extract_company_data(linkedin_url.strip())
                
                # Update company size if needed
                if not current_size or current_size in ['', 'nan', 'None']:
                    df.at[index, self.size_column.get()] = str(data['company_size'])
                    if data['company_size'] not in ['Not Found', 'Error', 'Timeout', 'Blocked by LinkedIn']:
                        size_successful += 1
                        self.log_message(f"✅ Row {index + 1}: Company Size - {data['company_size']}")
                    else:
                        self.log_message(f"❌ Row {index + 1}: Company Size - {data['company_size']}")
                
                # Update industry if needed
                if not current_industry or current_industry in ['', 'nan', 'None']:
                    df.at[index, self.industry_column.get()] = str(data['industry'])
                    if data['industry'] not in ['Not Found', 'Error', 'Timeout', 'Blocked by LinkedIn']:
                        industry_successful += 1
                        self.log_message(f"✅ Row {index + 1}: Industry - {data['industry']}")
                    else:
                        self.log_message(f"❌ Row {index + 1}: Industry - {data['industry']}")
                
                processed += 1
                
                # Save progress
                df.to_excel(self.output_file.get(), index=False)
                
                # Update status
                self.status_var.set(f"Processed: {processed}/{total_companies} | Size: {size_successful} | Industry: {industry_successful}")
                
                # Wait between companies
                if processed < total_companies and self.is_running:
                    import random
                    import time
                    wait_time = random.uniform(self.wait_min.get(), self.wait_max.get())
                    self.log_message(f"⏳ Waiting {wait_time:.1f} seconds before next company...")
                    
                    # Wait in small increments to allow stopping
                    wait_start = time.time()
                    while time.time() - wait_start < wait_time and self.is_running:
                        time.sleep(0.5)
                        self.root.update()
            
            # Final results
            if self.is_running:
                size_rate = (size_successful / processed * 100) if processed > 0 else 0
                industry_rate = (industry_successful / processed * 100) if processed > 0 else 0
                
                self.log_message("-" * 60)
                self.log_message(f"🎉 ENHANCED SCRAPING COMPLETE!")
                self.log_message(f"📊 Total processed: {processed}")
                self.log_message(f"📏 Company Size success: {size_successful} ({size_rate:.1f}%)")
                self.log_message(f"🏭 Industry success: {industry_successful} ({industry_rate:.1f}%)")
                self.log_message(f"💾 Results saved to: {self.output_file.get()}")
                
                self.status_var.set(f"Complete! Size: {size_successful}/{processed} | Industry: {industry_successful}/{processed}")
                
                messagebox.showinfo("Complete", f"Enhanced scraping complete!\n\nProcessed: {processed}\nCompany Size Success: {size_successful} ({size_rate:.1f}%)\nIndustry Success: {industry_successful} ({industry_rate:.1f}%)")
            
        except Exception as e:
            error_msg = f"Error during scraping: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
            
        finally:
            # Reset UI
            self.is_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.progress.stop()
            if not hasattr(self, '_final_status_set'):
                self.status_var.set("Ready to scrape Company Size + Industry")

def main():
    root = tk.Tk()
    app = EnhancedLinkedInGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()