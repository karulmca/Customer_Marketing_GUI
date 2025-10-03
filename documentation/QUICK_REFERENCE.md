# Enhanced Processing System - Quick Reference

## 🚀 Getting Started

### 1. Start the Enhanced GUI
- **File**: `batch_files\run_enhanced_gui.bat`
- **What it does**: Opens the main GUI for file upload and monitoring
- **Features**: 5 tabs - Upload, Files, Data, Jobs, Statistics

### 2. Upload a File
1. Open the GUI using the batch file above
2. Go to "📁 File Upload (JSON)" tab
3. Click "Browse and Upload File"
4. Select your Excel/CSV file with company data
5. File gets stored in database as JSON for processing

### 3. Process Files

#### Option A: Single Processing Run
```batch
# Run once and complete all pending files
python enhanced_scheduled_processor.py --mode single
```

#### Option B: Continuous Processing
```batch
# Process every 30 minutes
python enhanced_scheduled_processor.py --mode continuous --interval 30
```

#### Option C: Interactive Monitor
```batch
# Interactive menu-driven processing
batch_files\run_enhanced_processor_monitor.bat
```

### 4. Check Processing Status

#### Quick Statistics
```batch
# Show current processing stats
batch_files\check_processing_stats.bat
```

#### Detailed Statistics
- Open GUI → Go to "⚙️ Processing Jobs" tab → Click "📊 Show Processing Stats"

## 📊 What Gets Processed

For each company in your uploaded file, the system extracts:

1. **Company Size** (from LinkedIn profile)
2. **Industry** (from LinkedIn company page)  
3. **Revenue** (from company website)

## 📈 Monitoring Progress

### Real-time Status Updates
- Processing shows stage-by-stage progress
- Each stage shows percentage completion
- Detailed logging of extraction results

### Processing Stages
1. **Data Preparation** (25%) - Loading and cleaning data
2. **File Preparation** (50%) - Creating temporary processing files
3. **LinkedIn Scraping** (75%) - Extracting company data
4. **Database Storage** (100%) - Saving final results

## 🔧 Column Requirements

Your Excel/CSV file should have columns for:
- **Company Name** (Company_Name, Company Name, etc.)
- **LinkedIn URL** (LinkedIn_URL, LinkedIn URL, etc.)
- **Company Website** (Company_Website, Website, etc.)

*Note: Column names are auto-detected and mapped*

## ⚡ Quick Commands

```powershell
# Check if database is running
python -c "import sys; sys.path.append('database_config'); from postgresql_config import PostgreSQLConfig; print('Database OK')"

# Process specific file type
python enhanced_scheduled_processor.py --mode single --scraper-type complete

# Test entire workflow
batch_files\test_enhanced_workflow.bat
```

## 📋 Current System Status

After setup completion, you have:
- ✅ **26 companies** in database
- ✅ **3 files** processed successfully
- ✅ **Company Size**: 23.1% extraction rate
- ✅ **Industry**: 30.8% extraction rate  
- ✅ **Revenue**: 23.1% extraction rate

## 🆘 Troubleshooting

### Database Issues
```batch
# Check PostgreSQL is running
services.msc → PostgreSQL service should be "Running"
```

### Processing Issues  
```batch
# Check logs in GUI
GUI → Statistics tab → View detailed logs
```

### File Upload Issues
- Ensure file has company data columns
- Check file is not corrupted or password-protected
- Try uploading a smaller test file first

## 📞 Support

For detailed information, refer to:
- `documentation\ENHANCED_SYSTEM_IMPLEMENTATION_SUMMARY.md`
- `documentation\USAGE_GUIDE.md`
- Log files in the application for troubleshooting