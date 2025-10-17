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
        
        return {
            "status": "success",
            "source_name": source.name,
            "articles_found": len(entries),
            "articles_created": articles_created,
            "articles_updated": articles_updated,
            "execution_time": time.time() - start_time
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
def curate_articles_task():
    """
    Celery task to curate raw articles using AI.
    
    This task will:
    1. Fetch uncurated ArticleRaw entries
    2. Generate AI summaries (short and detailed)
    3. Create embeddings using OpenAI/similar API
    4. Calculate relevance scores
    5. Generate AI tags
    6. Create ArticleCurated entries
    
    TODO: Implement AI curation logic
    - Integrate with OpenAI API or similar
    - Generate embeddings for vector similarity search
    - Implement relevance scoring algorithm
    - Schedule this task to run after ingestion
    """
    logger.info("curate_articles_task called - implementation pending")
    # Implementation coming soon
    pass


@shared_task
def test_task(message):
    """Simple test task to verify Celery is working."""
    logger.info(f"Test task executed with message: {message}")
    return f"Task completed: {message}"

