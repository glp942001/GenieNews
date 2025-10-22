#!/usr/bin/env python
"""
Add fallback images for articles without cover media.
Uses multiple strategies including Unsplash API for relevant AI/tech images.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genienews_backend.settings')
django.setup()

from news.models import ArticleCurated, MediaAsset
from news.utils import extract_best_image_from_html
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Curated list of high-quality AI/tech stock images from Unsplash
FALLBACK_IMAGES = [
    {
        'url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800',
        'keywords': ['ai', 'artificial intelligence', 'neural', 'deep learning'],
        'description': 'AI Neural Network'
    },
    {
        'url': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800',
        'keywords': ['robot', 'robotics', 'automation', 'machine'],
        'description': 'Robotics and Automation'
    },
    {
        'url': 'https://images.unsplash.com/photo-1535378917042-10a22c95931a?w=800',
        'keywords': ['code', 'programming', 'developer', 'software'],
        'description': 'Code and Programming'
    },
    {
        'url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800',
        'keywords': ['data', 'analytics', 'visualization', 'analysis'],
        'description': 'Data Analytics'
    },
    {
        'url': 'https://images.unsplash.com/photo-1488229297570-58520851e868?w=800',
        'keywords': ['chip', 'processor', 'hardware', 'semiconductor'],
        'description': 'Computer Chip'
    },
    {
        'url': 'https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800',
        'keywords': ['chatbot', 'chat', 'conversation', 'assistant'],
        'description': 'AI Chatbot'
    },
    {
        'url': 'https://images.unsplash.com/photo-1555255707-c07966088b7b?w=800',
        'keywords': ['cloud', 'server', 'computing', 'infrastructure'],
        'description': 'Cloud Computing'
    },
    {
        'url': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800',
        'keywords': ['microsoft', 'copilot', 'windows', 'assistant'],
        'description': 'Tech Interface'
    }
]

def get_relevant_fallback_image(article_title, article_tags):
    """Get most relevant fallback image based on article content."""
    title_lower = article_title.lower()
    tags_lower = [tag.lower() for tag in article_tags] if article_tags else []
    
    # Score each image
    scored_images = []
    for img in FALLBACK_IMAGES:
        score = 0
        for keyword in img['keywords']:
            if keyword in title_lower:
                score += 10
            for tag in tags_lower:
                if keyword in tag:
                    score += 5
        scored_images.append((score, img))
    
    # Sort by score and return best match
    scored_images.sort(key=lambda x: x[0], reverse=True)
    
    if scored_images[0][0] > 0:
        return scored_images[0][1]
    
    # Default to first image
    return FALLBACK_IMAGES[0]

def main():
    # Get articles without cover images
    articles_without_images = ArticleCurated.objects.filter(
        cover_media__isnull=True
    ).select_related('raw_article')[:10]
    
    if not articles_without_images:
        print("✅ All articles have cover images!")
        return
    
    print(f"Found {len(articles_without_images)} articles without images")
    print("=" * 80)
    
    for article in articles_without_images:
        raw_article = article.raw_article
        print(f"\n📰 {raw_article.title[:70]}...")
        
        # Strategy 1: Try HTML extraction
        if raw_article.raw_html:
            print("  🔍 Trying HTML extraction...")
            try:
                best_image = extract_best_image_from_html(raw_article.raw_html, raw_article.url)
                if best_image:
                    media_asset, created = MediaAsset.objects.get_or_create(
                        source_url=best_image['url'][:200],  # Truncate if needed
                        defaults={
                            'type': 'image',
                            'width': best_image.get('width'),
                            'height': best_image.get('height'),
                            'mime_type': 'image/jpeg'
                        }
                    )
                    raw_article.media_assets.add(media_asset)
                    article.cover_media = media_asset
                    article.save()
                    print(f"  ✅ Extracted from HTML: {best_image['url'][:60]}...")
                    continue
            except Exception as e:
                print(f"  ⚠️  HTML extraction failed: {str(e)}")
        
        # Strategy 2: Fetch HTML content and try again
        if not raw_article.raw_html:
            print("  🌐 Fetching HTML content...")
            try:
                response = requests.get(raw_article.url, timeout=20)
                raw_article.raw_html = response.text
                raw_article.save()
                
                best_image = extract_best_image_from_html(raw_article.raw_html, raw_article.url)
                if best_image:
                    media_asset, created = MediaAsset.objects.get_or_create(
                        source_url=best_image['url'][:200],
                        defaults={
                            'type': 'image',
                            'width': best_image.get('width'),
                            'height': best_image.get('height'),
                            'mime_type': 'image/jpeg'
                        }
                    )
                    raw_article.media_assets.add(media_asset)
                    article.cover_media = media_asset
                    article.save()
                    print(f"  ✅ Extracted after fetching: {best_image['url'][:60]}...")
                    continue
            except Exception as e:
                print(f"  ⚠️  Fetch failed: {str(e)}")
        
        # Strategy 3: Use relevant fallback image
        print("  🎨 Using relevant fallback image...")
        fallback = get_relevant_fallback_image(raw_article.title, article.ai_tags)
        
        try:
            media_asset, created = MediaAsset.objects.get_or_create(
                source_url=fallback['url'],
                defaults={
                    'type': 'image',
                    'width': 800,
                    'height': 600,
                    'mime_type': 'image/jpeg'
                }
            )
            raw_article.media_assets.add(media_asset)
            article.cover_media = media_asset
            article.save()
            print(f"  ✅ Added fallback: {fallback['description']}")
            print(f"     {fallback['url'][:80]}...")
        except Exception as e:
            print(f"  ❌ Failed to add fallback: {str(e)}")
    
    # Final check
    print("\n" + "=" * 80)
    print("FINAL STATUS - TOP 8 ARTICLES")
    print("=" * 80)
    
    top_8 = ArticleCurated.objects.select_related(
        'raw_article',
        'cover_media'
    ).order_by('-relevance_score')[:8]
    
    images_count = 0
    for i, article in enumerate(top_8, 1):
        has_image = "✅" if article.cover_media else "❌"
        if article.cover_media:
            images_count += 1
        print(f"{i}. {has_image} {article.raw_article.title[:70]}...")
    
    print(f"\n📊 Coverage: {images_count}/8 articles have images ({images_count/8*100:.0f}%)")

if __name__ == '__main__':
    main()

