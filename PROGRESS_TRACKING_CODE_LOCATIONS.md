# Where to Add Progress Tracking in Code

## Summary
The progress tracking needs to be added in **2 key locations** where the actual record-by-record processing happens:

1. **In `database_config/file_upload_processor.py`** - During LinkedIn scraping loop
2. **In `backend_api/main.py`** - Already has the `_update_file_progress()` helper function

---

## 📍 Location 1: During Initial Data Import

**File:** `database_config/file_upload_processor.py`  
**Method:** `process_uploaded_file()` around line 580

### Add Progress Tracking After Data is Loaded:

```python
def process_uploaded_file(self, file_upload_id: str, user_id: str = None) -> bool:
    """Process an uploaded file and move data to company_data table with LinkedIn scraping"""
    try:
        # ... existing code ...
        
        # Convert JSON data back to DataFrame
        df = pd.DataFrame(raw_data['data'])
        
        # 🆕 ADD THIS: Initialize progress tracking
        total_records = len(df)
        from backend_api.main import _update_file_progress
        _update_file_progress(
            file_upload_id=int(file_upload_id),
            total=total_records,
            processed=0,
            status_message=f"Starting processing {total_records} records...",
            success=0,
            errors=0
        )
        
        # Apply column mapping
        mapped_df = self.apply_column_mapping(df)
        
        # ... rest of existing code ...
```

---

## 📍 Location 2: During LinkedIn Scraping Loop

**File:** `database_config/file_upload_processor.py`  
**Method:** `_perform_linkedin_scraping()` around line 476

### Add Progress Updates in the Processing Loop:

```python
def _perform_linkedin_scraping(self, file_upload_id: str, df: pd.DataFrame) -> int:
    """Perform LinkedIn scraping on the companies and update database"""
    try:
        print(f"🔍 Starting LinkedIn scraping for {len(df)} companies")
        
        # Initialize the LinkedIn scraper
        scraper = CompleteCompanyScraper(...)
        
        # Perform the scraping
        enhanced_df = scraper.process_companies(...)
        
        # 🆕 ADD THIS: Import progress update function
        from backend_api.main import _update_file_progress
        
        # Update database with scraped data
        scraped_count = 0
        error_count = 0
        total_records = len(enhanced_df)
        
        # 🆕 MODIFY THIS LOOP: Add progress tracking
        for index, row in enhanced_df.iterrows():
            try:
                company_id = row.get('id')
                company_name = row.get('company_name', row.get('Company_Name', ''))
                
                # ... existing update logic ...
                
                if update_data:
                    # ... existing database update code ...
                    scraped_count += 1
                    
            except Exception as e:
                print(f"Error updating company: {e}")
                error_count += 1
            
            # 🆕 ADD THIS: Update progress every 10 records or on last record
            if (index + 1) % 10 == 0 or (index + 1) == total_records:
                _update_file_progress(
                    file_upload_id=int(file_upload_id),
                    total=total_records,
                    processed=index + 1,
                    status_message=f"Scraping company {index + 1}/{total_records}: {company_name[:50]}",
                    success=scraped_count,
                    errors=error_count
                )
        
        print(f"✅ Scraping completed: {scraped_count} successful, {error_count} errors")
        return scraped_count
```

---

## 📍 Location 3: At Processing Completion

**File:** `database_config/file_upload_processor.py`  
**Method:** `process_uploaded_file()` around line 630

### Mark Final Progress When Complete:

```python
# Perform LinkedIn scraping if available
scraped_count = 0
if LINKEDIN_SCRAPER_AVAILABLE:
    scraped_count = self._perform_linkedin_scraping(file_upload_id, mapped_df)
else:
    print("⚠️ LinkedIn scraper not available, skipping scraping step")

# 🆕 ADD THIS: Final progress update
from backend_api.main import _update_file_progress
_update_file_progress(
    file_upload_id=int(file_upload_id),
    total=len(mapped_df),
    processed=len(mapped_df),
    status_message=f"Processing complete! Scraped {scraped_count} companies",
    success=scraped_count,
    errors=len(mapped_df) - scraped_count
)

# Update all three tables for complete sync and mark job as completed
self.mark_job_as_completed(file_upload_id, len(mapped_df))
self.sync_processing_completion(file_upload_id, 'completed', len(mapped_df), ...)
```

---

## 🎯 Complete Example: Modified _perform_linkedin_scraping Method

Here's the complete modified method with progress tracking:

