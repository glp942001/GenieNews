"""
Django management command to import RSS feed sources from sources.txt
"""
import os
from django.core.management.base import BaseCommand
from urllib.parse import urlparse
from news.models import Source


class Command(BaseCommand):
    help = 'Import RSS feed sources from sources.txt file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='../sources.txt',
            help='Path to sources.txt file (default: ../sources.txt)'
        )

    def handle(self, *args, **options):
        sources_file = options['file']
        
        # Build absolute path from backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        file_path = os.path.join(backend_dir, sources_file)
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Reading sources from: {file_path}'))
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                
                # Skip empty lines, the header line, and API key line
                if not line or line.lower().startswith('sources') or line.startswith('sk-'):
                    continue
                
                # Parse "Name: URL" or "Name:URL" format
                if ':' not in line:
                    self.stdout.write(self.style.WARNING(f'Line {line_num}: Invalid format (no colon): {line}'))
                    error_count += 1
                    continue
                
                # Split on first colon only
                parts = line.split(':', 1)
                if len(parts) != 2:
                    self.stdout.write(self.style.WARNING(f'Line {line_num}: Invalid format: {line}'))
                    error_count += 1
                    continue
                
                name = parts[0].strip()
                url = parts[1].strip()
                
                # Validate URL
                if not url.startswith('http'):
                    self.stdout.write(self.style.WARNING(f'Line {line_num}: Invalid URL: {url}'))
                    error_count += 1
                    continue
                
                # Extract site URL (base domain)
                try:
                    parsed = urlparse(url)
                    site_url = f"{parsed.scheme}://{parsed.netloc}"
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Line {line_num}: Error parsing URL {url}: {e}'))
                    error_count += 1
                    continue
                
                # Check if source already exists
                if Source.objects.filter(feed_url=url).exists():
                    self.stdout.write(self.style.WARNING(f'Skipping duplicate: {name} ({url})'))
                    skip_count += 1
                    continue
                
                # Create source
                try:
                    source = Source.objects.create(
                        name=name,
                        feed_url=url,
                        site_url=site_url,
                        active=True,
                        fetch_interval_minutes=10080,  # Weekly
                        max_articles_per_fetch=50
                    )
                    self.stdout.write(self.style.SUCCESS(f'✓ Created: {name}'))
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Line {line_num}: Error creating source {name}: {e}'))
                    error_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Import Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  Successfully created: {success_count}'))
        self.stdout.write(self.style.WARNING(f'  Skipped (duplicates): {skip_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  Errors: {error_count}'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        # Note about RSS feeds
        if success_count > 0:
            self.stdout.write(self.style.WARNING('\nNote: Some URLs may be web pages rather than RSS feeds.'))
            self.stdout.write(self.style.WARNING('You may need to find actual RSS feed URLs for proper ingestion.'))
            self.stdout.write(self.style.WARNING('Check Django admin to verify and update feed URLs as needed.'))

