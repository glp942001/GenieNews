#!/usr/bin/env python
"""
Script to extract images from RSS feeds for top 8 articles.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genienews_backend.settings')
django.setup()

from news.models import ArticleCurated, ArticleRaw, MediaAsset
from news.feed_parser import FeedParser
from news.utils import extract_media_from_rss_entry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 80)
    print("EXTRACTING IMAGES FROM RSS FEEDS FOR TOP 8")
    print("=" * 80)
    
    # Get top 8 articles
    top_8 = ArticleCurated.objects.select_related(
        'raw_article',
        'raw_article__source',
        'cover_media'
    ).order_by('-relevance_score')[:8]
    
    extracted_count = 0
    
    for i, article in enumerate(top_8, 1):
        raw_article = article.raw_article
        source = raw_article.source
        
        print(f"\n[{i}/8] {raw_article.title[:70]}...")
        print(f"  Source: {source.name}")
        print(f"  URL: {raw_article.url[:80]}...")
        
        # Skip if already has cover
        if article.cover_media:
            print(f"  ✅ Already has cover image")
            continue
        
        # Check if article has media assets from RSS
        existing_media = raw_article.media_assets.filter(type='image').first()
        
        if existing_media:
            print(f"  📸 Found existing media asset from RSS")
            article.cover_media = existing_media
            article.save()
            print(f"  ✅ Set as cover: {existing_media.source_url[:80]}...")
            extracted_count += 1
        else:
            # Try to re-fetch from RSS feed
            print(f"  🔄 Re-fetching from RSS feed: {source.feed_url[:60]}...")
            
            try:
                parser = FeedParser()
                feed = parser.fetch_feed(source.feed_url)
                
                # Find the matching entry
                for entry in feed.entries[:50]:  # Check first 50 entries
                    entry_url = getattr(entry, 'link', '')
                    if entry_url == raw_article.url:
                        print(f"  ✅ Found matching RSS entry")
                        
                        # Extract media from entry
                        media_list = extract_media_from_rss_entry(entry)
                        
                        if media_list:
                            print(f"  📸 Found {len(media_list)} media items in RSS")
                            
                            # Use first image
                            first_media = media_list[0]
                            media_asset, created = MediaAsset.objects.get_or_create(
                                source_url=first_media['url'],
                                defaults={
                                    'type': 'image',
                                    'width': first_media.get('width'),
                                    'height': first_media.get('height'),
                                    'mime_type': first_media.get('type', 'image/jpeg')
                                }
                            )
                            
                            # Link to article
                            raw_article.media_assets.add(media_asset)
                            article.cover_media = media_asset
                            article.save()
                            
                            print(f"  ✅ Extracted and set cover: {media_asset.source_url[:80]}...")
                            extracted_count += 1
                        else:
                            print(f"  ⚠️  No media found in RSS entry")
                        break
                else:
                    print(f"  ⚠️  Article not found in RSS feed (might be too old)")
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Images extracted: {extracted_count}/8")
    
    # Final status
    print("\n" + "=" * 80)
    print("FINAL STATUS - TOP 8 ARTICLES")
    print("=" * 80)
    
    top_8_final = ArticleCurated.objects.select_related(
        'raw_article',
        'cover_media'
    ).order_by('-relevance_score')[:8]
    
    images_count = 0
    for i, article in enumerate(top_8_final, 1):
        has_image = "✅ YES" if article.cover_media else "❌ NO"
        if article.cover_media:
            images_count += 1
        print(f"\n{i}. {article.raw_article.title[:70]}...")
        print(f"   Image: {has_image}")
        if article.cover_media:
            print(f"   URL: {article.cover_media.source_url[:80]}...")
    
    print(f"\n📊 Coverage: {images_count}/8 articles have images ({images_count/8*100:.0f}%)")

if __name__ == '__main__':
    main()

