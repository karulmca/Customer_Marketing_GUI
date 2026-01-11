# Multi-File Download - Quick Start Guide

## 📋 Overview
Users can now download multiple processed files at once as a ZIP archive.

## 🎯 How to Use

### Step 1: Navigate to Data Management Tab
1. Log in to the application
2. Click on the **"Uploaded Files & Data Management"** tab (second tab)

### Step 2: Select Files
You have multiple options:

#### Option A: Select Individual Files
- Click the checkbox next to each file you want to download
- Only **completed** files can be selected (others are disabled)

#### Option B: Select All Completed Files
- Click the checkbox in the table header
- All completed files will be selected automatically

### Step 3: Download
1. Click the **"Download Selected (N)"** button at the top
2. Wait for the download to complete
3. Files will be downloaded as:
   - **Single file**: Individual Excel file
   - **Multiple files**: ZIP archive

### Step 4: Clear Selection (Optional)
- Click **"Clear Selection"** to deselect all files
- Selection is automatically cleared after successful download

---

## 📊 Features

### ✅ What You Can Do
- ✔️ Select multiple completed files at once
- ✔️ Download as ZIP archive
- ✔️ Select all completed files with one click
- ✔️ View selection count in real-time
- ✔️ Clear selection anytime

### ❌ Limitations
- ⚠️ Only **completed** files can be selected
- ⚠️ Pending/Failed/Processing files cannot be downloaded
- ⚠️ Must be logged in to download files

---

## 📦 Downloaded File Structure

### Single File Download
```
processed_company_data.xlsx
```

### Multiple Files Download
```
processed_files_20260111_143022.zip
  ├── processed_file1.xlsx
  ├── processed_file2.xlsx
  └── processed_file3.xlsx
```

---

## 💡 Tips & Best Practices

1. **Check File Status**: Ensure files show "Completed" status before selecting
2. **Large Downloads**: For many files, be patient - ZIP creation may take a moment
3. **Original Names**: Downloaded files preserve their original names
4. **Automatic Cleanup**: Selection clears after successful download
5. **Browser Downloads**: Check your browser's download folder for the ZIP file

---

## 🔧 Troubleshooting

### Issue: Checkbox is Disabled
**Solution**: File must be in "Completed" status. Process the file first.

### Issue: Download Button is Disabled
**Solution**: Select at least one completed file.

### Issue: Download Failed
**Possible Causes**:
- Network connection issue
- Session expired (log in again)
- Selected files have no processed data

### Issue: ZIP File is Empty
**Solution**: Ensure selected files have completed processing with data.

---

## 🎨 UI Elements

### Checkbox States
- ☐ **Unchecked**: File not selected
- ☑ **Checked**: File selected for download
- ☐ **Disabled**: File not available for download (not completed)

### Header Checkbox States
- ☐ **Unchecked**: No files selected
- ☑ **Checked**: All completed files selected
- ◫ **Indeterminate**: Some files selected

### Button States
- **"Download Selected (0)"**: Disabled, no files selected
- **"Download Selected (3)"**: Ready to download 3 files
- **"Downloading..."**: Download in progress

---

## 📱 Screenshots Reference

### 1. Data Management Tab
```
┌─────────────────────────────────────────┐
│ [Download Selected (3)]  [Clear]        │
│                                         │
│ [☑] File Details  Status  Stats  Actions│
│ [☑] file1.xlsx    ✅       ...    [📥]  │
│ [☑] file2.xlsx    ✅       ...    [📥]  │
│ [☐] file3.xlsx    ⏳       ...    [ ]   │
│ [☑] file4.xlsx    ✅       ...    [📥]  │
└─────────────────────────────────────────┘
```

### 2. Select All State
```
┌─────────────────────────────────────────┐
│ [☑] = Select All Completed Files        │
└─────────────────────────────────────────┘
```

### 3. Bulk Actions Toolbar
```
┌─────────────────────────────────────────┐
│ [📥 Download Selected (3)] [Clear]      │
└─────────────────────────────────────────┘
```

---

## 📞 Support

If you encounter any issues:
1. Check the browser console for error messages
2. Verify your session is active (try refreshing the page)
3. Ensure files are fully processed before attempting download
4. Contact system administrator for persistent issues

---

## 🚀 What's New

**Version 2.0 Features:**
- ✨ Multi-file selection with checkboxes
- ✨ Bulk download as ZIP archive
- ✨ Select all completed files option
- ✨ Visual selection counter
- ✨ One-click selection clearing
- ✨ Preserved original filenames
- ✨ Smart download (single file or ZIP based on selection)

---

**Last Updated**: January 11, 2026  
**Feature Status**: ✅ Production Ready
