#!/usr/bin/env python3
"""
Web Search & Scraping Skill for OpenClaw
Provides internet search and web scraping capabilities for autonomous problem-solving
"""

import requests
import json
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import time
import random

class WebSearchScraping:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def duckduckgo_search(self, query, max_results=5):
        """Search using DuckDuckGo HTML interface"""
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results
            for result in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                url_elem = result.find('a', class_='result__url')
                
                if title_elem:
                    title = title_elem.get_text().strip()
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                    
                    if url.startswith('/'):
                        url = urljoin('https://duckduckgo.com', url)
                        
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
            
            return results
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def searxng_search(self, query, searxng_url="https://searx.info", max_results=5):
        """Search using SearxNG instance"""
        try:
            search_params = {
                'q': query,
                'format': 'json',
                'pageno': 1,
                'language': 'en'
            }
            
            response = self.session.get(f"{searxng_url}/search", params=search_params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get('results', [])[:max_results]:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('content', '')
                })
            
            return results
            
        except Exception as e:
            print(f"SearxNG search error: {e}")
            return []
    
    def scrape_page_content(self, url, extract_mode='text'):
        """Scrape and extract content from a webpage"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Handle encoding
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            if extract_mode == 'text':
                # Get text content
                text = soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                return text[:5000]  # Limit to 5000 characters
                
            elif extract_mode == 'markdown':
                # Simple markdown conversion
                import markdownify
                return markdownify.markdownify(str(soup), heading_style="ATX")[:5000]
                
            else:
                return str(soup)[:5000]
                
        except Exception as e:
            print(f"Page scraping error: {e}")
            return f"Error scraping {url}: {str(e)}"
    
    def search_and_scrape(self, query, source='duckduckgo', max_results=3, extract_mode='text'):
        """Perform search and scrape top results"""
        if source == 'duckduckgo':
            results = self.duckduckgo_search(query, max_results)
        elif source == 'searxng':
            results = self.searxng_search(query, max_results=max_results)
        else:
            results = self.duckduckgo_search(query, max_results)
        
        scraped_results = []
        for result in results:
            content = self.scrape_page_content(result['url'], extract_mode)
            scraped_results.append({
                'title': result['title'],
                'url': result['url'],
                'snippet': result['snippet'],
                'content': content
            })
            # Add delay to be respectful
            time.sleep(random.uniform(0.5, 1.5))
        
        return scraped_results

# CLI interface
def main():
    import argparse
    parser = argparse.ArgumentParser(description='Web Search & Scraping Tool')
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--source', choices=['duckduckgo', 'searxng'], default='duckduckgo')
    parser.add_argument('--max-results', type=int, default=3)
    parser.add_argument('--extract-mode', choices=['text', 'markdown'], default='text')
    
    args = parser.parse_args()
    
    searcher = WebSearchScraping()
    results = searcher.search_and_scrape(
        args.query, 
        source=args.source, 
        max_results=args.max_results,
        extract_mode=args.extract_mode
    )
    
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()