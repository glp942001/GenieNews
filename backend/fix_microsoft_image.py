#!/usr/bin/env python
"""Fix the Microsoft article image that failed due to long URL."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genienews_backend.settings')
django.setup()

from news.models import ArticleCurated, MediaAsset
from news.feed_parser import FeedParser
from news.utils import extract_media_from_rss_entry
import hashlib

def main():
    # Find the Microsoft article without image
    article = ArticleCurated.objects.filter(
        raw_article__title__icontains="Microsoft"
    ).filter(cover_media__isnull=True).first()
    
    if not article:
        print("Microsoft article already has an image or not found")
        return
    
    print(f"Found article: {article.raw_article.title}")
    print(f"URL: {article.raw_article.url}")
    
    # Re-fetch from RSS
    source = article.raw_article.source
    print(f"\nFetching from RSS: {source.feed_url}")
    
    parser = FeedParser()
    feed = parser.fetch_feed(source.feed_url)
    
    for entry in feed.entries[:30]:
        entry_url = getattr(entry, 'link', '')
        if entry_url == article.raw_article.url:
            print("✅ Found matching entry")
            
            media_list = extract_media_from_rss_entry(entry)
            print(f"Found {len(media_list)} media items")
            
            if media_list:
                first_media = media_list[0]
                original_url = first_media['url']
                
                # Truncate URL if too long (>200 chars)
                if len(original_url) > 200:
                    # Create a hash-based shortened version
                    url_hash = hashlib.md5(original_url.encode()).hexdigest()[:10]
                    # Use the base URL + hash
                    base_url = original_url[:180]
                    truncated_url = f"{base_url}...{url_hash}"
                    print(f"⚠️  URL too long ({len(original_url)} chars), using full URL anyway...")
                else:
                    truncated_url = original_url
                
                # Try with original URL
                try:
                    media_asset, created = MediaAsset.objects.get_or_create(
                        source_url=original_url,
                        defaults={
                            'type': 'image',
                            'width': first_media.get('width'),
                            'height': first_media.get('height'),
                            'mime_type': 'image/jpeg'
                        }
                    )
                    
                    article.raw_article.media_assets.add(media_asset)
                    article.cover_media = media_asset
                    article.save()
                    
                    print(f"✅ Successfully added image!")
                    print(f"URL: {original_url[:100]}...")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    # Fallback: use a placeholder or extract from HTML
                    print("Trying to extract from HTML...")
                    
                    if article.raw_article.raw_html:
                        from news.utils import extract_best_image_from_html
                        best_image = extract_best_image_from_html(
                            article.raw_article.raw_html,
                            article.raw_article.url
                        )
                        
                        if best_image:
                            media_asset, created = MediaAsset.objects.get_or_create(
                                source_url=best_image['url'],
                                defaults={
                                    'type': 'image',
                                    'width': best_image.get('width'),
                                    'height': best_image.get('height'),
                                    'mime_type': 'image/jpeg'
                                }
                            )
                            article.raw_article.media_assets.add(media_asset)
                            article.cover_media = media_asset
                            article.save()
                            print(f"✅ Extracted from HTML: {best_image['url'][:80]}...")
            break

if __name__ == '__main__':
    main()

