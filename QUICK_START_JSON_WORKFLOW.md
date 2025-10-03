# 🚀 QUICK START GUIDE - JSON Upload Workflow

## 📋 **WORKFLOW SUMMARY:**

Your new system now stores uploaded files as JSON in PostgreSQL and processes them separately:

1. **📁 Upload Stage**: Files → JSON storage (immediate)
2. **⏳ Processing Stage**: JSON → Company data (scheduled)
3. **📊 Management Stage**: Monitor and export (ongoing)

---

## 🎯 **STEP-BY-STEP USAGE:**

### **1. Start the JSON Upload GUI**
```bash
.\batch_files\run_json_upload_gui.bat
```
**OR**
```bash
python gui\file_upload_json_gui.py
```

### **2. Upload Your Excel/CSV File**
- Click **"Upload File"** in Tab 1
- Select your Excel/CSV file
- File is immediately stored as JSON
- Status shows "pending" for processing

### **3. Process the Uploaded Data**
**Option A - Enhanced Single Processing (RECOMMENDED):**
```bash
python enhanced_scheduled_processor.py --mode single
```

**Option B - Enhanced Continuous Processing:**
```bash
python enhanced_scheduled_processor.py --mode continuous --interval 30
```

**Option C - Interactive Monitor:**
```bash
.\batch_files\run_enhanced_processor_monitor.bat
```

**Option D - From GUI:**
- Go to Tab 4 (Processing Jobs)
- Click **"Process All Pending"**

### **🚀 LinkedIn Scraper Integration**
The enhanced processor automatically:
- ✅ Extracts **Company Size** from LinkedIn profiles (e.g., "77,559 employees")
- ✅ Extracts **Industry** from LinkedIn pages (e.g., "Motor Vehicle Manufacturing") 
- ✅ Attempts **Revenue** extraction from company websites
- ✅ Updates database with scraped data and file traceability
- ✅ Provides real-time progress monitoring with 4 processing stages

### **4. View Results**
- Tab 3: View processed company data
- Tab 2: Monitor uploaded files status
- Tab 5: System statistics and exports

---

## 🧪 **TEST THE SYSTEM:**

### **Step 1: Use Test Data**
```bash
# Test file is ready at: test_data\json_test.xlsx
# Contains 2 sample companies (Microsoft, Apple)
```

### **Step 2: Upload Test File**
1. Run `.\batch_files\run_json_upload_gui.bat`
2. Upload `test_data\json_test.xlsx`
3. Verify JSON storage in Tab 2

### **Step 3: Process Data**
1. Run `python enhanced_scheduled_processor.py --mode single`
2. Check Tab 3 for processed results
3. Verify company data extraction with LinkedIn scraped data

### **🔄 Job Status Tracking**
Monitor complete processing pipeline:
- **⏳ Queued**: Job created, waiting to start
- **🔄 Started**: Processing initiated  
- **⚡ Processing**: LinkedIn scraping in progress (25% → 50% → 75% → 100%)
- **✅ Completed**: All stages finished successfully
- **❌ Error**: Processing failed (with error details)

---

## 📊 **DATABASE TABLES:**

### **`file_upload` (JSON Storage)**
- Stores raw uploaded files as JSON
- Status: pending → completed/failed
- Full audit trail and metadata

### **`company_data` (Processed Results)**
- Clean, structured company information
- Extracted from JSON files
- Ready for analysis and export

### **`processing_jobs` (Job Management)**
- Tracks all processing jobs
- Retry logic for failed jobs
- Scheduling and execution history

---

## 🔧 **ADVANCED FEATURES:**

### **Automatic Column Mapping**
The system intelligently maps columns:
- `Company Name` → company_name
- `LinkedIn URL` → linkedin_url
- `Website` → company_website
- `Industry` → industry
- `Company Size` → company_size
- `Revenue` → revenue

### **Duplicate Detection**
- File hash checking prevents duplicate uploads
- Intelligent data deduplication
- Maintains data integrity

### **Job Scheduling**
```bash
# Process every 30 minutes
python enhanced_scheduled_processor.py --mode continuous --interval 30

# Process specific file type
python enhanced_scheduled_processor.py --mode single --scraper-type complete

# Single run processing  
python enhanced_scheduled_processor.py --mode single
```

### **Job Status Monitoring**
```bash
# Check current job status
python -c "import sys; sys.path.append('database_config'); from enhanced_scheduled_processor import EnhancedScheduledProcessor; processor = EnhancedScheduledProcessor(); processor.get_job_status_summary()"

# View processing statistics
python -c "import sys; sys.path.append('database_config'); from enhanced_scheduled_processor import EnhancedScheduledProcessor; processor = EnhancedScheduledProcessor(); processor.get_processing_statistics()"
```

### **Export Capabilities**
- Export all uploaded files
- Export processed company data
- Export system statistics
- Multiple formats supported

---

## 📁 **FILE LOCATIONS:**

```
📁 Uploaded Files → JSON Storage → PostgreSQL file_upload table
📊 Processed Data → PostgreSQL company_data table  
📋 Job Logs → logs\scheduled_processor.log
⚙️ GUI Logs → Main GUI window + database logs
```

---

## 🚨 **TROUBLESHOOTING:**

### **GUI Not Opening:**
- Check PostgreSQL is running (localhost:5432)
- Verify database connection in database_config\postgresql_config.py

### **Processing Failed:**
- Check logs\scheduled_processor.log
- Failed jobs auto-retry up to 3 times
- Use GUI Tab 4 to manually retry

### **Data Not Appearing:**
- Verify file upload completed (Tab 2)
- Check processing job status (Tab 4)
- Run manual processing if needed

---

## 💡 **BENEFITS OF NEW SYSTEM:**

✅ **Fast Uploads**: Files stored as JSON immediately
✅ **Scheduled Processing**: Non-blocking data extraction
✅ **Complete Audit**: Full traceability of data flow
✅ **Scalable**: Handle large files and batch processing
✅ **Recoverable**: Retry failed jobs, reprocess data
✅ **Flexible**: Easy to add new processing rules

---

## 🎉 **YOU'RE READY TO GO!**

1. **Upload**: Use the JSON GUI to upload your files
2. **Process**: Run scheduled processor to extract data
3. **Monitor**: Track everything through the GUI tabs
4. **Export**: Get your processed company data

**Your LinkedIn data scraping system now has enterprise-grade file processing capabilities!** 🚀