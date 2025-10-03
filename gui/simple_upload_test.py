#!/usr/bin/env python3
"""
Simple File Upload Test GUI - To check button visibility
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class SimpleUploadGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple File Upload Test")
        self.root.geometry("800x600")
        
        # Variables
        self.uploaded_file_path = tk.StringVar()
        self.df_preview = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📁 Simple File Upload Test", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(file_frame, text="Select File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.uploaded_file_path, width=50)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="📁 Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # File info display
        self.file_info_var = tk.StringVar(value="No file selected")
        info_label = ttk.Label(main_frame, textvariable=self.file_info_var, font=('Arial', 10))
        info_label.pack(pady=(0, 20))
        
        # UPLOAD BUTTONS - Multiple styles for visibility
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Button 1: Basic upload
        upload_btn1 = ttk.Button(buttons_frame, text="📤 UPLOAD FILE", 
                                command=self.upload_file, width=20)
        upload_btn1.pack(side=tk.LEFT, padx=(0, 10))
        
        # Button 2: Upload to database  
        upload_btn2 = ttk.Button(buttons_frame, text="🗄️ UPLOAD TO DATABASE", 
                                command=self.upload_to_database, width=25)
        upload_btn2.pack(side=tk.LEFT, padx=(0, 10))
        
        # Button 3: Clear
        clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear", 
                              command=self.clear_form, width=15)
        clear_btn.pack(side=tk.LEFT)
        
        # Preview area
        preview_frame = ttk.LabelFrame(main_frame, text="File Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text area for preview
        self.preview_text = tk.Text(preview_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def browse_file(self):
        """Browse for Excel or CSV file"""
        filetypes = [
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Excel or CSV file",
            filetypes=filetypes
        )
        
        if filename:
            self.uploaded_file_path.set(filename)
            self.analyze_file(filename)
            
    def analyze_file(self, file_path):
        """Analyze the selected file"""
        try:
            # Read file based on extension
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
                
            self.df_preview = df
            
            # Update file info
            file_info = f"✅ File loaded: {os.path.basename(file_path)} | Rows: {len(df)} | Columns: {len(df.columns)}"
            self.file_info_var.set(file_info)
            
            # Show preview
            preview_text = f"File: {os.path.basename(file_path)}\\n"
            preview_text += f"Rows: {len(df)}\\n"
            preview_text += f"Columns: {len(df.columns)}\\n\\n"
            preview_text += f"Column Names:\\n{', '.join(df.columns.tolist())}\\n\\n"
            preview_text += f"First 5 rows:\\n{df.head().to_string()}"
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")
            self.file_info_var.set("❌ Failed to load file")
            
    def upload_file(self):
        """Basic upload function"""
        if self.df_preview is None:
            messagebox.showerror("Error", "Please select and analyze a file first")
            return
            
        messagebox.showinfo("Upload", f"File ready for upload!\\n\\nRows: {len(self.df_preview)}\\nColumns: {len(self.df_preview.columns)}")
        
    def upload_to_database(self):
        """Upload to database function"""
        if self.df_preview is None:
            messagebox.showerror("Error", "Please select and analyze a file first")
            return
            
        messagebox.showinfo("Database Upload", 
                           f"File ready for database upload!\\n\\n"
                           f"File: {os.path.basename(self.uploaded_file_path.get())}\\n"
                           f"Rows: {len(self.df_preview)}\\n"
                           f"Columns: {len(self.df_preview.columns)}\\n\\n"
                           f"This would upload to PostgreSQL database.")
        
    def clear_form(self):
        """Clear the form"""
        self.uploaded_file_path.set("")
        self.df_preview = None
        self.file_info_var.set("No file selected")
        self.preview_text.delete(1.0, tk.END)

def main():
    print("🚀 Starting Simple Upload Test GUI...")
    
    root = tk.Tk()
    app = SimpleUploadGUI(root)
    
    print("✅ Simple Upload GUI Created - Window should be visible now")
    print("🔧 Test the upload buttons to make sure they're visible")
    
    root.mainloop()

if __name__ == "__main__":
    main()