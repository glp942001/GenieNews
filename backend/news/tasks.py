from celery import shared_task
import logging
import time
from datetime import datetime
from typing import List, Dict, Any

from django.utils import timezone
from django.db import transaction

from .models import Source, ArticleRaw, MediaAsset, FeedIngestionLog
from .feed_parser import parse_feed, FeedParseError
from .content_extractor import extract_article_content

logger = logging.getLogger(__name__)


@shared_task
def ingest_all_feeds_task():
    """
    Main orchestrator task to ingest all active feeds.
    
    This task:
    1. Gets all active sources
    2. Spawns individual tasks per source
    3. Collects results and logs summary
    """
    logger.info("Starting feed ingestion for all sources")
    
    # Get all active sources
    sources = Source.objects.filter(active=True)
    
    if not sources.exists():
        logger.warning("No active sources found")
        return {"status": "no_sources", "message": "No active sources to process"}
    
    logger.info(f"Found {sources.count()} active sources")
    
    # Spawn individual tasks
    task_results = []
    for source in sources:
        try:
            # Check if source needs to be fetched (based on interval)
            if _should_fetch_source(source):
                result = ingest_single_feed_task.delay(source.id)
                task_results.append({
                    'source_id': source.id,
                    'source_name': source.name,
                    'task_id': result.id,
                    'status': 'queued'
                })
                logger.info(f"Queued feed ingestion for: {source.name}")
            else:
                logger.info(f"Skipping {source.name} - not due for fetch yet")
                task_results.append({
                    'source_id': source.id,
                    'source_name': source.name,
                    'status': 'skipped',
                    'reason': 'not_due'
                })
        except Exception as e:
            logger.error(f"Error queuing task for {source.name}: {str(e)}")
            task_results.append({
                'source_id': source.id,
                'source_name': source.name,
                'status': 'error',
                'error': str(e)
            })
    
    logger.info(f"Feed ingestion orchestration completed. {len(task_results)} sources processed.")
    return {
        "status": "completed",
        "sources_processed": len(task_results),
        "results": task_results
    }


