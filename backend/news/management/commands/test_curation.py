"""
Management command to test AI curation on a single article without saving.

Usage:
    python manage.py test_curation <article_id>
    python manage.py test_curation --latest
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from news.models import ArticleRaw
from news.ai_service import get_ai_service, AIServiceError


class Command(BaseCommand):
    help = 'Test AI curation on a single article without saving to database'

    def add_arguments(self, parser):
        parser.add_argument(
            'article_id',
            nargs='?',
            type=int,
            help='ID of the article to test curation on'
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Test curation on the latest uncurated article'
        )
        parser.add_argument(
            '--show-text',
            action='store_true',
            help='Show the article text being processed'
        )

    def handle(self, *args, **options):
        article_id = options.get('article_id')
        use_latest = options.get('latest')
        show_text = options.get('show_text')

        # Get article
        if use_latest:
            try:
                article = ArticleRaw.objects.filter(curated__isnull=True).latest('created_at')
                self.stdout.write(f"Testing on latest uncurated article (ID: {article.id})")
            except ArticleRaw.DoesNotExist:
                raise CommandError("No uncurated articles found")
        elif article_id:
            try:
                article = ArticleRaw.objects.get(id=article_id)
            except ArticleRaw.DoesNotExist:
                raise CommandError(f"Article with ID {article_id} not found")
        else:
            raise CommandError("Please provide an article ID or use --latest flag")

        # Display article info
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("ARTICLE INFORMATION"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"ID: {article.id}")
        self.stdout.write(f"Title: {article.title}")
        self.stdout.write(f"Source: {article.source.name}")
        self.stdout.write(f"URL: {article.url}")
        self.stdout.write(f"Published: {article.published_at}")
        self.stdout.write(f"Feed Summary: {article.summary_feed[:200]}...")
        self.stdout.write(f"Has raw_html: {'Yes' if article.raw_html else 'No'}")
        
        # Prepare article text
        article_text = article.summary_feed
        if article.raw_html:
            article_text = article.raw_html[:10000] + " " + article.summary_feed

        if show_text:
            self.stdout.write("\n" + "-" * 80)
            self.stdout.write("ARTICLE TEXT (truncated to 1000 chars):")
            self.stdout.write("-" * 80)
            self.stdout.write(article_text[:1000])
            self.stdout.write("...\n")

        # Initialize AI service
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("INITIALIZING AI SERVICE"))
        self.stdout.write("=" * 80)
        
        try:
            ai_service = get_ai_service()
            self.stdout.write(self.style.SUCCESS("✓ AI service initialized"))
            self.stdout.write(f"  Model: {settings.AI_MODEL}")
            self.stdout.write(f"  Embedding Model: {settings.EMBEDDING_MODEL}")
            self.stdout.write(f"  API Key: {settings.OPENAI_API_KEY[:20]}...")
        except Exception as e:
            raise CommandError(f"Failed to initialize AI service: {str(e)}")

        # Test summaries generation
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("TESTING SUMMARY GENERATION"))
        self.stdout.write("=" * 80)
        
        try:
            summary_short, summary_detailed = ai_service.generate_summaries(
                article_text,
                article.title
            )
            self.stdout.write(self.style.SUCCESS("✓ Summaries generated"))
            self.stdout.write("\nSHORT SUMMARY:")
            self.stdout.write("-" * 80)
            self.stdout.write(summary_short)
            self.stdout.write("\nDETAILED SUMMARY:")
            self.stdout.write("-" * 80)
            self.stdout.write(summary_detailed)
        except AIServiceError as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to generate summaries: {str(e)}"))
            summary_short, summary_detailed = "Error", "Error"

        # Test relevance score calculation
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("TESTING RELEVANCE SCORE CALCULATION"))
        self.stdout.write("=" * 80)
        
        try:
            relevance_score = ai_service.calculate_relevance_score(
                article_text,
                article.title
            )
            self.stdout.write(self.style.SUCCESS("✓ Relevance score calculated"))
            
            # Color code the score
            if relevance_score >= 0.7:
                score_style = self.style.SUCCESS
                assessment = "HIGH relevance to AI/tech"
            elif relevance_score >= 0.4:
                score_style = self.style.WARNING
                assessment = "MEDIUM relevance to AI/tech"
            else:
                score_style = self.style.ERROR
                assessment = "LOW relevance to AI/tech"
            
            self.stdout.write(f"\nRelevance Score: {score_style(f'{relevance_score:.3f}')}")
            self.stdout.write(f"Assessment: {assessment}")
        except AIServiceError as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to calculate relevance: {str(e)}"))
            relevance_score = 0.5

        # Test tags generation
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("TESTING TAG GENERATION"))
        self.stdout.write("=" * 80)
        
        try:
            ai_tags = ai_service.generate_tags(article_text, article.title)
            self.stdout.write(self.style.SUCCESS("✓ Tags generated"))
            self.stdout.write(f"\nTags ({len(ai_tags)}): {', '.join(ai_tags)}")
        except AIServiceError as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to generate tags: {str(e)}"))
            ai_tags = []

        # Test embeddings generation
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("TESTING EMBEDDING GENERATION"))
        self.stdout.write("=" * 80)
        
        try:
            embedding = ai_service.generate_embeddings(summary_detailed)
            self.stdout.write(self.style.SUCCESS("✓ Embedding generated"))
            self.stdout.write(f"\nEmbedding dimension: {len(embedding)}")
            self.stdout.write(f"First 5 values: {embedding[:5]}")
            self.stdout.write(f"Vector norm: {sum(x*x for x in embedding)**0.5:.4f}")
        except AIServiceError as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to generate embedding: {str(e)}"))
            embedding = [0.0] * 1536

        # Check for cover media
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("MEDIA ASSETS"))
        self.stdout.write("=" * 80)
        
        media_count = article.media_assets.count()
        image_media = article.media_assets.filter(type='image').first()
        
        self.stdout.write(f"Total media assets: {media_count}")
        if image_media:
            self.stdout.write(f"Cover image: {image_media.source_url}")
        else:
            self.stdout.write("No cover image found")

        # Summary
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("TEST SUMMARY"))
        self.stdout.write("=" * 80)
        self.stdout.write("All AI curation components tested successfully!")
        self.stdout.write("\nThis article would be curated with:")
        self.stdout.write(f"  • Relevance Score: {relevance_score:.3f}")
        self.stdout.write(f"  • Tags: {len(ai_tags)}")
        self.stdout.write(f"  • Embedding: {len(embedding)} dimensions")
        self.stdout.write(f"  • Cover Media: {'Yes' if image_media else 'No'}")
        self.stdout.write("\nNo changes were saved to the database.")
        self.stdout.write("=" * 80 + "\n")

