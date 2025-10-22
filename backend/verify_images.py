#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genienews_backend.settings')
django.setup()

from news.models import ArticleCurated

top8 = ArticleCurated.objects.select_related('raw_article', 'cover_media').order_by('-relevance_score')[:8]

print('TOP 8 ARTICLES WITH IMAGES:')
print('=' * 80)

count = 0
for i, a in enumerate(top8, 1):
    has = '✅' if a.cover_media else '❌'
    count += 1 if a.cover_media else 0
    print(f'{i}. {has} {a.raw_article.title[:65]}...')
    if a.cover_media:
        print(f'   {a.cover_media.source_url[:75]}...')

print(f'\n📊 Total: {count}/8 articles have images ({count/8*100:.0f}%)')

