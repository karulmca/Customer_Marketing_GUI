#!/usr/bin/env python3
"""
File Upload GUI with Backend Database Integration
Handles file uploads and saves data to database
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import sqlite3
import os
import json
from datetime import datetime
import threading

class FileUploadDatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Upload & Database Manager")
        self.root.geometry("1200x800")
        
        # Force window to be visible and on top initially
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        # Remove topmost after 3 seconds
        self.root.after(3000, lambda: self.root.attributes('-topmost', False))
        
        # Variables
        self.uploaded_file_path = tk.StringVar()
        self.table_name = tk.StringVar(value="company_data")
        self.db_path = tk.StringVar(value="company_database.db")
        
        # Status variables
        self.is_processing = False
        self.df_preview = None
        
        # Initialize database
        self.init_database()
        
        self.create_widgets()
        
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path.get())
            cursor = conn.cursor()
            
            # Create a sample table structure
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    linkedin_url TEXT,
                    company_website TEXT,
                    company_size TEXT,
                    industry TEXT,
                    revenue TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_source TEXT
                )
            ''')
            
            # Create upload history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS upload_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT,
                    file_path TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    records_count INTEGER,
                    status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
    
    def create_widgets(self):
        # Main container with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: File Upload
        upload_frame = ttk.Frame(notebook)
        notebook.add(upload_frame, text="📁 File Upload")
        
        # Tab 2: Database View
        database_frame = ttk.Frame(notebook)
        notebook.add(database_frame, text="🗄️ Database View")
        
        # Tab 3: Settings
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        
        self.create_upload_tab(upload_frame)
        self.create_database_tab(database_frame)
        self.create_settings_tab(settings_frame)
        
    def create_upload_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📁 File Upload & Database Integration", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Select File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.uploaded_file_path, width=60)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # File info frame
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_info_text = scrolledtext.ScrolledText(info_frame, height=6, wrap=tk.WORD)
        self.file_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Data Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview for preview
        columns = ("Column1", "Column2", "Column3", "Column4", "Column5")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=150)
            
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        upload_btn = ttk.Button(control_frame, text="🔄 Process & Upload to Database", 
                               command=self.upload_to_database, style="Accent.TButton")
        upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(control_frame, text="🗑️ Clear", command=self.clear_upload)
        clear_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(control_frame, textvariable=self.status_var)
        status_bar.pack(side=tk.RIGHT)
        
    def create_database_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🗄️ Database Records", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = ttk.Button(control_frame, text="🔄 Refresh", command=self.refresh_database_view)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = ttk.Button(control_frame, text="📤 Export", command=self.export_database)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ttk.Button(control_frame, text="🗑️ Delete Selected", command=self.delete_selected_records)
        delete_btn.pack(side=tk.LEFT)
        
        # Database view frame
        db_frame = ttk.LabelFrame(main_frame, text="Database Records", padding="10")
        db_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for database records
        db_columns = ("ID", "Company Name", "LinkedIn URL", "Website", "Size", "Industry", "Revenue", "Upload Date")
        self.db_tree = ttk.Treeview(db_frame, columns=db_columns, show="headings", height=15)
        
        for col in db_columns:
            self.db_tree.heading(col, text=col)
            self.db_tree.column(col, width=120)
            
        db_scrollbar_y = ttk.Scrollbar(db_frame, orient=tk.VERTICAL, command=self.db_tree.yview)
        db_scrollbar_x = ttk.Scrollbar(db_frame, orient=tk.HORIZONTAL, command=self.db_tree.xview)
        self.db_tree.configure(yscrollcommand=db_scrollbar_y.set, xscrollcommand=db_scrollbar_x.set)
        
        self.db_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        db_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        db_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load initial database view
        self.refresh_database_view()
        
    def create_settings_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="⚙️ Database Settings", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Database settings frame
        db_settings_frame = ttk.LabelFrame(main_frame, text="Database Configuration", padding="10")
        db_settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(db_settings_frame, text="Database Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        db_entry = ttk.Entry(db_settings_frame, textvariable=self.db_path, width=50)
        db_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_db_btn = ttk.Button(db_settings_frame, text="Browse", command=self.browse_database)
        browse_db_btn.grid(row=0, column=2)
        
        ttk.Label(db_settings_frame, text="Default Table:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        table_entry = ttk.Entry(db_settings_frame, textvariable=self.table_name, width=30)
        table_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        db_settings_frame.columnconfigure(1, weight=1)
        
        # Database actions frame
        actions_frame = ttk.LabelFrame(main_frame, text="Database Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        create_table_btn = ttk.Button(actions_frame, text="🔧 Create/Reset Table", 
                                     command=self.create_table)
        create_table_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        backup_btn = ttk.Button(actions_frame, text="💾 Backup Database", 
                               command=self.backup_database)
        backup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Database Statistics", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=10, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Load initial stats
        self.update_stats()
        
    def browse_file(self):
        """Browse for file to upload"""
        file_types = [
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select file to upload",
            filetypes=file_types
        )
        
        if filename:
            self.uploaded_file_path.set(filename)
            self.analyze_file()
            
    def analyze_file(self):
        """Analyze the uploaded file and show preview"""
        file_path = self.uploaded_file_path.get()
        if not file_path or not os.path.exists(file_path):
            return
            
        try:
            # Read file based on extension
            if file_path.lower().endswith(('.xlsx', '.xls')):
                self.df_preview = pd.read_excel(file_path)
            elif file_path.lower().endswith('.csv'):
                self.df_preview = pd.read_csv(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
                
            # Update file info
            info = f"📁 File: {os.path.basename(file_path)}\n"
            info += f"📊 Rows: {len(self.df_preview)}\n"
            info += f"📋 Columns: {len(self.df_preview.columns)}\n"
            info += f"💾 Size: {os.path.getsize(file_path)} bytes\n\n"
            info += "📋 Columns:\n"
            for i, col in enumerate(self.df_preview.columns):
                info += f"  {i+1}. {col}\n"
                
            self.file_info_text.delete(1.0, tk.END)
            self.file_info_text.insert(1.0, info)
            
            # Update preview
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")
            
    def update_preview(self):
        """Update the preview treeview with file data"""
        # Clear existing data
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
            
        if self.df_preview is None:
            return
            
        # Update column headers
        columns = list(self.df_preview.columns)[:5]  # Show first 5 columns
        self.preview_tree["columns"] = columns
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=150)
            
        # Add data rows (first 10 rows)
        for i, row in self.df_preview.head(10).iterrows():
            values = [str(row[col]) if col in row else "" for col in columns]
            self.preview_tree.insert("", tk.END, values=values)
            
    def upload_to_database(self):
        """Upload file data to database"""
        if self.df_preview is None:
            messagebox.showerror("Error", "Please select and analyze a file first")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Upload already in progress")
            return
            
        # Start upload in separate thread
        self.is_processing = True
        self.status_var.set("Processing...")
        
        thread = threading.Thread(target=self._upload_worker)
        thread.daemon = True
        thread.start()
        
    def _upload_worker(self):
        """Worker thread for database upload"""
        try:
            conn = sqlite3.connect(self.db_path.get())
            cursor = conn.cursor()
            
            # Map columns to database fields
            column_mapping = self.get_column_mapping()
            
            uploaded_count = 0
            file_name = os.path.basename(self.uploaded_file_path.get())
            
            for _, row in self.df_preview.iterrows():
                # Extract values based on mapping
                values = {
                    'company_name': self.safe_get_value(row, column_mapping.get('company_name')),
                    'linkedin_url': self.safe_get_value(row, column_mapping.get('linkedin_url')),
                    'company_website': self.safe_get_value(row, column_mapping.get('company_website')),
                    'company_size': self.safe_get_value(row, column_mapping.get('company_size')),
                    'industry': self.safe_get_value(row, column_mapping.get('industry')),
                    'revenue': self.safe_get_value(row, column_mapping.get('revenue')),
                    'file_source': file_name
                }
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO company_data 
                    (company_name, linkedin_url, company_website, company_size, 
                     industry, revenue, file_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    values['company_name'], values['linkedin_url'], 
                    values['company_website'], values['company_size'],
                    values['industry'], values['revenue'], values['file_source']
                ))
                
                uploaded_count += 1
                
            # Record upload history
            cursor.execute('''
                INSERT INTO upload_history (file_name, file_path, records_count, status)
                VALUES (?, ?, ?, ?)
            ''', (file_name, self.uploaded_file_path.get(), uploaded_count, "Success"))
            
            conn.commit()
            conn.close()
            
            # Update UI in main thread
            self.root.after(0, lambda: self._upload_completed(uploaded_count))
            
        except Exception as e:
            self.root.after(0, lambda: self._upload_failed(str(e)))
            
    def safe_get_value(self, row, column_name):
        """Safely get value from row"""
        if column_name and column_name in row:
            return str(row[column_name]) if pd.notna(row[column_name]) else ""
        return ""
        
    def get_column_mapping(self):
        """Get column mapping based on common column names"""
        if self.df_preview is None:
            return {}
            
        mapping = {}
        columns = [col.lower() for col in self.df_preview.columns]
        
        # Define mapping patterns
        patterns = {
            'company_name': ['company', 'name', 'company_name', 'business'],
            'linkedin_url': ['linkedin', 'linkedin_url', 'linkedin_link'],
            'company_website': ['website', 'url', 'web', 'site'],
            'company_size': ['size', 'employees', 'company_size'],
            'industry': ['industry', 'sector', 'business_type'],
            'revenue': ['revenue', 'sales', 'turnover', 'income']
        }
        
        for field, keywords in patterns.items():
            for col in self.df_preview.columns:
                if any(keyword in col.lower() for keyword in keywords):
                    mapping[field] = col
                    break
                    
        return mapping
        
    def _upload_completed(self, count):
        """Handle successful upload completion"""
        self.is_processing = False
        self.status_var.set(f"✅ Uploaded {count} records successfully")
        messagebox.showinfo("Success", f"Successfully uploaded {count} records to database")
        self.refresh_database_view()
        self.update_stats()
        
    def _upload_failed(self, error):
        """Handle upload failure"""
        self.is_processing = False
        self.status_var.set("❌ Upload failed")
        messagebox.showerror("Upload Failed", f"Failed to upload data: {error}")
        
    def clear_upload(self):
        """Clear upload form"""
        self.uploaded_file_path.set("")
        self.df_preview = None
        self.file_info_text.delete(1.0, tk.END)
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self.status_var.set("Ready")
        
    def refresh_database_view(self):
        """Refresh the database records view"""
        try:
            # Clear existing data
            for item in self.db_tree.get_children():
                self.db_tree.delete(item)
                
            conn = sqlite3.connect(self.db_path.get())
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, company_name, linkedin_url, company_website, 
                       company_size, industry, revenue, upload_date
                FROM company_data 
                ORDER BY upload_date DESC
            ''')
            
            records = cursor.fetchall()
            
            for record in records:
                # Format the record for display
                formatted_record = [
                    str(record[0]),  # ID
                    record[1] or "",  # Company Name
                    record[2] or "",  # LinkedIn URL
                    record[3] or "",  # Website
                    record[4] or "",  # Size
                    record[5] or "",  # Industry
                    record[6] or "",  # Revenue
                    record[7] or ""   # Upload Date
                ]
                self.db_tree.insert("", tk.END, values=formatted_record)
                
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to refresh database view: {str(e)}")
            
    def export_database(self):
        """Export database to Excel file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Database",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
                
            conn = sqlite3.connect(self.db_path.get())
            df = pd.read_sql_query("SELECT * FROM company_data", conn)
            conn.close()
            
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Database exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export database: {str(e)}")
            
    def delete_selected_records(self):
        """Delete selected records from database"""
        selected_items = self.db_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select records to delete")
            return
            
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected_items)} selected records?"):
            return
            
        try:
            conn = sqlite3.connect(self.db_path.get())
            cursor = conn.cursor()
            
            for item in selected_items:
                record_id = self.db_tree.item(item)['values'][0]
                cursor.execute("DELETE FROM company_data WHERE id = ?", (record_id,))
                
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Deleted {len(selected_items)} records")
            self.refresh_database_view()
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete records: {str(e)}")
            
    def browse_database(self):
        """Browse for database file"""
        file_path = filedialog.asksaveasfilename(
            title="Select Database File",
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        
        if file_path:
            self.db_path.set(file_path)
            self.init_database()
            self.refresh_database_view()
            self.update_stats()
            
    def create_table(self):
        """Create or reset the main table"""
        if messagebox.askyesno("Confirm", "This will reset the table and delete all data. Continue?"):
            try:
                conn = sqlite3.connect(self.db_path.get())
                cursor = conn.cursor()
                
                cursor.execute("DROP TABLE IF EXISTS company_data")
                cursor.execute('''
                    CREATE TABLE company_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT,
                        linkedin_url TEXT,
                        company_website TEXT,
                        company_size TEXT,
                        industry TEXT,
                        revenue TEXT,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_source TEXT
                    )
                ''')
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Table created/reset successfully")
                self.refresh_database_view()
                self.update_stats()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create table: {str(e)}")
                
    def backup_database(self):
        """Backup the current database"""
        try:
            backup_path = filedialog.asksaveasfilename(
                title="Backup Database",
                defaultextension=".db",
                filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
            )
            
            if backup_path:
                import shutil
                shutil.copy2(self.db_path.get(), backup_path)
                messagebox.showinfo("Success", f"Database backed up to {backup_path}")
                
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup database: {str(e)}")
            
    def update_stats(self):
        """Update database statistics"""
        try:
            conn = sqlite3.connect(self.db_path.get())
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM company_data")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT file_source) FROM company_data")
            unique_sources = cursor.fetchone()[0]
            
            cursor.execute("SELECT file_source, COUNT(*) FROM company_data GROUP BY file_source")
            source_stats = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) FROM upload_history")
            upload_count = cursor.fetchone()[0]
            
            # Format stats
            stats = f"📊 Database Statistics\n"
            stats += f"{'='*50}\n\n"
            stats += f"📋 Total Records: {total_records}\n"
            stats += f"📁 Unique File Sources: {unique_sources}\n"
            stats += f"📤 Total Uploads: {upload_count}\n\n"
            
            stats += f"📁 Records by Source:\n"
            stats += f"{'-'*30}\n"
            for source, count in source_stats:
                stats += f"  • {source or 'Unknown'}: {count} records\n"
                
            conn.close()
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"Error loading stats: {str(e)}")

def main():
    print("🚀 Starting File Upload & Database GUI...")
    print("📋 Look for window: 'File Upload & Database Manager'")
    
    root = tk.Tk()
    app = FileUploadDatabaseGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    print("✅ File Upload GUI Created - Window should be visible now")
    print("🔧 Features: File Upload + Database Integration + Data Management")
    
    root.mainloop()
    
    print("🏁 File Upload GUI Closed")

if __name__ == "__main__":
    main()