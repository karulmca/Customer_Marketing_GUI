# Fix for Sequential File Processing Issue

## Problem Description

**Issue:** When multiple files are uploaded and marked as "pending", the automated scheduler was processing ALL pending files simultaneously, causing:
1. Multiple files changing to "processing" status at the same time
2. Status confusion - files showing as "processing" but not actually being processed sequentially
3. Violation of the single-job-per-user constraint

**Root Cause:** The `run_automated_jobs.py` file was fetching ALL pending files at once and iterating through them, which caused all files to have their status updated to "processing" simultaneously before actual processing began.

## Solution Implemented

### File Modified: `backend_api/automated_job/run_automated_jobs.py`

**Changes Made:**
1. **Sequential Processing Loop:** Instead of fetching all pending files at once, the system now:
   - Fetches ONE pending file at a time
   - Processes it completely (pending → processing → completed/failed)
   - Only after completion, fetches the next pending file
   - Repeats until no more pending files or limit reached

2. **Key Improvements:**
   ```python
   # OLD APPROACH (PROBLEMATIC):
   # Fetch ALL pending files → Process each → Mark complete
   cursor.execute("SELECT ... WHERE processing_status = 'pending' LIMIT 10")
   rows = cursor.fetchall()  # Gets ALL 10 files
   for row in rows:
       process_file(row)  # All marked as processing simultaneously
   
   # NEW APPROACH (FIXED):
   # Loop: Fetch ONE → Process → Complete → Fetch next ONE
   for iteration in range(limit):
       cursor.execute("SELECT ... WHERE processing_status = 'pending' LIMIT 1")
       row = cursor.fetchone()  # Gets only 1 file
       if not row:
           break
       process_file(row)  # Only this one file is processing
       # Loop repeats, fetching next pending file
   ```

3. **Status Flow Per File:**
   - File 1: pending → processing → completed
   - File 2: pending (waits) → processing → completed  
   - File 3: pending (waits) → processing → completed

## How to Verify the Fix

### 1. Monitor Database Status in Real-Time

Open a database query tool and run this query repeatedly:

```sql
-- Check file_upload status
SELECT 
    id, 
    file_name, 
    processing_status, 
    upload_date,
    processed_date,
    uploaded_by
FROM file_upload 
WHERE processing_status IN ('pending', 'processing', 'completed', 'failed')
ORDER BY upload_date DESC;

-- Check processing_jobs status
SELECT 
    pj.id,
    pj.file_upload_id,
    pj.job_status,
    fu.file_name,
    pj.started_at,
    pj.completed_at
FROM processing_jobs pj
JOIN file_upload fu ON pj.file_upload_id = fu.id
WHERE pj.job_status IN ('queued', 'processing', 'completed', 'failed')
ORDER BY pj.scheduled_at DESC;
```

**Expected Behavior:**
- At any given time, only ONE file should have `processing_status = 'processing'`
- Files should transition: pending → processing → completed (one at a time)
- No multiple files should be "processing" simultaneously

### 2. Upload Multiple Files and Monitor

1. Upload 3-5 files to the system (don't process manually)
2. Wait for the scheduler to run (or trigger manually via API)
3. Watch the file list in the UI
4. **Expected:** Files process one by one, not all at once

### 3. Check Backend Logs

Monitor the application logs for these patterns:

```
🔄 Processing file 1/5: id=xxx filename=file1.csv
✅ Successfully processed file xxx (file1.csv)
🔄 Processing file 2/5: id=yyy filename=file2.csv
✅ Successfully processed file yyy (file2.csv)
...
```

**Expected:** Sequential processing with clear start/complete for each file

### 4. Verify Single-Job-Per-User Logic

If multiple users upload files:
```sql
SELECT 
    uploaded_by,
    COUNT(*) as pending_count,
    SUM(CASE WHEN processing_status = 'processing' THEN 1 ELSE 0 END) as processing_count
FROM file_upload
WHERE processing_status IN ('pending', 'processing')
GROUP BY uploaded_by;
```

**Expected:** Each user should have at most 1 file in "processing" status

## Testing Steps

1. **Start both servers:**
   ```bash
   # Backend (already running)
   # Frontend (already running)
   ```

2. **Upload multiple test files:**
   - Go to http://localhost:3000
   - Upload 3-4 CSV files using "Upload as JSON"
   - Do NOT click "Process" manually

3. **Trigger automated processing:**
   - Option A: Wait for scheduler (runs every 2 minutes by default)
   - Option B: Manually trigger via API:
     ```bash
     curl -X POST "http://localhost:8000/api/jobs/process-pending?session_id=YOUR_SESSION"
     ```

4. **Monitor the file list:**
   - Refresh the page or watch auto-refresh
   - Verify only ONE file shows "processing" at a time
   - Each file should complete before the next starts

5. **Check database:**
   - Run the SQL queries above
   - Confirm status transitions are sequential

## Configuration

The scheduler interval can be adjusted in `config.json`:

```json
{
  "job_processing": {
    "single_job_per_user": true,
    "scheduler_interval_minutes": 2,
    "max_processing_time_minutes": 30
  }
}
```

## Related Files

- **Fixed File:** `backend_api/automated_job/run_automated_jobs.py`
- **Status Update Logic:** `database_config/file_upload_processor.py`
- **Scheduler:** `backend_api/main.py` (_process_pending_uploads function)
- **Frontend Display:** `frontend/src/components/FileUploadDashboard.js`

## Summary

✅ **Fix Applied:** Sequential file processing (one at a time)
✅ **Status Flow:** pending → processing → completed (proper transitions)
✅ **No Simultaneous Processing:** Only one file in "processing" state at any time
✅ **Scraper Logic:** Unchanged and working correctly

The fix ensures that:
1. Files are processed sequentially, not concurrently
2. Status updates reflect actual processing state
3. Users see accurate progress for each file
4. System resources are not overwhelmed by parallel processing
