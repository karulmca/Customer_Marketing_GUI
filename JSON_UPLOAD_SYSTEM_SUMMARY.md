# 📋 FILE UPLOAD SYSTEM - JSON STORAGE IMPLEMENTATION

## ✅ **COMPLETED: New Database Schema & Workflow**

### 🗄️ **New Database Tables:**

#### **1. `file_upload` Table (Primary Storage)**
```sql
- id (SERIAL PRIMARY KEY)
- file_name (VARCHAR) - Original filename
- file_path (TEXT) - Full file path
- file_size (INTEGER) - File size in bytes
- original_columns (TEXT[]) - Array of original column names
- raw_data (JSONB) - Complete file data as JSON
- upload_date (TIMESTAMP) - When uploaded
- uploaded_by (VARCHAR) - Who uploaded
- processing_status (VARCHAR) - 'pending', 'completed', 'failed'
- processed_date (TIMESTAMP) - When processed
- processing_error (TEXT) - Error details if failed
- records_count (INTEGER) - Number of records in file
- file_hash (VARCHAR) - SHA-256 hash for duplicate detection
```

#### **2. `company_data` Table (Processed Data)**
```sql
- id (SERIAL PRIMARY KEY)
- company_name (VARCHAR)
- linkedin_url (TEXT)
- company_website (TEXT)
- company_size (VARCHAR)
- industry (VARCHAR)
- revenue (VARCHAR)
- upload_date (TIMESTAMP)
- file_source (VARCHAR) - Source filename
- file_upload_id (INTEGER) - References file_upload.id
- created_by (VARCHAR)
- updated_at (TIMESTAMP)
- data_source_priority (INTEGER)
- validation_status (VARCHAR)
```

#### **3. `processing_jobs` Table (Job Management)**
```sql
- id (SERIAL PRIMARY KEY)
- job_type (VARCHAR) - Type of processing job
- file_upload_id (INTEGER) - File to process
- job_status (VARCHAR) - 'queued', 'running', 'completed', 'failed'
- scheduled_at (TIMESTAMP)
- started_at (TIMESTAMP)
- completed_at (TIMESTAMP)
- error_message (TEXT)
- job_config (JSONB) - Job configuration
- retry_count (INTEGER)
- max_retries (INTEGER)
```

#### **4. `upload_history` Table (Audit Trail)**
```sql
- id (SERIAL PRIMARY KEY)
- file_name (VARCHAR)
- file_path (TEXT)
- upload_date (TIMESTAMP)
- records_count (INTEGER)
- status (VARCHAR)
- error_message (TEXT)
- uploaded_by (VARCHAR)
- file_upload_id (INTEGER)
- processing_duration_seconds (INTEGER)
```

### 🔄 **New Workflow:**

```
1. 📁 File Upload → JSON Storage
   ├── User uploads Excel/CSV file
   ├── File content converted to JSON
   ├── Stored in `file_upload` table
   ├── Status: 'pending'
   └── Processing job created automatically

2. ⏳ Scheduled Processing
   ├── Scheduled processor runs (manual/automated)
   ├── Finds pending files in `file_upload`
   ├── Extracts and maps data from JSON
   ├── Inserts processed data into `company_data`
   └── Updates status to 'completed'

3. 📊 Data Management
   ├── View uploaded files (JSON storage)
   ├── Monitor processing jobs
   ├── Access processed company data
   └── Export and manage results
```

### 📁 **New Files Created:**

#### **🔧 Core Processing Files:**
1. **`database_config/file_upload_processor.py`** - File upload processing logic
2. **`scheduled_processor.py`** - Scheduled job processor (main script)

#### **🎮 GUI Applications:**
1. **`gui/file_upload_json_gui.py`** - New JSON-based upload GUI

#### **🔥 Batch Files:**
1. **`batch_files/run_json_upload_gui.bat`** - Run JSON upload GUI
2. **`batch_files/run_scheduled_processor.bat`** - Run single processing job
3. **`batch_files/run_continuous_processor.bat`** - Run continuous processing

### 🎯 **GUI Features (JSON Upload Version):**

#### **📁 Tab 1: File Upload (JSON Storage)**
- Upload Excel/CSV files → Stored as JSON
- Smart file analysis and preview
- Duplicate detection via file hashing
- Automatic processing job creation

#### **📋 Tab 2: Uploaded Files**
- View all uploaded files and their status
- Process selected files manually
- View raw JSON data
- Monitor upload statistics

