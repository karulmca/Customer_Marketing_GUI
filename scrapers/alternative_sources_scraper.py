#!/usr/bin/env python3
"""
Enhanced Alternative Data Sources Revenue Scraper
Focuses on company websites, SEC filings, annual reports, and financial disclosures
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional, Dict, List
import random
from urllib.parse import urlparse, urljoin, quote_plus
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlternativeDataSourcesScraper:
    def __init__(self):
        self.timeout = 30
        self.delay_range = (3, 6)
        
        # Enhanced revenue patterns for different document types
        self.revenue_patterns = [
            # Standard revenue patterns
            r'(?:total\s+)?(?:net\s+)?(?:annual\s+)?revenue[:\s]*(?:of\s*)?\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(?:net\s+)?(?:total\s+)?sales[:\s]*(?:of\s*)?\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # Financial statement patterns
            r'(?:fiscal\s+year|fy)\s*(\d{4})[:\s]*(?:revenue|sales)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'(?:year\s+ended|for\s+the\s+year)[^$]*revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            
            # SEC filing patterns
            r'total\s+revenues?[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'consolidated\s+revenues?[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            
            # Annual report patterns
            r'(\d{4})\s+annual\s+revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'generated\s+(?:approximately\s+)?\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:in\s+)?(?:revenue|sales)',
            
            # Press release patterns
            r'reported\s+(?:revenue|sales)\s+of\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'achieved\s+(?:revenue|sales)\s+of\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            
            # Investor presentation patterns
            r'revenue\s+growth[^$]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'(?:ltm|ttm)\s+revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            
            # Alternative formats
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)\s+(?:in\s+)?(?:annual\s+)?(?:revenue|sales|turnover)',
            r'€(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:revenue|sales)',
            r'£(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:revenue|sales)',
        ]
    
    def _create_session(self):
        """Create session with realistic headers"""
        session = requests.Session()
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
        
        session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def _find_revenue_in_text(self, text: str, source_type: str = "general") -> Optional[str]:
        """Find revenue in text with context-aware patterns"""
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
                
                # Skip very small amounts that might be costs or other figures
                if any(word in revenue_text.lower() for word in ['thousand', 'k ']):
                    nums = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', revenue_text)
                    if nums and float(nums[0].replace(',', '')) < 500:  # Less than 500K
                        continue
                
                # Clean and format the match
                revenue_text = re.sub(r'\s+', ' ', revenue_text).strip()
                logger.info(f"Found revenue pattern in {source_type}: {revenue_text}")
                return revenue_text
        
        return None
    
    def _get_page_content(self, url: str, session: requests.Session) -> Optional[BeautifulSoup]:
        """Get page content with error handling"""
        try:
            time.sleep(random.uniform(*self.delay_range))
            response = session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            else:
                logger.debug(f"HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            logger.debug(f"Error accessing {url}: {str(e)}")
            return None
    
    def search_company_website_comprehensive(self, company_name: str, website_url: str) -> Dict:
        """Comprehensive search of company website for revenue data"""
        result = {
            'revenue': None,
            'source': 'Company Website',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            base_url = website_url.rstrip('/')
            
            # Comprehensive list of pages that might contain revenue information
            financial_pages = [
                '',  # Homepage
                '/about',
                '/about-us',
                '/company',
                '/corporate-information',
                
                # Investor relations
                '/investors',
                '/investor-relations',
                '/investor-information',
                '/ir',
                
                # Financial documents
                '/financials',
                '/financial-information',
                '/financial-results',
                '/annual-report',
                '/annual-reports',
                '/quarterly-results',
                '/earnings',
                
                # SEC filings
                '/sec-filings',
                '/regulatory-filings',
                '/financial-reports',
                '/10k',
                '/10-k',
                
                # Press and news
                '/press',
                '/press-releases',
                '/news',
                '/media',
                '/press-room',
                '/newsroom',
                
                # Corporate pages
                '/corporate',
                '/corporate-profile',
                '/company-profile',
                '/overview',
                '/fact-sheet',
                '/company-facts',
            ]
            
            logger.info(f"Searching {len(financial_pages)} pages on {website_url}")
            
            for page in financial_pages:
                url = base_url + page
                soup = self._get_page_content(url, session)
                
                if soup:
                    # Get text content
                    text_content = soup.get_text()
                    
                    # Look for revenue in main content
                    revenue = self._find_revenue_in_text(text_content, f"website-{page}")
                    if revenue:
                        result.update({
                            'revenue': revenue,
                            'source_url': url,
                            'status': 'Success'
                        })
                        logger.info(f"✓ Found revenue on {url}: {revenue}")
                        return result
                    
                    # Look for links to financial documents
                    financial_links = soup.find_all('a', href=True)
                    for link in financial_links:
                        href = link.get('href', '').lower()
                        link_text = link.get_text('').lower()
                        
                        # Check if this looks like a financial document
                        if any(keyword in href or keyword in link_text for keyword in 
                               ['annual-report', 'financial', '10-k', '10k', 'earnings', 'investor']):
                            
                            # Construct full URL
                            if href.startswith('http'):
                                doc_url = href
                            else:
                                doc_url = urljoin(base_url, href)
                            
                            # Try to get revenue from this document
                            doc_soup = self._get_page_content(doc_url, session)
                            if doc_soup:
                                doc_text = doc_soup.get_text()
                                revenue = self._find_revenue_in_text(doc_text, f"document-{href}")
                                if revenue:
                                    result.update({
                                        'revenue': revenue,
                                        'source_url': doc_url,
                                        'status': 'Success'
                                    })
                                    logger.info(f"✓ Found revenue in document {doc_url}: {revenue}")
                                    return result
            
            return result
        
        except Exception as e:
            logger.error(f"Error searching company website for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def search_sec_edgar(self, company_name: str) -> Dict:
        """Search SEC EDGAR database for financial filings"""
        result = {
            'revenue': None,
            'source': 'SEC EDGAR',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            
            # Search EDGAR for the company
            search_url = f"https://www.sec.gov/cgi-bin/browse-edgar"
            params = {
                'company': company_name,
                'match': 'contains',
                'filenum': '',
                'State': '',
                'Country': '',
                'SIC': '',
                'owner': 'exclude',
                'Find': 'Find Companies',
                'action': 'getcompany'
            }
            
            response = session.get(search_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for 10-K filings (annual reports)
                filing_links = soup.find_all('a', href=True)
                for link in filing_links:
                    if '10-K' in link.get_text():
                        filing_url = urljoin('https://www.sec.gov', link['href'])
                        
                        # Get the filing content
                        filing_soup = self._get_page_content(filing_url, session)
                        if filing_soup:
                            filing_text = filing_soup.get_text()
                            revenue = self._find_revenue_in_text(filing_text, "SEC-10K")
                            if revenue:
                                result.update({
                                    'revenue': revenue,
                                    'source_url': filing_url,
                                    'status': 'Success'
                                })
                                return result
                        break  # Only check first 10-K found
            
            return result
        
        except Exception as e:
            logger.error(f"Error searching SEC EDGAR for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def search_google_for_financial_docs(self, company_name: str) -> Dict:
        """Search Google for financial documents"""
        result = {
            'revenue': None,
            'source': 'Google Financial Docs',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            
            # Search queries for financial documents
            search_queries = [
                f'"{company_name}" annual report revenue filetype:pdf',
                f'"{company_name}" financial results revenue',
                f'"{company_name}" 10-K revenue site:sec.gov',
                f'"{company_name}" investor presentation revenue',
                f'"{company_name}" earnings revenue million billion',
            ]
            
            for query in search_queries:
                try:
                    encoded_query = quote_plus(query)
                    google_url = f"https://www.google.com/search?q={encoded_query}&num=5"
                    
                    time.sleep(random.uniform(*self.delay_range))
                    response = session.get(google_url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for search result links
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            
                            # Extract actual URL from Google redirect
                            if href.startswith('/url?q='):
                                try:
                                    actual_url = href.split('/url?q=')[1].split('&')[0]
                                    from urllib.parse import unquote
                                    actual_url = unquote(actual_url)
                                    
                                    # Skip if it's a PDF (would need special handling)
                                    if actual_url.endswith('.pdf'):
                                        continue
                                    
                                    # Try to get content and search for revenue
                                    doc_soup = self._get_page_content(actual_url, session)
                                    if doc_soup:
                                        doc_text = doc_soup.get_text()
                                        revenue = self._find_revenue_in_text(doc_text, f"google-doc")
                                        if revenue:
                                            result.update({
                                                'revenue': revenue,
                                                'source_url': actual_url,
                                                'status': 'Success'
                                            })
                                            logger.info(f"✓ Found revenue via Google search: {revenue}")
                                            return result
                                except Exception as e:
                                    continue
                    
                    # If we found revenue, stop searching
                    if result['revenue']:
                        break
                
                except Exception as e:
                    logger.debug(f"Google search failed for query '{query}': {str(e)}")
                    continue
            
            return result
        
        except Exception as e:
            logger.error(f"Error in Google financial docs search for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def search_crunchbase_alternative(self, company_name: str) -> Dict:
        """Alternative Crunchbase search method"""
        result = {
            'revenue': None,
            'source': 'Crunchbase',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            
            # Try direct Crunchbase URL construction
            company_slug = company_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
            crunchbase_url = f"https://www.crunchbase.com/organization/{company_slug}"
            
            soup = self._get_page_content(crunchbase_url, session)
            if soup:
                text_content = soup.get_text()
                revenue = self._find_revenue_in_text(text_content, "crunchbase-direct")
                if revenue:
                    result.update({
                        'revenue': revenue,
                        'source_url': crunchbase_url,
                        'status': 'Success'
                    })
                    return result
            
            return result
        
        except Exception as e:
            logger.error(f"Error searching Crunchbase for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def get_comprehensive_revenue(self, company_name: str, website_url: str) -> Dict:
        """Get revenue using all alternative data sources"""
        logger.info(f"Comprehensive revenue search for {company_name}")
        
        # Try different sources in order of reliability
        sources = [
            ("Company Website", lambda: self.search_company_website_comprehensive(company_name, website_url)),
            ("Google Financial Docs", lambda: self.search_google_for_financial_docs(company_name)),
            ("SEC EDGAR", lambda: self.search_sec_edgar(company_name)),
            ("Crunchbase Alternative", lambda: self.search_crunchbase_alternative(company_name)),
        ]
        
        for source_name, source_func in sources:
            try:
                logger.info(f"Trying {source_name}...")
                result = source_func()
                
                if result['revenue']:
                    logger.info(f"✓ Found revenue for {company_name} from {source_name}: {result['revenue']}")
                    return result
                else:
                    logger.info(f"✗ No revenue found in {source_name}")
            
            except Exception as e:
                logger.debug(f"{source_name} failed: {str(e)}")
                continue
        
        # No revenue found from any source
        return {
            'revenue': None,
            'source': 'Multiple Alternative Sources',
            'source_url': None,
            'status': 'No revenue found from any alternative source'
        }

def process_test5_with_alternative_sources():
    """Process Test5.xlsx with alternative data sources scraper"""
    
    df = pd.read_excel('Test5.xlsx')
    scraper = AlternativeDataSourcesScraper()
    
    # Add new columns
    df['Revenue_Alternative'] = None
    df['Alternative_Source'] = None
    df['Alternative_Source_URL'] = None
    df['Alternative_Status'] = None
    
    print("Processing Test5.xlsx with Alternative Data Sources Scraper")
    print("=" * 65)
    
    for index, row in df.iterrows():
        company_name = row['Company Name']
        website_url = row['Company Website']
        
        print(f"\n{'='*60}")
        print(f"Processing: {company_name}")
        print(f"Website: {website_url}")
        print(f"{'='*60}")
        
        # Get revenue from alternative sources
        result = scraper.get_comprehensive_revenue(company_name, website_url)
        
        # Update dataframe
        df.at[index, 'Revenue_Alternative'] = result['revenue']
        df.at[index, 'Alternative_Source'] = result['source']
        df.at[index, 'Alternative_Source_URL'] = result['source_url']
        df.at[index, 'Alternative_Status'] = result['status']
        
        print(f"\nFINAL RESULT:")
        print(f"Status: {result['status']}")
        if result['revenue']:
            print(f"Revenue: {result['revenue']}")
            print(f"Source: {result['source']}")
            print(f"URL: {result['source_url']}")
        print(f"{'='*60}")
    
    # Save results
    output_file = 'Test5_alternative_sources_revenue.xlsx'
    df.to_excel(output_file, index=False)
    
    # Print summary
    success_count = df['Revenue_Alternative'].notna().sum()
    total_count = len(df)
    
    print(f"\n{'='*65}")
    print("COMPREHENSIVE REVENUE SEARCH RESULTS")
    print(f"{'='*65}")
    print(f"Total companies processed: {total_count}")
    print(f"Revenue data found: {success_count}")
    print(f"Success rate: {(success_count/total_count)*100:.1f}%")
    print(f"Results saved to: {output_file}")
    print(f"{'='*65}")
    
    return df

if __name__ == "__main__":
    process_test5_with_alternative_sources()