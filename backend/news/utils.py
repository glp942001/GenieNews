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
    """Extract media URLs from RSS entry."""
    media_urls = []
    
    # Check for enclosures
    if hasattr(entry, 'enclosures'):
        for enclosure in entry.enclosures:
            if hasattr(enclosure, 'href'):
                media_urls.append({
                    'url': enclosure.href,
                    'type': getattr(enclosure, 'type', 'unknown'),
                    'length': getattr(enclosure, 'length', None),
                })
    
    # Check for media:content (RSS 2.0)
    if hasattr(entry, 'media_content'):
        for media in entry.media_content:
            if hasattr(media, 'url'):
                media_urls.append({
                    'url': media.url,
                    'type': getattr(media, 'type', 'unknown'),
                    'width': getattr(media, 'width', None),
                    'height': getattr(media, 'height', None),
                })
    
    # Check for media:thumbnail
    if hasattr(entry, 'media_thumbnail'):
        for thumb in entry.media_thumbnail:
            if hasattr(thumb, 'url'):
                media_urls.append({
                    'url': thumb.url,
                    'type': 'image',
                    'width': getattr(thumb, 'width', None),
                    'height': getattr(thumb, 'height', None),
                })
    
    return media_urls


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