@shared_task(rate_limit='10/m')  # 10 tasks per minute max
def ingest_single_feed_task(source_id: int):
    """
    Ingest a single RSS/Atom feed.
    
    Args:
        source_id: ID of the Source to process
    """
    start_time = time.time()
    ingestion_log = None
    
    try:
        # Get source
        try:
            source = Source.objects.get(id=source_id, active=True)
        except Source.DoesNotExist:
            logger.error(f"Source {source_id} not found or inactive")
            return {"status": "error", "message": "Source not found or inactive"}
        
        logger.info(f"Starting feed ingestion for: {source.name}")
        
        # Create ingestion log
        ingestion_log = FeedIngestionLog.objects.create(
            source=source,
            status='failed',  # Will update on success
            started_at=timezone.now()
        )
        
        # Parse feed
        try:
            feed, entries = parse_feed(
                source.feed_url,
                custom_headers=source.custom_headers,
                max_articles=source.max_articles_per_fetch
            )
        except FeedParseError as e:
            logger.error(f"Feed parsing failed for {source.name}: {str(e)}")
            _update_source_error(source, str(e))
            ingestion_log.error_message = str(e)
            ingestion_log.completed_at = timezone.now()
            ingestion_log.execution_time_seconds = time.time() - start_time
            ingestion_log.save()
            return {"status": "error", "message": str(e)}
        
        # Process entries
        articles_created = 0
        articles_updated = 0
        
        with transaction.atomic():
            for entry_data in entries:
                try:
                    article, created = _create_or_update_article(source, entry_data)
                    if created:
                        articles_created += 1
                    else:
                        articles_updated += 1
                except Exception as e:
                    logger.error(f"Error processing article {entry_data.get('title', 'Unknown')}: {str(e)}")
                    continue
        
        # Update source status
        _update_source_success(source)
        
        # Update ingestion log
        ingestion_log.status = 'success'
        ingestion_log.articles_found = len(entries)
        ingestion_log.articles_created = articles_created
        ingestion_log.articles_updated = articles_updated
        ingestion_log.completed_at = timezone.now()
        ingestion_log.execution_time_seconds = time.time() - start_time
        ingestion_log.save()
        
        logger.info(f"Successfully processed {source.name}: {articles_created} created, {articles_updated} updated")
        
        # Trigger curation task if new articles were created
        if articles_created > 0:
            logger.info(f"Triggering curation for {articles_created} new articles")
            curate_articles_task.delay(batch_size=articles_created)
        
        return {
            "status": "success",
            "source_name": source.name,
            "articles_found": len(entries),
            "articles_created": articles_created,
            "articles_updated": articles_updated,
            "execution_time": time.time() - start_time,
            "curation_triggered": articles_created > 0
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in ingest_single_feed_task: {str(e)}")
        
        # Update source error
        if 'source' in locals():
            _update_source_error(source, str(e))
        
        # Update ingestion log
        if ingestion_log:
            ingestion_log.error_message = str(e)
            ingestion_log.completed_at = timezone.now()
            ingestion_log.execution_time_seconds = time.time() - start_time
            ingestion_log.save()
        
        return {"status": "error", "message": str(e)}


def _should_fetch_source(source: Source) -> bool:
    """Check if source should be fetched based on interval."""
    if not source.last_fetched_at:
        return True
    
    time_since_last = timezone.now() - source.last_fetched_at
    interval_minutes = source.fetch_interval_minutes
    
    return time_since_last.total_seconds() >= (interval_minutes * 60)


def _create_or_update_article(source: Source, entry_data: Dict[str, Any]) -> tuple:
    """Create or update ArticleRaw from entry data."""
    article_url = entry_data['url']
    
    # Get or create article
    article, created = ArticleRaw.objects.get_or_create(
        url=article_url,
        defaults={
            'source': source,
            'title': entry_data['title'],
            'published_at': entry_data['published_at'],
            'summary_feed': entry_data['summary_feed'],
        }
    )
    
    # Update if not created (in case of updates)
    if not created:
        article.title = entry_data['title']
        article.published_at = entry_data['published_at']
        article.summary_feed = entry_data['summary_feed']
        article.save()
    
    # Process media assets
    _process_media_assets(article, entry_data.get('media_assets', []))
    
    return article, created


def _process_media_assets(article: ArticleRaw, media_assets: List[Dict]):
    """Process and create MediaAsset objects from RSS media data."""
    for media_data in media_assets:
        try:
            media_url = media_data['url']
            media_type = media_data.get('type', 'image')
            
            # Determine MIME type
            mime_type = _get_mime_type(media_url, media_type)
            
            # Create or get media asset
            media_asset, created = MediaAsset.objects.get_or_create(
                source_url=media_url,
                defaults={
                    'type': media_type,
                    'mime_type': mime_type,
                    'width': media_data.get('width'),
                    'height': media_data.get('height'),
                }
            )
            
            # Link to article if not already linked
            if not article.media_assets.filter(id=media_asset.id).exists():
                article.media_assets.add(media_asset)
                
        except Exception as e:
            logger.error(f"Error processing media asset: {str(e)}")
            continue


def _get_mime_type(url: str, media_type: str) -> str:
    """Determine MIME type from URL and media type."""
    if media_type == 'image':
        if url.lower().endswith(('.jpg', '.jpeg')):
            return 'image/jpeg'
        elif url.lower().endswith('.png'):
            return 'image/png'
        elif url.lower().endswith('.gif'):
            return 'image/gif'
        elif url.lower().endswith('.webp'):
            return 'image/webp'
        else:
            return 'image/jpeg'  # Default
    elif media_type == 'video':
        if url.lower().endswith('.mp4'):
            return 'video/mp4'
        elif url.lower().endswith('.webm'):
            return 'video/webm'
        else:
            return 'video/mp4'  # Default
    else:
        return 'application/octet-stream'


def _update_source_success(source: Source):
    """Update source after successful fetch."""
    source.last_fetched_at = timezone.now()
    source.last_error = None
    source.error_count = 0
    source.save()


def _update_source_error(source: Source, error_message: str):
    """Update source after failed fetch."""
    source.last_error = error_message
    source.error_count += 1
    
    # Deactivate source after 5 consecutive failures
    if source.error_count >= 5:
        source.active = False
        logger.warning(f"Deactivating source {source.name} after {source.error_count} consecutive failures")
    
    source.save()


@shared_task
def fetch_missing_content_task():
    """
    Fetch full HTML content for articles missing raw_html.
    
    This task:
    1. Finds ArticleRaw entries without raw_html
    2. Uses progressive content extraction strategies
    3. Updates articles with extracted content
    """
    logger.info("Starting content fetching for articles missing raw_html")
    
    # Get articles without raw_html
    articles = ArticleRaw.objects.filter(raw_html__isnull=True).exclude(raw_html='')
    
    if not articles.exists():
        logger.info("No articles need content fetching")
        return {"status": "no_articles", "message": "No articles need content fetching"}
    
    logger.info(f"Found {articles.count()} articles needing content")
    
    success_count = 0
    error_count = 0
    
    for article in articles[:100]:  # Limit to 100 articles per run
        try:
            result = fetch_article_content_task.delay(article.id)
            logger.info(f"Queued content fetching for article: {article.title}")
        except Exception as e:
            logger.error(f"Error queuing content fetch for {article.title}: {str(e)}")
            error_count += 1
    
    logger.info(f"Content fetching queued for {articles.count()} articles")
    return {
        "status": "queued",
        "articles_queued": articles.count(),
        "errors": error_count
    }


@shared_task
def fetch_article_content_task(article_id: int):
    """
    Fetch full HTML content for a specific article.
    
    Args:
        article_id: ID of the ArticleRaw to process
    """
    try:
        article = ArticleRaw.objects.get(id=article_id)
    except ArticleRaw.DoesNotExist:
        logger.error(f"Article {article_id} not found")
        return {"status": "error", "message": "Article not found"}
    
    logger.info(f"Fetching content for: {article.title}")
    
    try:
        # Extract content using progressive strategies
        result = extract_article_content(
            article.url,
            custom_headers=article.source.custom_headers
        )
        
        if result['success'] and result['content']:
            # Update article with content
            article.raw_html = result['content']
            article.save()
            
            logger.info(f"Successfully fetched content for: {article.title} (strategy: {result['strategy_used']})")
            return {
                "status": "success",
                "article_id": article_id,
                "strategy_used": result['strategy_used'],
                "content_length": len(result['content'])
            }
        else:
            logger.warning(f"Failed to extract content for: {article.title} - {result.get('error', 'Unknown error')}")
            return {
                "status": "failed",
                "article_id": article_id,
                "error": result.get('error', 'Unknown error')
            }
            
    except Exception as e:
        logger.error(f"Error fetching content for {article.title}: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def curate_articles_task(batch_size: int = None):
    """
    Celery task to curate raw articles using AI.
    
    This task will:
    1. Fetch uncurated ArticleRaw entries
    2. Generate AI summaries (short and detailed)
    3. Create embeddings using OpenAI API
    4. Calculate relevance scores
    5. Generate AI tags
    6. Create ArticleCurated entries
    
    Args:
        batch_size: Number of articles to process (defaults to settings.AI_BATCH_SIZE)
    """
    from django.conf import settings
    from django.db.models import Q
    from .models import ArticleRaw, ArticleCurated, MediaAsset
    from .ai_service import get_ai_service, AIServiceError
    
    start_time = time.time()
    batch_size = batch_size or settings.AI_BATCH_SIZE
    
    logger.info("Starting AI curation task")
    
    # Get uncurated articles
    uncurated_articles = ArticleRaw.objects.filter(
        Q(curated__isnull=True)
    ).select_related('source').prefetch_related('media_assets')[:batch_size]
    
    if not uncurated_articles.exists():
        logger.info("No uncurated articles found")
        return {
            "status": "no_articles",
            "message": "No articles need curation"
        }
    
    logger.info(f"Found {uncurated_articles.count()} articles to curate")
    
    # Initialize AI service
    try:
        ai_service = get_ai_service()
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {str(e)}")
        return {
            "status": "error",
            "message": f"AI service initialization failed: {str(e)}"
        }
    
    articles_processed = 0
    articles_created = 0
    errors = []
    
    for article in uncurated_articles:
        try:
            logger.info(f"Curating article: {article.title[:60]}...")
            
            # Prepare article text (combine available content)
            article_text = article.summary_feed
            if article.raw_html:
                # Use raw_html if available (truncate to reasonable length)
                article_text = article.raw_html[:10000] + " " + article.summary_feed
            
            # Generate summaries
            try:
                summary_short, summary_detailed = ai_service.generate_summaries(
                    article_text, 
                    article.title
                )
            except AIServiceError as e:
                logger.error(f"Failed to generate summaries for {article.id}: {str(e)}")
                # Use fallback summaries
                summary_short = article.title[:500]
                summary_detailed = article.summary_feed[:2000] if article.summary_feed else article.title
            
            # Calculate relevance score
            try:
                relevance_score = ai_service.calculate_relevance_score(
                    article_text,
                    article.title
                )
            except AIServiceError as e:
                logger.error(f"Failed to calculate relevance for {article.id}: {str(e)}")
                relevance_score = 0.5  # Default fallback
            
            # Generate tags
            try:
                ai_tags = ai_service.generate_tags(article_text, article.title)
            except AIServiceError as e:
                logger.error(f"Failed to generate tags for {article.id}: {str(e)}")
                ai_tags = ['ai', 'technology']  # Default fallback
            
            # Generate embeddings
            try:
                embedding = ai_service.generate_embeddings(summary_detailed)
            except AIServiceError as e:
                logger.error(f"Failed to generate embeddings for {article.id}: {str(e)}")
                embedding = [0.0] * 1536  # Zero vector fallback
            
            # Select cover media (first image if available)
            cover_media = None
            media_assets = article.media_assets.filter(type='image').first()
            if media_assets:
                cover_media = media_assets
            else:
                # If no images from RSS, try to extract from HTML content
                if article.raw_html:
                    from .utils import extract_best_image_from_html
                    
                    best_image = extract_best_image_from_html(article.raw_html, article.url)
                    if best_image:
                        # Create MediaAsset for the extracted image
                        media_asset, created = MediaAsset.objects.get_or_create(
                            source_url=best_image['url'],
                            defaults={
                                'type': 'image',
                                'width': best_image.get('width'),
                                'height': best_image.get('height'),
                                'mime_type': 'image/jpeg'  # Default
                            }
                        )
                        # Link to article
                        article.media_assets.add(media_asset)
                        cover_media = media_asset
                        logger.info(f"Extracted cover image from HTML for article {article.id}")
            
            # Create ArticleCurated entry
            with transaction.atomic():
                curated_article = ArticleCurated.objects.create(
                    raw_article=article,
                    relevance_score=relevance_score,
                    summary_short=summary_short,
                    summary_detailed=summary_detailed,
                    ai_tags=ai_tags,
                    cover_media=cover_media,
                    embedding=embedding
                )
            
            articles_created += 1
            articles_processed += 1
            
            logger.info(
                f"Successfully curated article {article.id}: "
                f"relevance={relevance_score:.2f}, tags={len(ai_tags)}"
            )
            
        except Exception as e:
            logger.error(f"Error curating article {article.id}: {str(e)}")
            errors.append({
                'article_id': article.id,
                'title': article.title[:100],
                'error': str(e)
            })
            articles_processed += 1
            continue
    
    execution_time = time.time() - start_time
    
    result = {
        "status": "completed",
        "articles_processed": articles_processed,
        "articles_created": articles_created,
        "errors_count": len(errors),
        "errors": errors[:5],  # Include first 5 errors
        "execution_time_seconds": round(execution_time, 2)
    }
    
    logger.info(
        f"Curation task completed: {articles_created}/{articles_processed} articles curated "
        f"in {execution_time:.2f}s"
    )
    
    # Automatically generate audio segment after curation
    if articles_created > 0:
        try:
            logger.info("Triggering automatic audio segment generation after curation")
            generate_audio_segment_task.delay()
        except Exception as e:
            logger.error(f"Failed to trigger audio generation: {str(e)}")
    
    return result


@shared_task
def generate_audio_segment_task():
    """
    Generate daily audio news segment after article curation.
    
    This task:
    1. Checks if today's audio segment already exists
    2. If not, generates script from top 8 articles
    3. Converts script to audio using OpenAI TTS
    4. Saves audio file and metadata to database
    """
    from django.conf import settings
    from datetime import date
    import os
    from .models import ArticleCurated, AudioSegment
    from .ai_service import get_ai_service
    
    logger.info("Starting audio segment generation task")
    start_time = time.time()
    today = date.today()
    
    try:
        # Check if today's audio already exists
        existing_segment = AudioSegment.objects.filter(date=today).first()
        if existing_segment:
            logger.info(f"Audio segment for {today} already exists, skipping generation")
            return {
                "status": "skipped",
                "message": "Audio segment already exists for today",
                "date": str(today)
            }
        
        # Fetch top 8 articles by relevance score
        top_articles = ArticleCurated.objects.select_related(
            'raw_article',
            'raw_article__source'
        ).order_by('-relevance_score')[:8]
        
        if not top_articles:
            logger.warning("No curated articles available for audio generation")
            return {
                "status": "error",
                "message": "No curated articles available"
            }
        
        logger.info(f"Found {top_articles.count()} articles for audio segment")
        
        # Build articles context
        articles_context = []
        article_ids = []
        for article in top_articles:
            articles_context.append({
                'title': article.raw_article.title,
                'source_name': article.raw_article.source.name,
                'summary_short': article.summary_short,
                'summary_detailed': article.summary_detailed,
                'url': article.raw_article.url
            })
            article_ids.append(article.id)
        
        # Initialize AI service
        ai_service = get_ai_service()
        
        # Generate news script
        logger.info("Generating news script...")
        script_text = ai_service.generate_news_script(articles_context)
        logger.info(f"Script generated: {len(script_text)} characters")
        
        # Create media directory if doesn't exist
        audio_dir = os.path.join(settings.MEDIA_ROOT, 'audio_segments')
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generate audio file
        filename = f"{today.isoformat()}.mp3"
        audio_path = os.path.join(audio_dir, filename)
        
        logger.info(f"Generating audio file: {filename}")
        ai_service.generate_audio_from_script(script_text, audio_path)
        
        # Calculate approximate duration
        word_count = len(script_text) / 5
        duration_seconds = int((word_count / 150) * 60)
        
        # Save to database
        audio_segment = AudioSegment.objects.create(
            date=today,
            audio_file=f"audio_segments/{filename}",
            script_text=script_text,
            article_ids=article_ids,
            duration_seconds=duration_seconds
        )
        
        execution_time = time.time() - start_time
        
        logger.info(
            f"Audio segment generated successfully: {filename} "
            f"({duration_seconds}s duration, {execution_time:.2f}s generation time)"
        )
        
        return {
            "status": "success",
            "date": str(today),
            "filename": filename,
            "article_count": len(article_ids),
            "duration_seconds": duration_seconds,
            "execution_time": round(execution_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Failed to generate audio segment: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@shared_task
def test_task(message):
    """Simple test task to verify Celery is working."""
    logger.info(f"Test task executed with message: {message}")
    return f"Task completed: {message}"

