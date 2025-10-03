#!/usr/bin/env python3
"""
Updated GUI for LinkedIn Company Size Scraper
Works with the optimized scraper that extracts exact LinkedIn range formats
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

class OptimizedLinkedInGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Company Size Scraper - Optimized")
        self.root.geometry("900x700")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.url_column = tk.StringVar(value="LinkedIn_URL")
        self.size_column = tk.StringVar(value="Company_Size")
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
        title_label = ttk.Label(main_frame, text="LinkedIn Company Size Scraper", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Extracts exact LinkedIn range formats: 1-10, 11-50, 201-500 employees", 
                                  font=('Arial', 10), foreground='green')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
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
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        
        # Column names
        ttk.Label(config_frame, text="LinkedIn URL Column:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(config_frame, textvariable=self.url_column, width=30).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(config_frame, text="Company Size Column:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Entry(config_frame, textvariable=self.size_column, width=30).grid(row=0, column=3, sticky=tk.W)
        
        # Wait times
        ttk.Label(config_frame, text="Wait Time (Min):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Spinbox(config_frame, from_=30, to=180, textvariable=self.wait_min, width=10).grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        ttk.Label(config_frame, text="Wait Time (Max):").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Spinbox(config_frame, from_=60, to=300, textvariable=self.wait_max, width=10).grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 15))
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_scraping, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Open Sample File", command=self.create_sample_file).pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure main frame row weights
        main_frame.rowconfigure(5, weight=1)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Excel file with LinkedIn URLs",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            base_name = os.path.splitext(filename)[0]
            self.output_file.set(f"{base_name}_scraped_results.xlsx")
            
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save results as",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            
    def create_sample_file(self):
        """Create a sample Excel file"""
        try:
            sample_data = {
                'Company_Name': ['Microsoft', 'Google', 'Apple', 'Amazon'],
                'LinkedIn_URL': [
                    'https://www.linkedin.com/company/microsoft/',
                    'https://www.linkedin.com/company/google/',
                    'https://www.linkedin.com/company/apple/',
                    'https://www.linkedin.com/company/amazon/'
                ],
                'Company_Size': ['', '', '', '']
            }
            
            df = pd.DataFrame(sample_data)
            sample_file = "sample_companies_gui.xlsx"
            df.to_excel(sample_file, index=False)
            
            messagebox.showinfo("Sample Created", f"Sample file created: {sample_file}")
            
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
            from linkedin_scraper_optimized import OptimizedLinkedInScraper
            
            self.log_message("Starting LinkedIn Company Size Scraper (Optimized)")
            self.log_message(f"Input file: {self.input_file.get()}")
            self.log_message(f"Output file: {self.output_file.get()}")
            self.log_message(f"Wait time: {self.wait_min.get()}-{self.wait_max.get()} seconds")
            self.log_message("-" * 50)
            
            # Load Excel file
            df = pd.read_excel(self.input_file.get())
            total_companies = len(df)
            
            self.log_message(f"Loaded {total_companies} companies from Excel file")
            
            processed = 0
            successful = 0
            
            for index, row in df.iterrows():
                if not self.is_running:
                    self.log_message("Scraping stopped by user")
                    break
                    
                linkedin_url = row[self.url_column.get()]
                
                # Skip empty URLs
                if pd.isna(linkedin_url) or linkedin_url.strip() == '':
                    self.log_message(f"Row {index + 1}: Skipping empty URL")
                    continue
                
                # Skip if size already exists
                current_size = str(row[self.size_column.get()]).strip()
                if current_size and current_size not in ['', 'nan', 'None']:
                    self.log_message(f"Row {index + 1}: Size already exists ({current_size}), skipping")
                    continue
                
                self.log_message(f"Row {index + 1}: Processing {linkedin_url}")
                
                # Create fresh scraper
                scraper = OptimizedLinkedInScraper()
                company_size = scraper.extract_company_size(linkedin_url.strip())
                
                if company_size and company_size not in ['Not Found', 'Error', 'Timeout']:
                    df.at[index, self.size_column.get()] = str(company_size)
                    successful += 1
                    self.log_message(f"✅ Row {index + 1}: SUCCESS - {company_size}")
                else:
                    df.at[index, self.size_column.get()] = str(company_size or 'Not Found')
                    self.log_message(f"❌ Row {index + 1}: FAILED - {company_size}")
                
                processed += 1
                
                # Save progress
                df.to_excel(self.output_file.get(), index=False)
                
                # Update status
                self.status_var.set(f"Processed: {processed}/{total_companies} | Success: {successful}")
                
                # Wait between companies
                if processed < total_companies and self.is_running:
                    import random
                    import time
                    wait_time = random.uniform(self.wait_min.get(), self.wait_max.get())
                    self.log_message(f"Waiting {wait_time:.1f} seconds before next company...")
                    
                    # Wait in small increments to allow stopping
                    wait_start = time.time()
                    while time.time() - wait_start < wait_time and self.is_running:
                        time.sleep(0.5)
                        self.root.update()
            
            # Final results
            if self.is_running:
                success_rate = (successful / processed * 100) if processed > 0 else 0
                self.log_message("-" * 50)
                self.log_message(f"🎉 SCRAPING COMPLETE!")
                self.log_message(f"Total processed: {processed}")
                self.log_message(f"Successful extractions: {successful}")
                self.log_message(f"Success rate: {success_rate:.1f}%")
                self.log_message(f"Results saved to: {self.output_file.get()}")
                self.status_var.set(f"Complete! Success: {successful}/{processed} ({success_rate:.1f}%)")
                
                messagebox.showinfo("Complete", f"Scraping complete!\n\nProcessed: {processed}\nSuccessful: {successful}\nSuccess rate: {success_rate:.1f}%")
            
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
                self.status_var.set("Ready")

def main():
    root = tk.Tk()
    app = OptimizedLinkedInGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()