#!/usr/bin/env python
"""
Script to retroactively extract and add cover images to curated articles.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genienews_backend.settings')
django.setup()

from news.models import ArticleCurated, MediaAsset
from news.utils import extract_best_image_from_html
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Check current status
    total = ArticleCurated.objects.count()
    with_images = ArticleCurated.objects.filter(cover_media__isnull=False).count()
    without_images = total - with_images
    
    print("=" * 80)
    print("CURRENT STATUS")
    print("=" * 80)
    print(f"Total curated articles: {total}")
    print(f"With cover images: {with_images} ({with_images/total*100:.1f}%)")
    print(f"Without images: {without_images}")
    
    # Show top 8 articles
    print("\n" + "=" * 80)
    print("TOP 8 ARTICLES (by relevance)")
    print("=" * 80)
    top_8 = ArticleCurated.objects.select_related('raw_article', 'cover_media').order_by('-relevance_score')[:8]
    for i, article in enumerate(top_8, 1):
        has_image = "✅ YES" if article.cover_media else "❌ NO"
        print(f"{i}. {article.raw_article.title[:70]}...")
        print(f"   Image: {has_image}")
        if article.cover_media:
            print(f"   URL: {article.cover_media.source_url[:80]}...")
    
    # Extract images for articles without them
    if without_images > 0:
        print("\n" + "=" * 80)
        print(f"EXTRACTING IMAGES FOR {without_images} ARTICLES")
        print("=" * 80)
        
        articles_without_images = ArticleCurated.objects.filter(
            cover_media__isnull=True
        ).select_related('raw_article')[:50]  # Process first 50
        
        extracted_count = 0
        
        for article in articles_without_images:
            raw_article = article.raw_article
            
            # Check if article has HTML content
            if not raw_article.raw_html:
                logger.info(f"Skipping article {raw_article.id} - no HTML content")
                continue
            
            # Try to extract image
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
                    
                    # Set as cover media for curated article
                    article.cover_media = media_asset
                    article.save()
                    
                    extracted_count += 1
                    source = best_image.get('source', 'unknown')
                    print(f"✅ Extracted image for: {raw_article.title[:60]}... (from {source})")
                else:
                    print(f"⚠️  No image found for: {raw_article.title[:60]}...")
                    
            except Exception as e:
                logger.error(f"Error extracting image for article {raw_article.id}: {str(e)}")
                continue
        
        print("\n" + "=" * 80)
        print("EXTRACTION COMPLETE")
        print("=" * 80)
        print(f"Images extracted: {extracted_count}")
        
        # Show updated status
        with_images_after = ArticleCurated.objects.filter(cover_media__isnull=False).count()
        print(f"Articles with images now: {with_images_after} ({with_images_after/total*100:.1f}%)")
        
        # Show top 8 again
        print("\n" + "=" * 80)
        print("TOP 8 ARTICLES - AFTER EXTRACTION")
        print("=" * 80)
        top_8_after = ArticleCurated.objects.select_related('raw_article', 'cover_media').order_by('-relevance_score')[:8]
        for i, article in enumerate(top_8_after, 1):
            has_image = "✅ YES" if article.cover_media else "❌ NO"
            print(f"{i}. {article.raw_article.title[:70]}...")
            print(f"   Image: {has_image}")
            if article.cover_media:
                print(f"   URL: {article.cover_media.source_url[:80]}...")

if __name__ == '__main__':
    main()

