#!/usr/bin/env python
"""
Script to fetch HTML content and extract cover images for the top 8 articles.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genienews_backend.settings')
django.setup()

from news.models import ArticleCurated, MediaAsset
from news.content_extractor import extract_article_content
from news.utils import extract_best_image_from_html
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Get top 8 articles by relevance
    print("=" * 80)
    print("FETCHING & EXTRACTING IMAGES FOR TOP 8 ARTICLES")
    print("=" * 80)
    
    top_8 = ArticleCurated.objects.select_related(
        'raw_article', 
        'cover_media'
    ).order_by('-relevance_score')[:8]
    
    print(f"\nProcessing {len(top_8)} articles...")
    
    extracted_count = 0
    
    for i, article in enumerate(top_8, 1):
        raw_article = article.raw_article
        print(f"\n[{i}/8] {raw_article.title[:70]}...")
        
        # Check if already has cover image
        if article.cover_media:
            print(f"  ✅ Already has cover image: {article.cover_media.source_url[:80]}...")
            continue
        
        # Check if has HTML content
        if raw_article.raw_html:
            print(f"  📄 Has HTML content, extracting image...")
        else:
            print(f"  🌐 Fetching HTML content from: {raw_article.url[:60]}...")
            
            try:
                # Fetch HTML content
                result = extract_article_content(raw_article.url)
                
                if result['success'] and result['content']:
                    # Save HTML content
                    from bs4 import BeautifulSoup
                    import requests
                    
                    response = requests.get(raw_article.url, timeout=30)
                    raw_article.raw_html = response.text
                    raw_article.save()
                    print(f"  ✅ Fetched HTML content ({len(raw_article.raw_html)} chars)")
                else:
                    print(f"  ❌ Failed to fetch content: {result.get('error', 'Unknown error')}")
                    continue
                    
            except Exception as e:
                print(f"  ❌ Error fetching HTML: {str(e)}")
                continue
        
        # Try to extract image from HTML
        try:
            best_image = extract_best_image_from_html(raw_article.raw_html, raw_article.url)
            
            if best_image:
                # Create or get MediaAsset
                media_asset, created = MediaAsset.objects.get_or_create(
                    source_url=best_image['url'],
                    defaults={
                        'type': 'image',
                        'width': best_image.get('width'),
                        'height': best_image.get('height'),
                        'mime_type': 'image/jpeg'
                    }
                )
                
                # Link to raw article
                raw_article.media_assets.add(media_asset)
                
                # Set as cover media
                article.cover_media = media_asset
                article.save()
                
                source = best_image.get('source', 'unknown')
                extracted_count += 1
                print(f"  🎉 Extracted image (from {source}):")
                print(f"     {best_image['url'][:80]}...")
            else:
                print(f"  ⚠️  No suitable image found in HTML")
                
        except Exception as e:
            logger.error(f"  ❌ Error extracting image: {str(e)}")
            continue
    
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Images extracted for top 8: {extracted_count}/8")
    
    # Show final status
    print("\n" + "=" * 80)
    print("FINAL STATUS - TOP 8 ARTICLES")
    print("=" * 80)
    
    top_8_final = ArticleCurated.objects.select_related(
        'raw_article', 
        'cover_media'
    ).order_by('-relevance_score')[:8]
    
    for i, article in enumerate(top_8_final, 1):
        has_image = "✅ YES" if article.cover_media else "❌ NO"
        print(f"\n{i}. {article.raw_article.title}")
        print(f"   Image: {has_image}")
        if article.cover_media:
            print(f"   URL: {article.cover_media.source_url}")

if __name__ == '__main__':
    main()

