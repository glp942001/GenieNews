"""
RSS/Atom feed parsing logic with error handling and retry.
"""
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import feedparser
import requests
from dateutil import parser as date_parser

from .utils import (
    get_request_headers,
    normalize_url,
    is_valid_url,
    get_domain_from_url,
    add_rate_limit_delay,
    retry_with_exponential_backoff,
    extract_media_from_rss_entry,
    clean_text,
    is_recent_article,
)

logger = logging.getLogger(__name__)


class FeedParseError(Exception):
    """Custom exception for feed parsing errors."""
    pass


class FeedParser:
    """RSS/Atom feed parser with retry logic and error handling."""
    
    def __init__(self, timeout: int = 30, max_articles: int = 50):
        self.timeout = timeout
        self.max_articles = max_articles
    
    @retry_with_exponential_backoff(
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        exceptions=(requests.RequestException, FeedParseError)
    )
    def fetch_feed(self, feed_url: str, custom_headers: Optional[Dict] = None) -> feedparser.FeedParserDict:
        """Fetch and parse RSS/Atom feed with retry logic."""
        logger.info(f"Fetching feed: {feed_url}")
        
        # Rate limiting
        domain = get_domain_from_url(feed_url)
        add_rate_limit_delay(domain)
        
        # Prepare headers
        headers = get_request_headers(custom_headers)
        
        try:
            # Fetch feed
            response = requests.get(
                feed_url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse with feedparser
            feed = feedparser.parse(response.content)
            
            # Validate feed
            if feed.bozo:
                logger.warning(f"Feed has parsing issues: {feed.bozo_exception}")
            
            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_url}")
                return feed
            
            logger.info(f"Successfully parsed feed: {len(feed.entries)} entries")
            return feed
            
        except requests.exceptions.Timeout:
            raise FeedParseError(f"Timeout fetching feed: {feed_url}")
        except requests.exceptions.ConnectionError:
            raise FeedParseError(f"Connection error fetching feed: {feed_url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise FeedParseError(f"Feed not found (404): {feed_url}")
            elif e.response.status_code == 403:
                raise FeedParseError(f"Feed access forbidden (403): {feed_url}")
            else:
                raise FeedParseError(f"HTTP error {e.response.status_code}: {feed_url}")
        except Exception as e:
            raise FeedParseError(f"Unexpected error fetching feed: {str(e)}")
    
    def parse_entry(self, entry, source_url: str) -> Optional[Dict]:
        """Parse a single RSS/Atom entry into standardized format."""
        try:
            # Extract basic fields
            title = clean_text(getattr(entry, 'title', ''))
            link = getattr(entry, 'link', '')
            summary = clean_text(getattr(entry, 'summary', ''))
            
            # Validate required fields
            if not title or not link:
                logger.warning(f"Skipping entry with missing title or link: {link}")
                return None
            
            # Normalize URL
            article_url = normalize_url(link, source_url)
            if not is_valid_url(article_url):
                logger.warning(f"Invalid article URL: {article_url}")
                return None
            
            # Parse published date
            published_at = self._parse_published_date(entry)
            
            # Check if article is recent enough
            if not is_recent_article(published_at, max_age_days=30):
                logger.debug(f"Skipping old article: {title}")
                return None
            
            # Extract media
            media_assets = extract_media_from_rss_entry(entry)
            
            # Extract additional metadata
            author = clean_text(getattr(entry, 'author', ''))
            tags = self._extract_tags(entry)
            
            return {
                'title': title,
                'url': article_url,
                'published_at': published_at,
                'summary_feed': summary,
                'author': author,
                'tags': tags,
                'media_assets': media_assets,
                'raw_entry': entry,  # Keep original for debugging
            }
            
        except Exception as e:
            logger.error(f"Error parsing entry: {str(e)}")
            return None
    
    def _parse_published_date(self, entry) -> datetime:
        """Parse published date from entry with fallbacks."""
        # Try different date fields
        date_fields = ['published', 'updated', 'created', 'pubDate']
        
        for field in date_fields:
            if hasattr(entry, field):
                date_str = getattr(entry, field)
                if date_str:
                    try:
                        # Parse with dateutil
                        parsed_date = date_parser.parse(date_str)
                        if parsed_date:
                            return parsed_date
                    except Exception as e:
                        logger.debug(f"Failed to parse date '{date_str}': {e}")
                        continue
        
        # Fallback to current time
        logger.warning("No valid published date found, using current time")
        return datetime.now()
    
    def _extract_tags(self, entry) -> List[str]:
        """Extract tags/categories from entry."""
        tags = []
        
        # Try different tag fields
        tag_fields = ['tags', 'categories', 'subject']
        
        for field in tag_fields:
            if hasattr(entry, field):
                field_value = getattr(entry, field)
                if field_value:
                    if isinstance(field_value, list):
                        for item in field_value:
                            if hasattr(item, 'term'):
                                tags.append(clean_text(item.term))
                            elif isinstance(item, str):
                                tags.append(clean_text(item))
                    elif isinstance(field_value, str):
                        tags.append(clean_text(field_value))
        
        # Remove duplicates and empty tags
        return list(set(filter(None, tags)))
    
    def parse_feed_entries(self, feed: feedparser.FeedParserDict, source_url: str) -> List[Dict]:
        """Parse all entries from a feed."""
        parsed_entries = []
        
        # Limit number of articles
        entries = feed.entries[:self.max_articles]
        
        for i, entry in enumerate(entries):
            try:
                parsed_entry = self.parse_entry(entry, source_url)
                if parsed_entry:
                    parsed_entries.append(parsed_entry)
                else:
                    logger.debug(f"Skipped entry {i+1}/{len(entries)}")
            except Exception as e:
                logger.error(f"Error processing entry {i+1}: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(parsed_entries)} valid entries from {len(entries)} total")
        return parsed_entries


def parse_feed(feed_url: str, custom_headers: Optional[Dict] = None, max_articles: int = 50) -> Tuple[feedparser.FeedParserDict, List[Dict]]:
    """
    Parse a feed and return both raw feed and parsed entries.
    
    Returns:
        Tuple of (raw_feed, parsed_entries)
    """
    parser = FeedParser(max_articles=max_articles)
    
    # Fetch and parse feed
    feed = parser.fetch_feed(feed_url, custom_headers)
    
    # Parse entries
    entries = parser.parse_feed_entries(feed, feed_url)
    
    return feed, entries
