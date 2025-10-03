#!/usr/bin/env python3
"""
File Upload GUI with PostgreSQL Backend Database Integration
Handles file uploads and saves data to PostgreSQL database
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import sys
from datetime import datetime
import threading

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
database_config_path = os.path.join(parent_dir, 'database_config')
if database_config_path not in sys.path:
    sys.path.insert(0, database_config_path)

try:
    from db_utils import get_database_connection, check_database_requirements
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Database dependencies not available: {e}")
    DATABASE_AVAILABLE = False

class FileUploadPostgreSQLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Upload & PostgreSQL Database Manager")
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
        
        # Status variables
        self.is_processing = False
        self.df_preview = None
        self.db_connection = None
        
        # Initialize database connection
        self.init_database()
        
        self.create_widgets()
        
    def init_database(self):
        """Initialize PostgreSQL database connection"""
        if not DATABASE_AVAILABLE:
            messagebox.showerror("Database Error", 
                               "PostgreSQL dependencies not available.\n"
                               "Please run: pip install psycopg2-binary sqlalchemy")
            return
            
        try:
            self.db_connection = get_database_connection("postgresql")
            
            if not self.db_connection:
                messagebox.showerror("Database Error", "Failed to create database connection")
                return
                
            if not self.db_connection.test_connection():
                messagebox.showerror("Database Connection Error", 
                                   "Failed to connect to PostgreSQL database.\n"
                                   "Please check your connection settings in database_config/.env")
                return
                
            # Initialize database manager
            if not self.db_connection.connect():
                messagebox.showerror("Database Error", "Failed to initialize database manager")
                return
                
            # Ensure tables exist
            self.db_connection.create_tables()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Database initialization failed: {str(e)}")
    
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
        notebook.add(settings_frame, text="⚙️ Database Settings")
        
        self.create_upload_tab(upload_frame)
        self.create_database_tab(database_frame)
        self.create_settings_tab(settings_frame)
        
    def create_upload_tab(self, parent):
        # Main container
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📁 File Upload & PostgreSQL Integration", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Database status frame
        status_frame = ttk.LabelFrame(main_frame, text="Database Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        db_status = "✅ Connected" if self.db_connection and self.db_connection.test_connection() else "❌ Disconnected"
        self.db_status_label = ttk.Label(status_frame, text=f"PostgreSQL: {db_status}")
        self.db_status_label.pack(side=tk.LEFT)
        
        refresh_db_btn = ttk.Button(status_frame, text="🔄 Refresh", command=self.refresh_db_status)
        refresh_db_btn.pack(side=tk.RIGHT)
        
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
        
        upload_btn = ttk.Button(control_frame, text="🔄 Process & Upload to PostgreSQL", 
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
        title_label = ttk.Label(main_frame, text="🗄️ PostgreSQL Database Records", 
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
        title_label = ttk.Label(main_frame, text="⚙️ PostgreSQL Database Settings", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Connection info frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Information", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        conn_info = "📋 Connection Details:\n"
        conn_info += "   • Database: FileUpload\n"
        conn_info += "   • Host: localhost:5432\n"
        conn_info += "   • User: postgres\n"
        conn_info += "   • URL: postgresql://postgres:***@localhost:5432/FileUpload\n"
        conn_info += "   • Configuration: database_config/.env"
        
        conn_label = ttk.Label(conn_frame, text=conn_info, justify=tk.LEFT)
        conn_label.pack(anchor=tk.W)
        
        # Database actions frame
        actions_frame = ttk.LabelFrame(main_frame, text="Database Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        test_conn_btn = ttk.Button(actions_frame, text="🔍 Test Connection", 
                                  command=self.test_connection)
        test_conn_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        recreate_tables_btn = ttk.Button(actions_frame, text="🔧 Recreate Tables", 
                                        command=self.recreate_tables)
        recreate_tables_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        backup_btn = ttk.Button(actions_frame, text="💾 Export All Data", 
                               command=self.export_all_data)
        backup_btn.pack(side=tk.LEFT)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Database Statistics", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=12, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Load initial stats
        self.update_stats()
    
    def refresh_db_status(self):
        """Refresh database connection status"""
        if self.db_connection and self.db_connection.test_connection():
            self.db_status_label.config(text="PostgreSQL: ✅ Connected")
        else:
            self.db_status_label.config(text="PostgreSQL: ❌ Disconnected")
            # Try to reconnect
            self.init_database()
        
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
            info += "📋 Columns detected:\n"
            
            # Show column mapping
            column_mapping = self.get_column_mapping()
            for i, col in enumerate(self.df_preview.columns):
                mapped_to = None
                for db_field, source_col in column_mapping.items():
                    if source_col == col:
                        mapped_to = f" → {db_field}"
                        break
                info += f"  {i+1}. {col}{mapped_to or ''}\n"
                
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
        """Upload file data to PostgreSQL database"""
        if self.df_preview is None:
            messagebox.showerror("Error", "Please select and analyze a file first")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Upload already in progress")
            return
            
        if not self.db_connection or not self.db_connection.test_connection():
            messagebox.showerror("Database Error", "No database connection available")
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
            # Prepare DataFrame for database insertion
            df_to_insert = self.prepare_dataframe_for_db()
            
            # Insert DataFrame into database
            success = self.db_connection.insert_dataframe(df_to_insert, "company_data")
            
            if success:
                # Record upload history
                file_name = os.path.basename(self.uploaded_file_path.get())
                upload_history = pd.DataFrame([{
                    'file_name': file_name,
                    'file_path': self.uploaded_file_path.get(),
                    'records_count': len(df_to_insert),
                    'status': 'Success',
                    'uploaded_by': 'GUI_User'
                }])
                
                self.db_connection.insert_dataframe(upload_history, "upload_history")
                
                # Update UI in main thread
                self.root.after(0, lambda: self._upload_completed(len(df_to_insert)))
            else:
                self.root.after(0, lambda: self._upload_failed("Database insertion failed"))
                
        except Exception as e:
            self.root.after(0, lambda: self._upload_failed(str(e)))
            
    def prepare_dataframe_for_db(self):
        """Prepare DataFrame with proper column mapping for database"""
        if self.df_preview is None:
            return pd.DataFrame()
            
        # Get column mapping
        column_mapping = self.get_column_mapping()
        
        # Create new DataFrame with database column names
        df_mapped = pd.DataFrame()
        
        # Map columns
        for db_column, source_column in column_mapping.items():
            if source_column and source_column in self.df_preview.columns:
                df_mapped[db_column] = self.df_preview[source_column].astype(str)
            else:
                df_mapped[db_column] = ""
        
        # Add metadata columns
        df_mapped['file_source'] = os.path.basename(self.uploaded_file_path.get())
        df_mapped['created_by'] = 'GUI_User'
        
        return df_mapped
        
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
        messagebox.showinfo("Success", f"Successfully uploaded {count} records to PostgreSQL database")
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
                
            if not self.db_connection:
                return
                
            # Get all records
            df = self.db_connection.get_all_records("company_data")
            
            if df is not None and not df.empty:
                for _, row in df.head(100).iterrows():  # Show first 100 records
                    values = [
                        str(row.get('id', '')),
                        str(row.get('company_name', '')),
                        str(row.get('linkedin_url', '')),
                        str(row.get('company_website', '')),
                        str(row.get('company_size', '')),
                        str(row.get('industry', '')),
                        str(row.get('revenue', '')),
                        str(row.get('upload_date', ''))
                    ]
                    self.db_tree.insert("", tk.END, values=values)
            
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
                
            if not self.db_connection:
                messagebox.showerror("Error", "No database connection")
                return
                
            df = self.db_connection.get_all_records("company_data")
            if df is not None:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Database exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to retrieve data for export")
            
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
            if not self.db_connection:
                messagebox.showerror("Error", "No database connection")
                return
                
            for item in selected_items:
                record_id = self.db_tree.item(item)['values'][0]
                query = f"DELETE FROM company_data WHERE id = {record_id}"
                self.db_connection.query_to_dataframe(query)
                
            messagebox.showinfo("Success", f"Deleted {len(selected_items)} records")
            self.refresh_database_view()
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete records: {str(e)}")
    
    def test_connection(self):
        """Test database connection"""
        if not self.db_connection:
            messagebox.showerror("Error", "No database connection object")
            return
            
        if self.db_connection.test_connection():
            messagebox.showinfo("Connection Test", "✅ PostgreSQL connection successful!")
        else:
            messagebox.showerror("Connection Test", "❌ PostgreSQL connection failed!")
    
    def recreate_tables(self):
        """Recreate database tables"""
        if not messagebox.askyesno("Confirm", 
                                  "This will recreate all tables and delete existing data.\n"
                                  "Are you sure you want to continue?"):
            return
            
        try:
            if not self.db_connection:
                messagebox.showerror("Error", "No database connection")
                return
                
            # Drop and recreate tables
            self.db_connection.query_to_dataframe("DROP TABLE IF EXISTS company_data CASCADE")
            self.db_connection.query_to_dataframe("DROP TABLE IF EXISTS upload_history CASCADE")
            
            # Recreate tables
            if self.db_connection.create_tables():
                messagebox.showinfo("Success", "Tables recreated successfully!")
                self.refresh_database_view()
                self.update_stats()
            else:
                messagebox.showerror("Error", "Failed to recreate tables")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to recreate tables: {str(e)}")
    
    def export_all_data(self):
        """Export all database data to Excel"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export All Database Data",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
                
            if not self.db_connection:
                messagebox.showerror("Error", "No database connection")
                return
                
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export company_data
                df_company = self.db_connection.get_all_records("company_data")
                if df_company is not None:
                    df_company.to_excel(writer, sheet_name='CompanyData', index=False)
                
                # Export upload_history
                df_history = self.db_connection.get_all_records("upload_history")
                if df_history is not None:
                    df_history.to_excel(writer, sheet_name='UploadHistory', index=False)
            
            messagebox.showinfo("Success", f"All data exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export all data: {str(e)}")
    
    def update_stats(self):
        """Update database statistics"""
        try:
            if not self.db_connection:
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, "❌ No database connection")
                return
                
            stats = self.db_connection.get_table_stats()
            
            if not stats:
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, "ℹ️ No statistics available")
                return
            
            # Format stats
            stats_text = f"📊 PostgreSQL Database Statistics\n"
            stats_text += f"{'='*60}\n\n"
            
            total_records = 0
            for table_name, info in stats.items():
                stats_text += f"📋 Table: {table_name}\n"
                stats_text += f"   • Records: {info['row_count']}\n"
                stats_text += f"   • Columns: {len(info['columns'])}\n"
                
                # Show column details
                for col in info['columns']:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    stats_text += f"     - {col['name']} ({col['type']}) {nullable}\n"
                
                stats_text += "\n"
                total_records += info['row_count']
            
            stats_text += f"🔢 Total Records Across All Tables: {total_records}\n"
            stats_text += f"🗄️ Database: FileUpload\n"
            stats_text += f"🌐 Host: localhost:5432\n"
            stats_text += f"📅 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"❌ Error loading stats: {str(e)}")

def main():
    print("🚀 Starting File Upload & PostgreSQL GUI...")
    print("📋 Look for window: 'File Upload & PostgreSQL Database Manager'")
    
    # Check database requirements
    if not DATABASE_AVAILABLE:
        print("❌ Database dependencies not available")
        print("💡 Please install: pip install psycopg2-binary sqlalchemy")
        return
    
    root = tk.Tk()
    app = FileUploadPostgreSQLGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    print("✅ PostgreSQL File Upload GUI Created - Window should be visible now")
    print("🔧 Features: File Upload + PostgreSQL Integration + Data Management")
    
    root.mainloop()
    
    print("🏁 PostgreSQL File Upload GUI Closed")

if __name__ == "__main__":
    main()