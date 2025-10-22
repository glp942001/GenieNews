"""
Utility functions for feed ingestion.
"""
import logging
import time
import random
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict, Any
from fake_useragent import UserAgent
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)

# Initialize user agent
try:
    ua = UserAgent()
except Exception:
    # Fallback if fake-useragent fails
    ua = None


def get_random_user_agent() -> str:
    """Get a random user agent string."""
    if ua:
        try:
            return ua.random
        except Exception:
            pass
    
    # Fallback user agents
    fallback_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'GenieNewsBot/1.0 (+https://genienews.com/bot)',
    ]
    return random.choice(fallback_agents)


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Normalize and validate URL."""
    if not url:
        return ""
    
    # Handle relative URLs
    if base_url and not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)
    
    # Basic validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return ""
        return url
    except Exception:
        return ""


def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def get_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def add_rate_limit_delay(domain: str, min_delay: float = 2.0, max_delay: float = 5.0):
    """Add random delay between requests to same domain."""
    # Simple in-memory tracking (in production, use Redis)
    if not hasattr(add_rate_limit_delay, '_last_request'):
        add_rate_limit_delay._last_request = {}
    
    now = time.time()
    last_request = add_rate_limit_delay._last_request.get(domain, 0)
    
    if last_request > 0:
        elapsed = now - last_request
        if elapsed < min_delay:
            delay = min_delay - elapsed + random.uniform(0, max_delay - min_delay)
            logger.debug(f"Rate limiting: waiting {delay:.2f}s for domain {domain}")
            time.sleep(delay)
    
    add_rate_limit_delay._last_request[domain] = time.time()


def retry_with_exponential_backoff(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retry logic with exponential backoff."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


def get_request_headers(custom_headers: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """Get standard request headers with optional custom headers."""
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    if custom_headers:
        headers.update(custom_headers)
    
    return headers


def detect_paywall(html_content: str) -> bool:
    """Detect if content is behind a paywall."""
    if not html_content:
        return False
    
    paywall_indicators = [
        'subscribe to continue',
        'paywall',
        'premium content',
        'subscription required',
        'sign in to read',
        'free articles remaining',
        'you have reached your',
        'unlock this article',
        'become a member',
        'join now to read',
    ]
    
    content_lower = html_content.lower()
    return any(indicator in content_lower for indicator in paywall_indicators)


def extract_media_from_rss_entry(entry) -> list:
    """Extract media URLs from RSS entry with enhanced extraction."""
    media_urls = []
    seen_urls = set()
    
    # Check for enclosures
    if hasattr(entry, 'enclosures'):
        for enclosure in entry.enclosures:
            if hasattr(enclosure, 'href') and enclosure.href not in seen_urls:
                media_urls.append({
                    'url': enclosure.href,
                    'type': getattr(enclosure, 'type', 'unknown'),
                    'length': getattr(enclosure, 'length', None),
                })
                seen_urls.add(enclosure.href)
    
    # Check for media:content (RSS 2.0)
    if hasattr(entry, 'media_content'):
        for media in entry.media_content:
            if hasattr(media, 'url') and media.url not in seen_urls:
                media_urls.append({
                    'url': media.url,
                    'type': getattr(media, 'type', 'unknown'),
                    'width': getattr(media, 'width', None),
                    'height': getattr(media, 'height', None),
                })
                seen_urls.add(media.url)
    
    # Check for media:thumbnail
    if hasattr(entry, 'media_thumbnail'):
        for thumb in entry.media_thumbnail:
            if hasattr(thumb, 'url') and thumb.url not in seen_urls:
                media_urls.append({
                    'url': thumb.url,
                    'type': 'image',
                    'width': getattr(thumb, 'width', None),
                    'height': getattr(thumb, 'height', None),
                })
                seen_urls.add(thumb.url)
    
    # Extract images from content/description HTML
    from bs4 import BeautifulSoup
    import re
    
    # Check summary/description for images
    summary_fields = ['summary', 'description', 'content']
    for field in summary_fields:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list):
                content = content[0].get('value', '') if content else ''
            elif hasattr(content, 'value'):
                content = content.value
            
            if content:
                # Parse HTML content
                soup = BeautifulSoup(str(content), 'html.parser')
                for img in soup.find_all('img'):
                    img_url = img.get('src') or img.get('data-src')
                    if img_url and img_url not in seen_urls and is_valid_url(img_url):
                        media_urls.append({
                            'url': img_url,
                            'type': 'image',
                            'width': img.get('width'),
                            'height': img.get('height'),
                        })
                        seen_urls.add(img_url)
    
    return media_urls


def extract_best_image_from_html(html_content: str, base_url: str = '') -> Optional[Dict]:
    """
    Extract the best/primary image from HTML content.
    Prioritizes og:image, twitter:image, then large images in content.
    """
    if not html_content:
        return None
    
    from bs4 import BeautifulSoup
    import re
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Priority 1: Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            if base_url and not img_url.startswith('http'):
                img_url = normalize_url(img_url, base_url)
            if is_valid_url(img_url):
                return {
                    'url': img_url,
                    'type': 'image',
                    'source': 'og:image'
                }
        
        # Priority 2: Twitter image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            img_url = twitter_image['content']
            if base_url and not img_url.startswith('http'):
                img_url = normalize_url(img_url, base_url)
            if is_valid_url(img_url):
                return {
                    'url': img_url,
                    'type': 'image',
                    'source': 'twitter:image'
                }
        
        # Priority 3: First large image in article content
        # Look for images in article/main content areas
        content_areas = soup.find_all(['article', 'main', 'div'], class_=re.compile(r'(article|content|post|entry)', re.I))
        if not content_areas:
            content_areas = [soup]
        
        for area in content_areas:
            for img in area.find_all('img'):
                img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if not img_url:
                    continue
                
                # Skip small images (likely ads/icons)
                width = img.get('width')
                height = img.get('height')
                if width and height:
                    try:
                        if int(width) < 200 or int(height) < 200:
                            continue
                    except (ValueError, TypeError):
                        pass
                
                # Normalize URL
                if base_url and not img_url.startswith('http'):
                    img_url = normalize_url(img_url, base_url)
                
                if is_valid_url(img_url):
                    # Skip common ad/tracking images
                    if any(x in img_url.lower() for x in ['ad', 'tracking', 'pixel', 'logo', 'icon', 'avatar']):
                        continue
                    
                    return {
                        'url': img_url,
                        'type': 'image',
                        'width': width,
                        'height': height,
                        'source': 'content'
                    }
        
    except Exception as e:
        logger.error(f"Error extracting image from HTML: {str(e)}")
    
    return None


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common HTML entities
    replacements = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' ',
    }
    
    for entity, replacement in replacements.items():
        text = text.replace(entity, replacement)
    
    return text.strip()


def is_recent_article(published_date, max_age_days: int = 30) -> bool:
    """Check if article is recent enough to process."""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    if not published_date:
        return True  # Include articles without dates
    
    if isinstance(published_date, str):
        from dateutil import parser
        try:
            published_date = parser.parse(published_date)
        except Exception:
            return True  # Include if we can't parse
    
    # Make sure both dates are timezone-aware
    if published_date.tzinfo is None:
        published_date = timezone.make_aware(published_date)
    
    cutoff_date = timezone.now() - timedelta(days=max_age_days)
    return published_date >= cutoff_date
