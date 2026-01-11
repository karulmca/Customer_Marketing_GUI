# Real-Time Progress Tracking Implementation Guide

## Overview
This document describes the real-time progress tracking system that allows the UI to display processing status and completion percentage for file uploads.

## Database Schema Changes

### New Fields in `file_upload` Table:

```sql
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS total_records INTEGER DEFAULT 0;
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS processed_records INTEGER DEFAULT 0;
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS progress_percentage DECIMAL(5,2) DEFAULT 0.00;
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS current_status_message TEXT DEFAULT '';
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS processing_start_time TIMESTAMP NULL;
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS last_progress_update TIMESTAMP NULL;
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS success_count INTEGER DEFAULT 0;
ALTER TABLE file_upload ADD COLUMN IF NOT EXISTS error_count INTEGER DEFAULT 0;
```

### Field Descriptions:

- **total_records**: Total number of records to be processed
- **processed_records**: Number of records processed so far  
- **progress_percentage**: Current progress (0.00 to 100.00)
- **current_status_message**: Human-readable status message (e.g., "Processing company 45/100")
- **processing_start_time**: When processing started
- **last_progress_update**: Last time progress was updated
- **success_count**: Number of successfully processed records
- **error_count**: Number of records that failed processing

## Setup Instructions

### Step 1: Add Database Fields

Run the migration script to add progress tracking fields:

```bash
cd C:\Viji\Automation\Oct_7th_Code\Customer_Marketing_GUI
python add_progress_tracking.py
```

### Step 2: Update Backend (Already Done)

The backend now includes:
- `/api/files/progress/{file_upload_id}` - Get real-time progress
- `_update_file_progress()` - Helper function to update progress

### Step 3: Update Frontend (To Do)

Add progress polling to your React frontend:

```javascript
// Example: Poll for progress every 2 seconds
const pollProgress = async (fileUploadId) => {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/files/progress/${fileUploadId}?session_id=${sessionId}`
      );
      const data = await response.json();
      
      // Update UI with progress
      setProgress({
        percentage: data.progress_percentage,
        message: data.current_status_message,
        processed: data.processed_records,
        total: data.total_records,
        successCount: data.success_count,
        errorCount: data.error_count,
        etaSeconds: data.eta_seconds
      });
      
      // Stop polling if complete
      if (data.is_complete) {
        clearInterval(interval);
        console.log('Processing complete!');
      }
      
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  }, 2000); // Poll every 2 seconds
  
  return interval;
};
```

## API Endpoint Usage

### Get File Progress

**Endpoint:** `GET /api/files/progress/{file_upload_id}`

**Query Parameters:**
- `session_id` (optional): User session ID

**Response:**
```json
{
  "file_upload_id": 123,
  "file_name": "companies.xlsx",
  "status": "processing",
  "total_records": 100,
  "processed_records": 45,
  "progress_percentage": 45.0,
  "current_status_message": "Processing company 45/100: Acme Corp",
  "processing_start_time": "2026-01-11T17:30:00",
  "last_progress_update": "2026-01-11T17:35:30",
  "success_count": 42,
  "error_count": 3,
  "processed_date": null,
  "processing_error": null,
  "eta_seconds": 120,
  "is_complete": false
}
```

### Status Values:

- `pending`: Waiting to be processed
- `processing`: Currently being processed  
- `completed`: Successfully completed
- `failed`: Processing failed
- `error`: Error occurred

## Backend Implementation

### Updating Progress During Processing

In your processing code, call `_update_file_progress()`:

```python
from backend_api.main import _update_file_progress

# At start of processing
_update_file_progress(
    file_upload_id=123,
    total=100,
    processed=0,
    status_message="Starting processing...",
    success=0,
    errors=0
)

# During processing (e.g., after each record)
for i, record in enumerate(records):
    try:
        # Process record...
        success_count += 1
    except Exception as e:
        error_count += 1
    
    # Update progress every 10 records or on last record
    if (i + 1) % 10 == 0 or (i + 1) == len(records):
        _update_file_progress(
            file_upload_id=123,
            total=len(records),
            processed=i + 1,
            status_message=f"Processing record {i+1}/{len(records)}",
            success=success_count,
            errors=error_count
        )
```

## Example Frontend Component

```javascript
import React, { useState, useEffect } from 'react';
import { LinearProgress, Typography, Box } from '@mui/material';

const FileProgressTracker = ({ fileUploadId, sessionId }) => {
  const [progress, setProgress] = useState({
    percentage: 0,
    message: '',
    processed: 0,
    total: 0,
    isComplete: false
  });

  useEffect(() => {
    if (!fileUploadId) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/files/progress/${fileUploadId}?session_id=${sessionId}`
        );
        const data = await response.json();
        
        setProgress({
          percentage: data.progress_percentage,
          message: data.current_status_message,
          processed: data.processed_records,
          total: data.total_records,
          isComplete: data.is_complete,
          successCount: data.success_count,
          errorCount: data.error_count,
          etaSeconds: data.eta_seconds
        });

        if (data.is_complete) {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [fileUploadId, sessionId]);

  const formatETA = (seconds) => {
    if (!seconds) return 'Calculating...';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      <Typography variant="body2" color="textSecondary">
        {progress.message}
      </Typography>
      
      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
        <Box sx={{ width: '100%', mr: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress.percentage} 
          />
        </Box>
        <Box sx={{ minWidth: 35 }}>
          <Typography variant="body2" color="textSecondary">
            {`${Math.round(progress.percentage)}%`}
          </Typography>
        </Box>
      </Box>

      <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="caption" color="textSecondary">
          {progress.processed} / {progress.total} records
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Success: {progress.successCount} | Errors: {progress.errorCount}
        </Typography>
        {progress.etaSeconds && (
          <Typography variant="caption" color="textSecondary">
            ETA: {formatETA(progress.etaSeconds)}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default FileProgressTracker;
```

## Testing

### 1. Test Database Migration:
```bash
python add_progress_tracking.py
```

### 2. Test API Endpoint:
```bash
curl "http://localhost:8000/api/files/progress/123?session_id=your-session-id"
```

### 3. Test Frontend Integration:
- Upload a file
- Monitor the progress in real-time
- Verify completion status updates

## Benefits

✅ **Real-time visibility**: Users see exactly what's happening  
✅ **Better UX**: Progress bar instead of "waiting..."  
✅ **Error tracking**: See how many records succeeded vs failed  
✅ **ETA calculation**: Users know how long to wait  
✅ **Debugging**: Detailed status messages help troubleshoot issues  

## Next Steps

1. Run `add_progress_tracking.py` to update database
2. Deploy updated backend
3. Update frontend to poll progress endpoint
4. Add progress bar component to file upload screen
5. Test with real file uploads

## Notes

- Progress updates every 10 records (configurable)
- Frontend polls every 2 seconds (configurable)
- ETA calculated based on processing rate
- Polling stops automatically when processing completes
