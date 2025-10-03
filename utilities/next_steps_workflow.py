#!/usr/bin/env python3
"""
Production-Ready Revenue Scraping Workflow
Your complete next steps implementation
"""

import pandas as pd
import logging
from mixed_strategy_scraper import MixedStrategyRevenueScraper

def setup_production_workflow():
    """Set up your production revenue scraping workflow"""
    
    print("🚀 SETTING UP YOUR PRODUCTION REVENUE SCRAPING WORKFLOW")
    print("=" * 65)
    
    steps = [
        {
            'step': '1. IMMEDIATE ACTIONS (Today)',
            'tasks': [
                '✅ Use mixed_strategy_scraper.py as your primary tool',
                '📝 Manually collect 5-10 high-priority company revenues from ZoomInfo',
                '⚙️ Add manual data to mixed_strategy_scraper.py',
                '🧪 Test on your real company data'
            ]
        },
        {
            'step': '2. SCALE UP (This Week)', 
            'tasks': [
                '📊 Process your main company database',
                '🎯 Focus on companies where LinkedIn already worked',
                '📈 Build up manual ZoomInfo database gradually',
                '🔄 Run periodic batches with mixed strategy'
            ]
        },
        {
            'step': '3. OPTIMIZE (Next 2 Weeks)',
            'tasks': [
                '📋 Create company priority tiers (high/medium/low revenue importance)',
                '🏆 Manually collect revenue for Tier 1 companies first',
                '🤖 Use automated scraping for Tier 2/3 companies',
                '📊 Track success rates and ROI'
            ]
        }
    ]
    
    for step_info in steps:
        print(f"\n{step_info['step']}:")
        for task in step_info['tasks']:
            print(f"  {task}")
    
    print(f"\n{'='*65}")

def create_manual_zoominfo_template():
    """Create a template for manually collecting ZoomInfo data"""
    
    template_data = [
        {
            'Company_Name': 'AIMA - The Alternative Investment Management Association',
            'Website_URL': 'https://aima.org',
            'ZoomInfo_URL': 'https://www.zoominfo.com/c/all-india-management-association/350854624',
            'Revenue': '$55.2 Million',
            'Revenue_Year': '2024',
            'Notes': 'Found on ZoomInfo company profile page',
            'Date_Collected': '2025-10-02',
            'Priority': 'High'
        },
        {
            'Company_Name': '[Add your next company here]',
            'Website_URL': '[Company website]', 
            'ZoomInfo_URL': '[Search Google: "Company Name" site:zoominfo.com]',
            'Revenue': '[Extract from ZoomInfo page]',
            'Revenue_Year': '[Year of revenue data]',
            'Notes': '[Any additional details]',
            'Date_Collected': '[Today\'s date]',
            'Priority': '[High/Medium/Low]'
        }
    ]
    
    df = pd.DataFrame(template_data)
    template_file = 'manual_zoominfo_collection_template.xlsx'
    df.to_excel(template_file, index=False)
    
    print(f"\n📋 MANUAL ZOOMINFO COLLECTION TEMPLATE CREATED")
    print(f"File: {template_file}")
    print("\nHow to use:")
    print("1. Open the Excel file")
    print("2. For each company, search Google: 'Company Name site:zoominfo.com'")
    print("3. Visit the ZoomInfo page and extract revenue manually")
    print("4. Fill in the template")
    print("5. Use update_manual_data_from_excel() to add to scraper")
    
    return template_file

def update_manual_data_from_excel(excel_file='manual_zoominfo_collection_template.xlsx'):
    """Convert Excel template to Python dictionary format for the scraper"""
    
    try:
        df = pd.read_excel(excel_file)
        
        print(f"\n🔄 CONVERTING MANUAL DATA TO SCRAPER FORMAT")
        print(f"Reading from: {excel_file}")
        
        # Generate Python dictionary code
        manual_data_code = "# Add this to mixed_strategy_scraper.py in the manual_revenue_data dictionary:\n\n"
        manual_data_code += "manual_revenue_data = {\n"
        
        for _, row in df.iterrows():
            if pd.notna(row['Revenue']) and row['Revenue'] != '[Extract from ZoomInfo page]':
                company_name = row['Company_Name']
                revenue = row['Revenue'] 
                manual_data_code += f'    "{company_name}": "{revenue}",\n'
                
                # Also add by website domain
                if pd.notna(row['Website_URL']) and row['Website_URL'] != '[Company website]':
                    domain = row['Website_URL'].replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
                    manual_data_code += f'    "{domain}": "{revenue}",\n'
        
        manual_data_code += "}\n"
        
        # Save to file
        code_file = 'manual_data_update.py'
        with open(code_file, 'w') as f:
            f.write(manual_data_code)
            
        print(f"✅ Manual data code generated: {code_file}")
        print(f"📝 Copy the contents to your mixed_strategy_scraper.py file")
        print("\nGenerated code preview:")
        print(manual_data_code[:500] + "..." if len(manual_data_code) > 500 else manual_data_code)
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        print("Make sure you've filled in the manual collection template first")

def run_production_batch(input_file, output_suffix='_production_results'):
    """Run production batch processing"""
    
    print(f"\n🏭 RUNNING PRODUCTION BATCH PROCESSING")
    print(f"Input: {input_file}")
    
    try:
        # Import and run mixed strategy scraper
        from mixed_strategy_scraper import process_excel_with_mixed_strategy
        
        output_file = input_file.replace('.xlsx', f'{output_suffix}.xlsx')
        
        print(f"Processing with Mixed Strategy...")
        result_df = process_excel_with_mixed_strategy(
            input_file=input_file,
            output_file=output_file
        )
        
        print(f"✅ Production batch complete!")
        print(f"📊 Results saved to: {output_file}")
        
        return result_df
        
    except Exception as e:
        print(f"❌ Production batch failed: {str(e)}")
        return None

def main():
    """Main workflow orchestrator"""
    
    setup_production_workflow()
    
    print(f"\n{'='*65}")
    print("🎯 YOUR IMMEDIATE ACTION PLAN")
    print(f"{'='*65}")
    
    actions = [
        "1. Run: python next_steps_workflow.py --create-template",
        "2. Manually collect 5-10 company revenues using the template",
        "3. Run: python next_steps_workflow.py --update-manual-data", 
        "4. Run: python next_steps_workflow.py --production-batch your_file.xlsx",
        "5. Review results and scale up"
    ]
    
    for action in actions:
        print(f"  {action}")
    
    print(f"\n📞 SUPPORT: If you need help with any step, just ask!")
    print(f"{'='*65}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Production Revenue Scraping Workflow')
    parser.add_argument('--create-template', action='store_true', help='Create manual ZoomInfo collection template')
    parser.add_argument('--update-manual-data', action='store_true', help='Update manual data from Excel template')
    parser.add_argument('--production-batch', help='Run production batch on specified file')
    parser.add_argument('--setup', action='store_true', help='Show setup workflow', default=True)
    
    args = parser.parse_args()
    
    if args.create_template:
        create_manual_zoominfo_template()
    elif args.update_manual_data:
        update_manual_data_from_excel()
    elif args.production_batch:
        run_production_batch(args.production_batch)
    else:
        main()