#!/usr/bin/env python3
"""Test that API is serving images for top 8 articles."""
import requests
import json
import time

API_URL = 'http://localhost:8000/api/articles/?ordering=-relevance_score'

print("Testing API endpoint for images...")
print("=" * 80)

# Wait a moment for server to start
time.sleep(2)

try:
    response = requests.get(API_URL, timeout=5)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('results', [])[:8]
        
        print(f"✅ API responding successfully")
        print(f"Retrieved {len(articles)} articles\n")
        
        images_count = 0
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'No title')[:60]
            cover_media = article.get('cover_media')
            has_image = cover_media and cover_media.get('url')
            
            if has_image:
                images_count += 1
            
            status = "✅" if has_image else "❌"
            print(f"{i}. {status} {title}...")
            
            if has_image:
                url = cover_media['url'][:75]
                print(f"   Image URL: {url}...")
        
        print(f"\n📊 Result: {images_count}/{len(articles)} articles have images")
        
        if images_count == 8:
            print("\n🎉 SUCCESS! All 8 articles have images!")
            print("✅ Your frontend should display all images now!")
        elif images_count >= 7:
            print("\n✅ Great! Almost all articles have images.")
        else:
            print("\n⚠️  Some articles missing images. Run add_fallback_images.py")
    else:
        print(f"❌ API returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API. Make sure backend is running:")
    print("   cd backend && python manage.py runserver")
except Exception as e:
    print(f"❌ Error: {str(e)}")

