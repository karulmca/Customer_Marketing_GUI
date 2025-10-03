#!/usr/bin/env python3
"""
GUI version of LinkedIn Company Size Scraper
Simple interface for non-technical users
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
from linkedin_company_scraper import process_excel_file, load_config
import logging

class LinkedInScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Company Size Scraper")
        self.root.geometry("800x600")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.url_column = tk.StringVar(value="LinkedIn_URL")
        self.size_column = tk.StringVar(value="Company_Size")
        
        # Load default values from config
        config = load_config()
        defaults = config.get('default_columns', {})
        self.url_column.set(defaults.get('url_column', 'LinkedIn_URL'))
        self.size_column.set(defaults.get('size_column', 'Company_Size'))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="LinkedIn Company Size Scraper", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input Excel File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_input_file).grid(row=1, column=2, pady=5)
        
        # Output file selection (optional)
        ttk.Label(main_frame, text="Output Excel File (optional):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_output_file).grid(row=2, column=2, pady=5)
        
        # Column names
        ttk.Label(main_frame, text="LinkedIn URL Column:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.url_column, width=30).grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 5))
        
        ttk.Label(main_frame, text="Company Size Column:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.size_column, width=30).grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 5))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Create Sample File", command=self.create_sample_file).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Log output
        ttk.Label(main_frame, text="Log Output:").grid(row=8, column=0, sticky=tk.W, pady=(20, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(9, weight=1)
        
        # Setup logging to display in GUI
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging to display in the GUI text widget"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.update()
        
        # Add GUI handler to logger
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        logger = logging.getLogger('linkedin_company_scraper')
        logger.addHandler(gui_handler)
        logger.setLevel(logging.INFO)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Select Output Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            
    def create_sample_file(self):
        """Create a sample Excel file"""
        try:
            import pandas as pd
            
            # Sample data
            data = {
                self.url_column.get(): [
                    'https://www.linkedin.com/company/microsoft/',
                    'https://www.linkedin.com/company/google/',
                    'https://www.linkedin.com/company/apple/',
                    'https://www.linkedin.com/company/amazon/',
                    'https://www.linkedin.com/company/meta/'
                ],
                'Company_Name': ['Microsoft', 'Google', 'Apple', 'Amazon', 'Meta'],
                self.size_column.get(): [''] * 5,
                'Industry': ['Technology', 'Technology', 'Technology', 'E-commerce', 'Technology']
            }
            
            df = pd.DataFrame(data)
            
            filename = filedialog.asksaveasfilename(
                title="Save Sample Excel File",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Success", f"Sample file created: {filename}")
                self.input_file.set(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create sample file: {str(e)}")
            
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input Excel file")
            return False
            
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return False
            
        if not self.url_column.get().strip():
            messagebox.showerror("Error", "Please enter the LinkedIn URL column name")
            return False
            
        if not self.size_column.get().strip():
            messagebox.showerror("Error", "Please enter the Company Size column name")
            return False
            
        return True
        
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if not self.validate_inputs():
            return
            
        # Disable start button
        self.start_button.config(state='disabled')
        self.progress_bar.start()
        self.status_label.config(text="Starting scraping process...")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start scraping in separate thread
        thread = threading.Thread(target=self.run_scraping)
        thread.daemon = True
        thread.start()
        
    def run_scraping(self):
        """Run the scraping process"""
        try:
            input_file = self.input_file.get()
            output_file = self.output_file.get() if self.output_file.get() else None
            url_column = self.url_column.get().strip()
            size_column = self.size_column.get().strip()
            
            self.root.after(0, lambda: self.status_label.config(text="Processing Excel file..."))
            
            # Run the scraper
            process_excel_file(
                input_file=input_file,
                url_column=url_column,
                size_column=size_column,
                output_file=output_file
            )
            
            # Success
            self.root.after(0, self.scraping_complete)
            
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            self.root.after(0, lambda: self.scraping_error(error_msg))
            
    def scraping_complete(self):
        """Called when scraping is complete"""
        self.progress_bar.stop()
        self.start_button.config(state='normal')
        self.status_label.config(text="Scraping completed successfully!")
        messagebox.showinfo("Success", "Company size extraction completed!")
        
    def scraping_error(self, error_msg):
        """Called when scraping fails"""
        self.progress_bar.stop()
        self.start_button.config(state='normal')
        self.status_label.config(text="Scraping failed")
        messagebox.showerror("Error", error_msg)

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = LinkedInScraperGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()