#### **🗄️ Tab 3: Processed Data**
- View processed company data
- Export processed records
- Delete unwanted records
- Track data lineage

#### **⚙️ Tab 4: Processing Jobs**
- Monitor job queue and status
- Process all pending files
- Create custom processing jobs
- Job retry and error handling

#### **📊 Tab 5: Statistics**
- Upload and processing statistics
- Success/failure rates
- System performance metrics
- Export all system data

### 🚀 **How to Use the New System:**

#### **1. Upload Files as JSON:**
```bash
# Run the JSON upload GUI
.\batch_files\run_json_upload_gui.bat

# OR directly with Python
python gui\file_upload_json_gui.py
```

#### **2. Process Uploaded Files:**

**Manual Processing (Single Run):**
```bash
.\batch_files\run_scheduled_processor.bat
```

**Continuous Processing (Every 30 minutes):**
```bash
.\batch_files\run_continuous_processor.bat
```

**Command Line Options:**
```bash
# Process all pending files once
python scheduled_processor.py --mode single

# Continuous processing every 15 minutes
python scheduled_processor.py --mode continuous --interval 15

# Process specific file by ID
python scheduled_processor.py --file-id 123
```

### 💡 **Key Benefits:**

#### **🔄 Separation of Concerns:**
- **Upload Stage**: Fast file upload → JSON storage
- **Processing Stage**: Scheduled data extraction and validation
- **Data Stage**: Clean, processed company data

#### **📈 Scalability:**
- Handle large files without blocking GUI
- Batch process multiple files
- Retry failed processing automatically

#### **🔍 Traceability:**
- Complete audit trail of uploads
- Track data lineage from source to processed
- Monitor processing jobs and errors

#### **🛡️ Data Integrity:**
- Duplicate file detection
- Error handling and retry logic
- Validation and data quality checks

#### **⚡ Performance:**
- Non-blocking file uploads
- Efficient JSON storage with indexing
- Scheduled processing during off-hours

### 🎯 **Use Cases:**

#### **Immediate Upload:**
1. User uploads Excel file → Stored as JSON immediately
2. File available for preview and validation
3. Processing scheduled for later execution

#### **Batch Processing:**
1. Multiple files uploaded throughout the day
2. Scheduled processor runs every 30 minutes
3. All pending files processed automatically

#### **Data Pipeline:**
1. Files → JSON Storage → Processing Queue → Company Data
2. Full audit trail and error tracking
3. Easy reprocessing of failed jobs

### 🔧 **Technical Implementation:**

#### **JSON Storage Format:**
```json
{
  "columns": ["Company Name", "LinkedIn URL", "Website"],
  "data": [
    {
      "Company Name": "ABC Corp",
      "LinkedIn URL": "https://linkedin.com/company/abc",
      "Website": "https://abc.com"
    }
  ],
  "metadata": {
    "total_rows": 1,
    "total_columns": 3,
    "upload_timestamp": "2025-10-02T10:30:00",
    "file_extension": ".xlsx"
  }
}
```

#### **Smart Column Mapping:**
- Automatic detection of company names, LinkedIn URLs, websites
- Industry and company size identification
- Revenue data extraction
- Configurable mapping rules

#### **Processing Job Configuration:**
```json
{
  "auto_column_mapping": true,
  "data_validation": true,
  "duplicate_detection": true,
  "max_retries": 3,
  "notification_email": "admin@company.com"
}
```

### 📋 **Next Steps:**

1. **✅ Ready to Use**: Upload files and schedule processing
2. **🔄 Schedule Jobs**: Set up automated processing (cron/Task Scheduler)
3. **📊 Monitor**: Use GUI to track uploads and processing
4. **🚀 Scale**: Add more processing rules and validation logic

### 📞 **Support & Troubleshooting:**

- **Logs**: Check `logs/scheduled_processor.log` for processing details
- **Database**: Use GUI Statistics tab for system health
- **Processing**: Failed jobs are automatically retried up to 3 times
- **Recovery**: Reprocess specific files using file ID parameter

---

## 🎉 **SYSTEM READY FOR PRODUCTION USE!**

Your file upload system now supports:
- ✅ JSON-based file storage
- ✅ Scheduled data processing  
- ✅ Complete job management
- ✅ Comprehensive monitoring
- ✅ Scalable architecture