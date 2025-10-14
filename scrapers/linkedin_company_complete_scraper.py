#!/usr/bin/env python3
"""
Enhanced LinkedIn Company Scraper with Revenue Extraction
- Company Size & Industry: From LinkedIn (existing working logic)
- Revenue: From company websites using open source methods
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional, List, Dict
import random
from urllib.parse import urlparse, urljoin
import os
import sys
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import argparse

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        # Try main config file first
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Try production config as fallback
        production_config = 'config.production.json'
        if os.path.exists(production_config):
            logger.info(f"Using production config: {production_config}")
            with open(production_config, 'r') as f:
                return json.load(f)
        
        logger.warning(f"Config files not found: {config_file}, {production_config}. Using defaults.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file {config_file}, using defaults")
        return {}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_complete_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CompleteCompanyScraper:
    def __init__(self, config=None):
        """Enhanced scraper for LinkedIn data + website revenue"""
        self.config = config or load_config()
        scraper_settings = self.config.get('scraper_settings', {})
        
        self.delay_range = tuple(scraper_settings.get('delay_range', [10, 20]))
        self.timeout = scraper_settings.get('timeout', 30)
        self.max_retries = scraper_settings.get('max_retries', 3)
        
        # User agents rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
        ]
        
        # Revenue patterns for website extraction
        self.revenue_patterns = [
            # Standard revenue patterns
            r'(?:total\s+)?(?:net\s+)?(?:annual\s+)?revenue[:\s]*(?:of\s*)?\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(?:net\s+)?(?:total\s+)?sales[:\s]*(?:of\s*)?\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(?:fiscal\s+year|fy)\s*(\d{4})[:\s]*(?:revenue|sales)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'total\s+revenues?[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'generated\s+(?:approximately\s+)?\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:in\s+)?(?:revenue|sales)',
            r'reported\s+(?:revenue|sales)\s+of\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)\s+(?:in\s+)?(?:annual\s+)?(?:revenue|sales|turnover)',
        ]
        
    def _create_fresh_session(self):
        """Create a fresh session for each request to avoid detection"""
        session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Rotate user agent for each request
        user_agent = random.choice(self.user_agents)
        
        referrers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://duckduckgo.com/',
            'https://linkedin.com/',
            ''  # Sometimes no referrer
        ]
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': random.choice(referrers)
        }
        
        session.headers.update(headers)
        return session

    # =================== LINKEDIN SCRAPING (EXISTING WORKING LOGIC) ===================
    
    def extract_linkedin_data(self, linkedin_url: str) -> Dict[str, str]:
        """Extract company size and industry from LinkedIn (existing working logic)"""
        result = {
            'company_size': 'Not Found',
            'industry': 'Not Found',
            'linkedin_status': 'Failed'
        }
        
        if not linkedin_url or not self._is_valid_linkedin_url(linkedin_url):
            logger.warning(f"Invalid LinkedIn URL: {linkedin_url}")
            result['linkedin_status'] = 'Invalid URL'
            return result
        
        try:
            # Random delay before request
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            session = self._create_fresh_session()
            response = session.get(linkedin_url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for {linkedin_url}")
                result['linkedin_status'] = f'HTTP {response.status_code}'
                return result
            
            # Check if redirected to login
            if 'linkedin.com/login' in response.url or 'authwall' in response.url:
                logger.warning(f"Redirected to login page: {linkedin_url}")
                result['linkedin_status'] = 'Login Required'
                return result
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract company size (existing working logic)
            company_size = self._extract_size_multiple_strategies(soup)
            if company_size:
                result['company_size'] = company_size
            
            # Extract industry (existing working logic)
            industry = self._extract_industry_multiple_strategies(soup)
            if industry:
                result['industry'] = industry
            
            if company_size or industry:
                result['linkedin_status'] = 'Success'
            else:
                result['linkedin_status'] = 'No Data Found'
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {linkedin_url}")
            result['linkedin_status'] = 'Timeout'
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {linkedin_url}")
            result['linkedin_status'] = 'Connection Error'
        except Exception as e:
            logger.error(f"Unexpected error for {linkedin_url}: {str(e)}")
            result['linkedin_status'] = 'Error'
        
        return result
    
    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn company URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc.lower() in ['linkedin.com', 'www.linkedin.com'] and
                '/company/' in parsed.path.lower()
            )
        except:
            return False
    
    def _extract_size_multiple_strategies(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company size using proven working logic from GUI"""
        text_content = soup.get_text()
        
        # LinkedIn's EXACT range patterns (proven working from GUI)
        linkedin_ranges = [
            r'(1-10)\s+employees?',
            r'(11-50)\s+employees?', 
            r'(51-200)\s+employees?',
            r'(201-500)\s+employees?',
            r'(501-1,000)\s+employees?',
            r'(501-1000)\s+employees?',
            r'(1,001-5,000)\s+employees?',
            r'(1001-5000)\s+employees?',
            r'(5,001-10,000)\s+employees?',
            r'(5001-10000)\s+employees?',
            r'(10,001\+)\s+employees?',
            r'(10000\+)\s+employees?'
        ]
        
        # Try LinkedIn's standard ranges first
        for pattern in linkedin_ranges:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                size = matches[0].strip()
                logger.info(f"✅ Company size found: {size} employees")
                return f"{size} employees"
        
        # Fallback: look for Company size section specifically
        company_size_patterns = [
            r'Company size[:\s]*(1-10|11-50|51-200|201-500|501-1,?000|1,?001-5,?000|5,?001-10,?000|10,?000\+)\s+employees?',
            r'Company size[:\s]*(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?'
        ]
        
        for pattern in company_size_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                size = matches[0].strip()
                logger.info(f"✅ Company size found (pattern): {size} employees")
                return f"{size} employees"
        
        # Last resort: any range pattern
        general_patterns = [
            r'(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?',
            r'(\d+-\d+)\s+employees?'
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                size = matches[0].strip()
                logger.info(f"✅ Company size found (general): {size} employees")
                return f"{size} employees"
        
        logger.warning("❌ Company size not found")
        return None
    
    def _extract_industry_multiple_strategies(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract industry using proven working logic from GUI"""
        text_content = soup.get_text()
        
        # LinkedIn's industry patterns (proven working from GUI)
        industry_patterns = [
            r'Industry[:\s]*([^\n\r]+)',
            r'Industries[:\s]*([^\n\r]+)',
            r'Business Type[:\s]*([^\n\r]+)',
            r'Sector[:\s]*([^\n\r]+)',
            r'Category[:\s]*([^\n\r]+)'
        ]
        
        for pattern in industry_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                industry = matches[0].strip()
                # Clean up common artifacts
                industry = re.sub(r'^[:\s]*', '', industry)  # Remove leading colons/spaces
                industry = re.sub(r'\s+', ' ', industry)      # Normalize whitespace
                industry = industry.strip()
                
                if industry and len(industry) > 2:  # Valid industry found
                    logger.info(f"✅ Industry found: {industry}")
                    return industry
        
        # Try more specific LinkedIn selectors from GUI
        specific_selectors = [
            '.pv-entity__secondary-title',
            '.company-industries',
            '.org-top-card-summary__industry',
            '[data-test-id="about-us-industry"]'
        ]
        
        for selector in specific_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text and len(text) > 2:
                        logger.info(f"✅ Industry found (selector): {text}")
                        return text
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Fallback: Look for common industry keywords in context
        industry_context_patterns = [
            r'(?:works?\s+in|operates?\s+in|specializes?\s+in|focuses?\s+on)\s+([^.]+)',
            r'(?:leader\s+in|expert\s+in|provider\s+of)\s+([^.]+)'
        ]
        
        for pattern in industry_context_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                industry = matches[0].strip()
                if industry and len(industry) > 5:  # Longer context needed
                    logger.info(f"✅ Industry found (context): {industry}")
                    return industry
        
        logger.warning("❌ Industry not found")
        return None
    
    def _strategy_meta_tags(self, soup: BeautifulSoup, data_type: str) -> Optional[str]:
        """Extract from meta tags"""
        if data_type == 'size':
            # Look for company size in meta tags
            meta_tags = soup.find_all('meta', {'name': re.compile(r'description|keywords', re.I)})
            for tag in meta_tags:
                content = tag.get('content', '')
                if content:
                    size_match = re.search(r'(\d+[,-]\d+|\d+\+?)\s*employees?', content, re.I)
                    if size_match:
                        return size_match.group(1) + " employees"
        
        elif data_type == 'industry':
            # Look for industry in meta tags
            meta_tags = soup.find_all('meta', {'name': re.compile(r'description|keywords', re.I)})
            for tag in meta_tags:
                content = tag.get('content', '')
                if content and any(word in content.lower() for word in ['industry', 'sector', 'business']):
                    # Extract potential industry terms
                    words = content.split()
                    for i, word in enumerate(words):
                        if word.lower() in ['industry', 'sector']:
                            if i > 0:
                                return words[i-1].strip(',.')
        
        return None
    
    def _strategy_json_ld(self, soup: BeautifulSoup, data_type: str) -> Optional[str]:
        """Extract from JSON-LD structured data"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data_type == 'size' and 'numberOfEmployees' in data:
                        return str(data['numberOfEmployees']) + " employees"
                    elif data_type == 'industry' and 'industry' in data:
                        return data['industry']
            except:
                continue
        return None
    
    def _strategy_text_patterns(self, soup: BeautifulSoup, data_type: str) -> Optional[str]:
        """Extract using text patterns"""
        text = soup.get_text()
        
        if data_type == 'size':
            # Company size patterns
            size_patterns = [
                r'(\d+[,-]\d+)\s*employees?',
                r'(\d+\+?)\s*employees?',
                r'company\s+size[:\s]*(\d+[,-]\d+|\d+\+?)',
                r'(\d+[,-]\d+|\d+\+?)\s*people',
            ]
            
            for pattern in size_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    return match.group(1) + " employees"
        
        elif data_type == 'industry':
            # Industry patterns
            industry_patterns = [
                r'industry[:\s]*([^,\n]+)',
                r'sector[:\s]*([^,\n]+)',
                r'operates\s+in\s+([^,\n]+)',
            ]
            
            for pattern in industry_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    industry = match.group(1).strip()
                    if len(industry) < 50:  # Reasonable length
                        return industry
        
        return None
    
    def _strategy_css_selectors(self, soup: BeautifulSoup, data_type: str) -> Optional[str]:
        """Extract using CSS selectors"""
        if data_type == 'size':
            # Try common LinkedIn selectors for company size
            selectors = [
                '.org-top-card-summary-info-list__info-item',
                '.company-info-item',
                '[data-test="company-size"]',
                '.org-about-company-module__company-size',
            ]
        else:
            # Try common LinkedIn selectors for industry
            selectors = [
                '.org-top-card-summary-info-list__info-item',
                '.company-info-item',
                '[data-test="industry"]',
                '.org-about-company-module__industry',
            ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if data_type == 'size' and ('employee' in text.lower() or 'people' in text.lower()):
                    return text
                elif data_type == 'industry' and text and len(text) < 50:
                    return text
        
        return None
    
    def _strategy_about_section(self, soup: BeautifulSoup, data_type: str) -> Optional[str]:
        """Extract from about section"""
        about_sections = soup.find_all(['div', 'section'], class_=re.compile(r'about|summary|overview', re.I))
        
        for section in about_sections:
            text = section.get_text()
            if data_type == 'size':
                match = re.search(r'(\d+[,-]\d+|\d+\+?)\s*employees?', text, re.I)
                if match:
                    return match.group(1) + " employees"
            elif data_type == 'industry':
                match = re.search(r'industry[:\s]*([^,\n]+)', text, re.I)
                if match:
                    industry = match.group(1).strip()
                    if len(industry) < 50:
                        return industry
        
        return None

    # =================== REVENUE EXTRACTION FROM WEBSITES ===================
    
    def extract_revenue_from_website(self, company_website: str, company_name: str = "") -> Dict[str, str]:
        """Extract revenue from company website using open source methods"""
        result = {
            'revenue': 'Not Found',
            'revenue_source': 'None',
            'revenue_status': 'Failed'
        }
        
        if not company_website:
            result['revenue_status'] = 'No Website'
            return result
        
        try:
            # Add protocol if missing
            if not company_website.startswith(('http://', 'https://')):
                company_website = 'https://' + company_website
            
            logger.info(f"Extracting revenue from: {company_website}")
            
            # Random delay
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            session = self._create_fresh_session()
            response = session.get(company_website, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for {company_website}")
                result['revenue_status'] = f'HTTP {response.status_code}'
                return result
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple revenue extraction strategies
            revenue_data = self._extract_revenue_multiple_strategies(soup, company_website, company_name)
            
            if revenue_data:
                result.update(revenue_data)
                result['revenue_status'] = 'Success'
                logger.info(f"Revenue found: {revenue_data['revenue']} from {revenue_data['revenue_source']}")
            else:
                result['revenue_status'] = 'No Revenue Data'
                
        except requests.exceptions.Timeout:
            logger.error(f"Revenue extraction timeout: {company_website}")
            result['revenue_status'] = 'Timeout'
        except requests.exceptions.ConnectionError:
            logger.error(f"Revenue extraction connection error: {company_website}")
            result['revenue_status'] = 'Connection Error'
        except Exception as e:
            logger.error(f"Revenue extraction error for {company_website}: {str(e)}")
            result['revenue_status'] = 'Error'
        
        return result
    
    def _extract_revenue_multiple_strategies(self, soup: BeautifulSoup, website_url: str, company_name: str) -> Optional[Dict[str, str]]:
        """Try multiple strategies to extract revenue"""
        strategies = [
            ('Main Page', self._find_revenue_in_main_page),
            ('About Page', self._find_revenue_in_about_page),
            ('Investor Relations', self._find_revenue_in_investor_page),
            ('Financial Info', self._find_revenue_in_financial_page),
            ('Press Releases', self._find_revenue_in_press_page),
        ]
        
        for source_name, strategy in strategies:
            try:
                revenue_info = strategy(soup, website_url, company_name)
                if revenue_info:
                    return {
                        'revenue': revenue_info,
                        'revenue_source': source_name
                    }
            except Exception as e:
                logger.debug(f"Revenue strategy failed ({source_name}): {e}")
                continue
        
        return None
    
    def _find_revenue_in_main_page(self, soup: BeautifulSoup, website_url: str, company_name: str) -> Optional[str]:
        """Look for revenue in main page content"""
        # Get all text from main page
        text = soup.get_text()
        return self._find_revenue_in_text(text)
    
    def _find_revenue_in_about_page(self, soup: BeautifulSoup, website_url: str, company_name: str) -> Optional[str]:
        """Look for revenue in about page"""
        about_links = soup.find_all('a', href=re.compile(r'about|company|overview', re.I))
        
        for link in about_links[:2]:  # Try first 2 about links
            try:
                href = link.get('href')
                if href:
                    about_url = urljoin(website_url, href)
                    session = self._create_fresh_session()
                    response = session.get(about_url, timeout=15)
                    if response.status_code == 200:
                        about_soup = BeautifulSoup(response.content, 'html.parser')
                        revenue = self._find_revenue_in_text(about_soup.get_text())
                        if revenue:
                            return revenue
            except:
                continue
        
        return None
    
    def _find_revenue_in_investor_page(self, soup: BeautifulSoup, website_url: str, company_name: str) -> Optional[str]:
        """Look for revenue in investor relations pages"""
        investor_links = soup.find_all('a', href=re.compile(r'investor|financial|annual|report', re.I))
        
        for link in investor_links[:2]:  # Try first 2 investor links
            try:
                href = link.get('href')
                if href:
                    investor_url = urljoin(website_url, href)
                    session = self._create_fresh_session()
                    response = session.get(investor_url, timeout=15)
                    if response.status_code == 200:
                        investor_soup = BeautifulSoup(response.content, 'html.parser')
                        revenue = self._find_revenue_in_text(investor_soup.get_text())
                        if revenue:
                            return revenue
            except:
                continue
        
        return None
    
    def _find_revenue_in_financial_page(self, soup: BeautifulSoup, website_url: str, company_name: str) -> Optional[str]:
        """Look for revenue in financial information pages"""
        financial_links = soup.find_all('a', href=re.compile(r'finance|earning|result|performance', re.I))
        
        for link in financial_links[:2]:  # Try first 2 financial links
            try:
                href = link.get('href')
                if href:
                    financial_url = urljoin(website_url, href)
                    session = self._create_fresh_session()
                    response = session.get(financial_url, timeout=15)
                    if response.status_code == 200:
                        financial_soup = BeautifulSoup(response.content, 'html.parser')
                        revenue = self._find_revenue_in_text(financial_soup.get_text())
                        if revenue:
                            return revenue
            except:
                continue
        
        return None
    
    def _find_revenue_in_press_page(self, soup: BeautifulSoup, website_url: str, company_name: str) -> Optional[str]:
        """Look for revenue in press releases"""
        press_links = soup.find_all('a', href=re.compile(r'press|news|media', re.I))
        
        for link in press_links[:2]:  # Try first 2 press links
            try:
                href = link.get('href')
                if href:
                    press_url = urljoin(website_url, href)
                    session = self._create_fresh_session()
                    response = session.get(press_url, timeout=15)
                    if response.status_code == 200:
                        press_soup = BeautifulSoup(response.content, 'html.parser')
                        revenue = self._find_revenue_in_text(press_soup.get_text())
                        if revenue:
                            return revenue
            except:
                continue
        
        return None
    
    def _find_revenue_in_text(self, text: str) -> Optional[str]:
        """Find revenue patterns in text"""
        if not text:
            return None
        
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text)
        text_lower = text.lower()
        
        # Look for revenue patterns
        for pattern in self.revenue_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                revenue_text = match.group(0).strip()
                
                # Skip very small amounts that might be costs
                if any(word in revenue_text.lower() for word in ['thousand', 'k ']):
                    nums = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', revenue_text)
                    if nums and float(nums[0].replace(',', '')) < 500:  # Less than 500K
                        continue
                
                # Clean and format the match
                revenue_text = re.sub(r'\s+', ' ', revenue_text).strip()
                return revenue_text
        
        return None

    # =================== MAIN PROCESSING FUNCTION ===================
    
    def process_companies(self, df: pd.DataFrame, linkedin_column: str = 'LinkedIn_URL', 
                         website_column: str = 'Company_Website', company_name_column: str = 'Company_Name') -> pd.DataFrame:
        """Process companies to extract LinkedIn data and website revenue"""
        
        # Initialize new columns
        df['Company_Size_Enhanced'] = 'Not Processed'
        df['Industry_Enhanced'] = 'Not Processed'
        df['LinkedIn_Status'] = 'Not Processed'
        df['Revenue_Enhanced'] = 'Not Processed'
        df['Revenue_Source'] = 'Not Processed'
        df['Revenue_Status'] = 'Not Processed'
        
        total_companies = len(df)
        logger.info(f"Starting processing of {total_companies} companies")
        
        for index, row in df.iterrows():
            logger.info(f"Processing company {index + 1}/{total_companies}: {row.get(company_name_column, 'Unknown')}")
            
            # Extract LinkedIn data (company size and industry)
            linkedin_url = row.get(linkedin_column, '')
            if linkedin_url:
                linkedin_data = self.extract_linkedin_data(linkedin_url)
                # Enhanced columns (detailed output)
                df.at[index, 'Company_Size_Enhanced'] = linkedin_data['company_size']
                df.at[index, 'Industry_Enhanced'] = linkedin_data['industry']
                df.at[index, 'LinkedIn_Status'] = linkedin_data['linkedin_status']
                
                # Also populate original columns if they exist (for display compatibility)
                if 'Size' in df.columns:
                    df.at[index, 'Size'] = linkedin_data['company_size']
                if 'Company_Size' in df.columns:
                    df.at[index, 'Company_Size'] = linkedin_data['company_size']
                if 'Industry' in df.columns:
                    df.at[index, 'Industry'] = linkedin_data['industry']
            else:
                df.at[index, 'LinkedIn_Status'] = 'No LinkedIn URL'
            
            # Extract revenue from website
            website_url = row.get(website_column, '')
            company_name = row.get(company_name_column, '')
            if website_url:
                revenue_data = self.extract_revenue_from_website(website_url, company_name)
                # Enhanced columns (detailed output)
                df.at[index, 'Revenue_Enhanced'] = revenue_data['revenue']
                df.at[index, 'Revenue_Source'] = revenue_data['revenue_source']
                df.at[index, 'Revenue_Status'] = revenue_data['revenue_status']
                
                # Also populate original column if it exists (for display compatibility)
                if 'Revenue' in df.columns:
                    df.at[index, 'Revenue'] = revenue_data['revenue']
            else:
                df.at[index, 'Revenue_Status'] = 'No Website URL'
            
            # Progress update
            if (index + 1) % 5 == 0:
                logger.info(f"Processed {index + 1}/{total_companies} companies")
        
        logger.info("Processing completed")
        return df

def main():
    parser = argparse.ArgumentParser(description='Enhanced LinkedIn and Website Revenue Scraper')
    parser.add_argument('input_file', help='Input Excel file with company data')
    parser.add_argument('--linkedin-column', default='LinkedIn_URL', help='Column name for LinkedIn URLs')
    parser.add_argument('--website-column', default='Company_Website', help='Column name for company websites')
    parser.add_argument('--company-column', default='Company_Name', help='Column name for company names')
    parser.add_argument('--output-file', help='Output Excel file (optional)')
    parser.add_argument('--wait-min', type=int, default=10, help='Minimum wait time between requests')
    parser.add_argument('--wait-max', type=int, default=20, help='Maximum wait time between requests')
    
    args = parser.parse_args()
    
    # Load input file
    try:
        df = pd.read_excel(args.input_file)
        logger.info(f"Loaded {len(df)} companies from {args.input_file}")
    except Exception as e:
        logger.error(f"Error loading input file: {e}")
        sys.exit(1)
    
    # Create scraper with custom delay settings
    config = {
        'scraper_settings': {
            'delay_range': [args.wait_min, args.wait_max],
            'timeout': 30,
            'max_retries': 3
        }
    }
    
    scraper = CompleteCompanyScraper(config)
    
    # Process companies
    try:
        df_result = scraper.process_companies(
            df, 
            linkedin_column=args.linkedin_column,
            website_column=args.website_column,
            company_name_column=args.company_column
        )
        
        # Save results
        output_file = args.output_file or args.input_file.replace('.xlsx', '_complete_results.xlsx')
        df_result.to_excel(output_file, index=False)
        logger.info(f"Results saved to {output_file}")
        
        # Print summary
        linkedin_success = len(df_result[df_result['LinkedIn_Status'] == 'Success'])
        revenue_success = len(df_result[df_result['Revenue_Status'] == 'Success'])
        
        print(f"\n========== PROCESSING SUMMARY ==========")
        print(f"Total companies processed: {len(df_result)}")
        print(f"LinkedIn data extracted: {linkedin_success} ({linkedin_success/len(df_result)*100:.1f}%)")
        print(f"Revenue data extracted: {revenue_success} ({revenue_success/len(df_result)*100:.1f}%)")
        print(f"Results saved to: {output_file}")
        print(f"==========================================")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()