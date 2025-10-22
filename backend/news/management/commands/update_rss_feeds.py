"""
Django management command to update sources with proper RSS feed URLs
"""
import os
from django.core.management.base import BaseCommand
from news.models import Source


class Command(BaseCommand):
    help = 'Update existing sources with proper RSS feed URLs or create new ones'

    def handle(self, *args, **options):
        
        # Mapping of source names to actual RSS feed URLs
        rss_feeds = {
            'Tech-Crunch': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'Venturebeat': 'https://venturebeat.com/category/ai/feed/',
            'The Verge': 'https://www.theverge.com/rss/index.xml',
            'MIT Technica': 'https://feeds.arstechnica.com/arstechnica/technology-lab',
            'WIRED': 'https://www.wired.com/feed/tag/ai/latest/rss',
            'ScienceDaily': 'https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml',
            'ZDNet': 'https://www.zdnet.com/news/rss.xml',
            'IEEE Spectrum': 'https://spectrum.ieee.org/feeds/feed.rss',
            'KDnuggets': 'https://feeds.feedburner.com/kdnuggets-data-mining-analytics',
            'MarkTechPost': 'https://www.marktechpost.com/feed/',
            'HackerNoon': 'https://hackernoon.com/feed',
            'OpenAI Blog': 'https://openai.com/blog/rss/',
            'Google AI Blog': 'https://blog.research.google/feeds/posts/default',
            'DeepMind Blog': 'https://deepmind.google/blog/rss.xml',
            'Meta AI Blog': 'https://ai.meta.com/blog/rss/',
            'Microsoft AI Blog': 'https://www.microsoft.com/en-us/research/feed/',
            'NVIDIA Blogs': 'https://blogs.nvidia.com/feed/',
            'AWS Machine Learning Blog': 'https://aws.amazon.com/blogs/machine-learning/feed/',
            'IBM Research AI Blog': 'https://research.ibm.com/blog/rss',
            'Apple Machine Learning Research': 'https://machinelearning.apple.com/rss.xml',
            'Intel AI Blog': 'https://community.intel.com/t5/blogs/rss?community.id=ai',
            'Stanford AI Lab (SAIL) Blog': 'https://hai.stanford.edu/news/rss.xml',
            'MIT News': 'https://news.mit.edu/rss/topic/artificial-intelligence2',
            'The Gradient': 'https://thegradient.pub/rss/',
            'Hugging Face': 'https://huggingface.co/blog/feed.xml',
        }
        
        # Additional new sources to add
        new_sources = {
            'AI News': 'https://www.artificialintelligence-news.com/feed/',
            'Unite.AI': 'https://www.unite.ai/feed/',
            'MIT Technology Review': 'https://www.technologyreview.com/feed/',
            'Towards Data Science': 'https://towardsdatascience.com/feed',
            'Papers With Code': 'https://paperswithcode.com/rss.xml',
            'Anthropic': 'https://www.anthropic.com/news/rss.xml',
            'Berkeley AI Research': 'https://bair.berkeley.edu/blog/feed.xml',
        }
        
        updated_count = 0
        created_count = 0
        failed_count = 0
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('UPDATING RSS FEED URLS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Update existing sources
        for name, rss_url in rss_feeds.items():
            try:
                source = Source.objects.filter(name=name).first()
                if source:
                    old_url = source.feed_url
                    source.feed_url = rss_url
                    source.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated: {name}'))
                    self.stdout.write(f'  Old: {old_url[:60]}...')
                    self.stdout.write(f'  New: {rss_url}')
                    updated_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ Not found: {name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error updating {name}: {e}'))
                failed_count += 1
        
        # Create new sources
        self.stdout.write(self.style.SUCCESS('\nADDING NEW SOURCES'))
        for name, rss_url in new_sources.items():
            try:
                source, created = Source.objects.get_or_create(
                    name=name,
                    defaults={
                        'feed_url': rss_url,
                        'site_url': rss_url.split('/feed')[0] if '/feed' in rss_url else rss_url.split('/rss')[0],
                        'active': True,
                        'fetch_interval_minutes': 10080,  # Weekly
                        'max_articles_per_fetch': 50,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created: {name}'))
                    self.stdout.write(f'  URL: {rss_url}')
                    created_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ Already exists: {name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error creating {name}: {e}'))
                failed_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('UPDATE SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'Sources updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Sources created: {created_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {failed_count}'))
        
        total_sources = Source.objects.filter(active=True).count()
        self.stdout.write(self.style.SUCCESS(f'\nTotal active sources: {total_sources}'))
        self.stdout.write(self.style.SUCCESS('\nReady to ingest AI/tech news!'))

