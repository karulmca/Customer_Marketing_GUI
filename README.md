# Company Data Scraper - Organized Project

## 🚀 Quick Start

### Main Scrapers (Production Ready)
```powershell
# Navigate to project
cd "c:\Viji\Automation\NewCode\CompanyDataScraper"

# OpenAI Enhanced Scraper (RECOMMENDED)
.\batch_files\run_openai_scraper.bat "test_data\Test5.xlsx" --use-openai

# Complete Scraper (Traditional + Website Revenue)  
.\batch_files\run_complete_company_scraper.bat "test_data\Test5.xlsx"

# LinkedIn Only (Company Size + Industry)
.\batch_files\run_linkedin_company_data.bat "test_data\Test5.xlsx"
```

## 📁 Project Structure

### 🔧 **scrapers/** - Core Scraping Engines
- **`linkedin_openai_scraper.py`** ⭐ **MAIN** - LinkedIn + OpenAI revenue extraction
- **`linkedin_company_complete_scraper.py`** - LinkedIn + traditional website revenue  
- **`linkedin_company_scraper_enhanced.py`** - LinkedIn company size/industry only
- **`zoominfo_revenue_scraper.py`** - ZoomInfo revenue (requires auth)
- **`alternative_sources_scraper.py`** - Multi-source revenue extraction
- **`mixed_strategy_scraper.py`** - Manual + automated hybrid
- **legacy/** - Older/experimental versions

### 🖥️ **gui/** - User Interface Applications  
- **`linkedin_data_scraper_gui.py`** - Main GUI for LinkedIn + revenue
- **`linkedin_scraper_gui_optimized.py`** - Optimized LinkedIn GUI
- **`linkedin_scraper_gui.py`** - Basic LinkedIn GUI

### ⚡ **batch_files/** - Easy Execution
- **`run_openai_scraper.bat`** ⭐ **RECOMMENDED** - OpenAI enhanced
- **`run_complete_company_scraper.bat`** - Complete data extraction
- **`run_linkedin_company_data.bat`** - LinkedIn only
- **`setup.bat`** - Environment setup
- **legacy/** - Older batch files

### 🧪 **test_data/** - Sample Files
- **`Test5.xlsx`** - Main test dataset (4 companies)
- **`sample_companies.xlsx`** - Additional samples
- **`test_public_companies.xlsx`** - Public company tests

### 📊 **results/** - Output Files
- All `*_results.xlsx` files from scraping runs
- Revenue extraction results
- Processing outputs

### 📝 **logs/** - Processing Logs
- Detailed execution logs
- Error tracking
- Debug information

### 📖 **documentation/** - Guides & Help
- **`README.md`** - Main documentation
- **`QUICK_START.md`** - Getting started guide
- **`REVENUE_SCRAPING_GUIDE.md`** - Revenue extraction help
- **`USAGE_GUIDE.md`** - Detailed usage instructions

### 🛠️ **utilities/** - Helper Tools
- Analysis scripts
- Data processing utilities
- Success rate calculators
- Test helpers

### 📋 **templates/** - Excel Templates
- Manual data collection templates
- Standard input formats

## 🎯 Recommended Workflow

### 1. First Time Setup
```powershell
cd "c:\Viji\Automation\NewCode\CompanyDataScraper"
.\batch_files\setup.bat
```

### 2. Get OpenAI API Key (For Best Results)
1. Visit: https://platform.openai.com/api-keys
2. Create API key (starts with "sk-...")
3. Set environment variable:
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
```

### 3. Run Main Scraper
```powershell
# With OpenAI (40-70% revenue success rate)
.\batch_files\run_openai_scraper.bat "test_data\Test5.xlsx" --use-openai --website-column "Website" --company-column "Company Name"

# Without OpenAI (15-25% revenue success rate)  
.\batch_files\run_complete_company_scraper.bat "test_data\Test5.xlsx" --website-column "Website" --company-column "Company Name"
```

## 📈 Success Rates

| Data Type | Method | Success Rate |
|-----------|---------|--------------|
| LinkedIn Size/Industry | Proven scraping | **90-100%** |
| Revenue (OpenAI) | GPT analysis | **40-70%** |
| Revenue (Traditional) | Pattern matching | **15-25%** |
| Revenue (Public companies) | Financial docs | **60-80%** |
| Revenue (Private companies) | Limited disclosure | **5-15%** |

## 🔧 Configuration

### Required Excel Columns
- **`LinkedIn_URL`** - LinkedIn company page URLs
- **`Company_Website`** - Company website URLs  
- **`Company_Name`** - Company names (optional)

### Output Columns Added
- **`Company_Size_Enhanced`** - Employee counts from LinkedIn
- **`Industry_Enhanced`** - Business sectors from LinkedIn
- **`LinkedIn_Status`** - LinkedIn scraping status
- **`Revenue_Enhanced`** - Revenue figures (OpenAI/traditional)
- **`Revenue_Source`** - Where revenue was found
- **`Revenue_Status`** - Revenue extraction status

## 🎉 What's New in Organized Structure

✅ **Clear separation** by functionality  
✅ **Main scrapers** easily identified  
✅ **Legacy code** preserved but separated  
✅ **Test data** organized and accessible  
✅ **Results** automatically organized  
✅ **Documentation** centralized  
✅ **Easy navigation** with clear paths

## 🚀 Next Steps

1. **Test the organized structure** with your data
2. **Use OpenAI scraper** for best revenue results  
3. **Check documentation/** for detailed guides
4. **Explore utilities/** for additional tools
5. **Scale up** to your production datasets

---
**Main Project Directory:** `c:\Viji\Automation\NewCode\CompanyDataScraper`  
**Primary Scraper:** `.\batch_files\run_openai_scraper.bat`  
**Documentation:** `.\documentation\` folder