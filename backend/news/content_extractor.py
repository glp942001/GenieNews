"""
Content extraction strategies for fetching full article HTML.
"""
import logging
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newspaper.article import ArticleException

from .utils import (
    get_request_headers,
    normalize_url,
    is_valid_url,
    get_domain_from_url,
    add_rate_limit_delay,
    retry_with_exponential_backoff,
    detect_paywall,
    clean_text,
)

logger = logging.getLogger(__name__)


class ContentExtractionError(Exception):
    """Custom exception for content extraction errors."""
    pass


class ContentExtractor:
    """Multi-strategy content extractor with progressive fallback."""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
    
    def extract_content(self, article_url: str, custom_headers: Optional[Dict] = None) -> Dict:
        """
        Extract article content using progressive strategies.
        
        Returns:
            Dict with 'content', 'title', 'images', 'success', 'strategy_used'
        """
        result = {
            'content': '',
            'title': '',
            'images': [],
            'success': False,
            'strategy_used': None,
            'error': None,
            'is_paywalled': False,
        }
        
        # Strategy 1: Lightweight (requests + BeautifulSoup)
        try:
            logger.debug(f"Trying Strategy 1 (requests) for: {article_url}")
            result = self._strategy_requests(article_url, custom_headers)
            if result['success'] and result['content']:
                result['strategy_used'] = 'requests'
                logger.info(f"Strategy 1 successful for: {article_url}")
                return result
        except Exception as e:
            logger.debug(f"Strategy 1 failed: {str(e)}")
        
        # Strategy 2: Medium (newspaper3k)
        try:
            logger.debug(f"Trying Strategy 2 (newspaper3k) for: {article_url}")
            result = self._strategy_newspaper3k(article_url, custom_headers)
            if result['success'] and result['content']:
                result['strategy_used'] = 'newspaper3k'
                logger.info(f"Strategy 2 successful for: {article_url}")
                return result
        except Exception as e:
            logger.debug(f"Strategy 2 failed: {str(e)}")
        
        # Strategy 3: Playwright (if enabled)
        # Note: Playwright implementation would go here
        # For now, we'll skip it and mark as failed
        
        logger.warning(f"All content extraction strategies failed for: {article_url}")
        result['error'] = 'All extraction strategies failed'
        return result
    
    @retry_with_exponential_backoff(
        max_attempts=2,
        min_wait=1.0,
        max_wait=10.0,
        exceptions=(requests.RequestException,)
    )
    def _strategy_requests(self, article_url: str, custom_headers: Optional[Dict] = None) -> Dict:
        """Strategy 1: Simple requests + BeautifulSoup extraction."""
        result = {
            'content': '',
            'title': '',
            'images': [],
            'success': False,
            'error': None,
            'is_paywalled': False,
        }
        
        # Rate limiting
        domain = get_domain_from_url(article_url)
        add_rate_limit_delay(domain)
        
        # Fetch page
        headers = get_request_headers(custom_headers)
        response = requests.get(article_url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for paywall
        if detect_paywall(response.text):
            result['is_paywalled'] = True
            result['error'] = 'Paywall detected'
            return result
        
        # Extract title
        title_selectors = ['h1', 'title', '.headline', '.article-title', '[class*="title"]']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                result['title'] = clean_text(title_elem.get_text())
                break
        
        # Extract main content
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            '[class*="article"]',
            '[class*="content"]',
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if content_elem:
            # Remove unwanted elements
            for unwanted in content_elem.select('script, style, nav, footer, .ad, .advertisement, .sidebar'):
                unwanted.decompose()
            
            result['content'] = clean_text(content_elem.get_text())
        
        # Extract images
        images = []
        for img in soup.select('img'):
            src = img.get('src')
            if src:
                img_url = normalize_url(src, article_url)
                if is_valid_url(img_url):
                    images.append({
                        'url': img_url,
                        'alt': img.get('alt', ''),
                        'width': img.get('width'),
                        'height': img.get('height'),
                    })
        
        result['images'] = images
        result['success'] = bool(result['content'])
        
        return result
    
    def _strategy_newspaper3k(self, article_url: str, custom_headers: Optional[Dict] = None) -> Dict:
        """Strategy 2: Newspaper3k extraction."""
        result = {
            'content': '',
            'title': '',
            'images': [],
            'success': False,
            'error': None,
            'is_paywalled': False,
        }
        
        try:
            # Rate limiting
            domain = get_domain_from_url(article_url)
            add_rate_limit_delay(domain)
            
            # Create article object
            article = Article(article_url)
            
            # Set custom headers if provided
            if custom_headers:
                article.set_headers(custom_headers)
            
            # Download and parse
            article.download()
            article.parse()
            
            # Check for paywall
            if detect_paywall(article.html):
                result['is_paywalled'] = True
                result['error'] = 'Paywall detected'
                return result
            
            # Extract content
            result['content'] = clean_text(article.text)
            result['title'] = clean_text(article.title)
            
            # Extract images
            images = []
            for img_url in article.images:
                if is_valid_url(img_url):
                    images.append({
                        'url': img_url,
                        'alt': '',
                        'width': None,
                        'height': None,
                    })
            
            result['images'] = images
            result['success'] = bool(result['content'])
            
        except ArticleException as e:
            result['error'] = f"Newspaper3k error: {str(e)}"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        
        return result
    
    def _strategy_playwright(self, article_url: str, custom_headers: Optional[Dict] = None) -> Dict:
        """
        Strategy 3: Playwright browser automation.
        
        Note: This is a placeholder implementation.
        In production, you would:
        1. Install playwright: pip install playwright
        2. Install browsers: playwright install
        3. Implement browser automation logic
        """
        result = {
            'content': '',
            'title': '',
            'images': [],
            'success': False,
            'error': 'Playwright not implemented',
            'is_paywalled': False,
        }
        
        logger.info("Playwright strategy not implemented - skipping")
        return result


def extract_article_content(article_url: str, custom_headers: Optional[Dict] = None) -> Dict:
    """
    Extract content from article URL using progressive strategies.
    
    Args:
        article_url: URL of the article to extract
        custom_headers: Optional custom HTTP headers
    
    Returns:
        Dict with extraction results
    """
    extractor = ContentExtractor()
    return extractor.extract_content(article_url, custom_headers)