```python
def _perform_linkedin_scraping(self, file_upload_id: str, df: pd.DataFrame) -> int:
    """Perform LinkedIn scraping on the companies and update database"""
    try:
        print(f"🔍 Starting LinkedIn scraping for {len(df)} companies")
        
        # 🆕 Import progress tracking
        from backend_api.main import _update_file_progress
        
        # Initialize the LinkedIn scraper
        scraper = CompleteCompanyScraper(self.config.config if hasattr(self.config, 'config') else None)
        
        # Create a copy of the dataframe for scraping
        scraping_df = df.copy()
        
        # Map our column names to what the scraper expects
        if 'linkedin_url' in scraping_df.columns:
            scraping_df['LinkedIn_URL'] = scraping_df['linkedin_url']
        if 'company_website' in scraping_df.columns:
            scraping_df['Company_Website'] = scraping_df['company_website']
        if 'company_name' in scraping_df.columns:
            scraping_df['Company_Name'] = scraping_df['company_name']
        
        # 🆕 Initial progress
        total_records = len(scraping_df)
        _update_file_progress(
            file_upload_id=int(file_upload_id),
            total=total_records,
            processed=0,
            status_message="Starting LinkedIn scraping...",
            success=0,
            errors=0
        )
        
        # Perform the scraping
        enhanced_df = scraper.process_companies(
            scraping_df,
            linkedin_column='LinkedIn_URL',
            website_column='Company_Website',
            company_name_column='Company_Name'
        )
        
        # Update database with scraped data
        scraped_count = 0
        error_count = 0
        
        for index, row in enhanced_df.iterrows():
            company_name = row.get('company_name', row.get('Company_Name', ''))
            
            try:
                company_id = row.get('id')
                
                # Prepare update data
                update_data = {}
                
                if row.get('Company_Size_Enhanced') and row.get('Company_Size_Enhanced') != 'Not Processed':
                    update_data['company_size'] = row['Company_Size_Enhanced']
                
                if row.get('Industry_Enhanced') and row.get('Industry_Enhanced') != 'Not Processed':
                    update_data['industry'] = row['Industry_Enhanced']
                
                if row.get('Revenue_Enhanced') and row.get('Revenue_Enhanced') != 'Not Processed':
                    update_data['revenue'] = row['Revenue_Enhanced']
                
                # Update the database if we have data to update
                if update_data and company_id:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_fields = []
                    for field, value in update_data.items():
                        update_fields.append(f"{field} = '{str(value).replace(chr(39), chr(39)+chr(39))}'")
                    
                    if update_fields:
                        update_query = f"""
                        UPDATE company_data 
                        SET {', '.join(update_fields)}, processing_status = 'completed', processed_date = '{current_time}'
                        WHERE id = '{company_id}'
                        """
                        self.db_connection.execute_query(update_query)
                        scraped_count += 1
                
            except Exception as e:
                print(f"Error updating company {company_name}: {e}")
                error_count += 1
            
            # 🆕 Update progress every 10 records or on last record
            if (index + 1) % 10 == 0 or (index + 1) == total_records:
                _update_file_progress(
                    file_upload_id=int(file_upload_id),
                    total=total_records,
                    processed=index + 1,
                    status_message=f"Processing company {index + 1}/{total_records}: {company_name[:40]}...",
                    success=scraped_count,
                    errors=error_count
                )
        
        print(f"✅ LinkedIn scraping completed: {scraped_count} companies updated")
        return scraped_count
        
    except Exception as e:
        print(f"❌ Error in LinkedIn scraping: {str(e)}")
        # 🆕 Mark as error
        try:
            from backend_api.main import _update_file_progress
            _update_file_progress(
                file_upload_id=int(file_upload_id),
                total=len(df),
                processed=len(df),
                status_message=f"Error: {str(e)}",
                success=0,
                errors=len(df)
            )
        except:
            pass
        return 0
```

---

## 🔧 How This Works:

1. **Line 542-565 (process_uploaded_file)**: Initialize progress at 0% when starting
2. **Line 476-540 (_perform_linkedin_scraping)**: Update progress every 10 records during the loop
3. **Line 630-640 (process_uploaded_file)**: Final progress update at 100% when complete

## 📊 What the UI Sees:

```
0% - "Starting processing 100 records..."
10% - "Processing company 10/100: Acme Corp..."
20% - "Processing company 20/100: Tech Solutions..."
...
100% - "Processing complete! Scraped 95 companies"
```

## ✅ Next Step:

Add these code changes to the file, then test by uploading a file and monitoring the `/api/files/progress/{file_upload_id}` endpoint!
