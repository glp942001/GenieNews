from django.db import models
from pgvector.django import VectorField


class Source(models.Model):
    """RSS/Atom feed source for news articles."""
    name = models.CharField(max_length=255)
    feed_url = models.URLField(unique=True)
    site_url = models.URLField()
    active = models.BooleanField(default=True)
    
    # Feed ingestion tracking
    last_fetched_at = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    error_count = models.IntegerField(default=0)
    fetch_interval_minutes = models.IntegerField(default=10080)  # Weekly (7*24*60)
    max_articles_per_fetch = models.IntegerField(default=50)
    requires_javascript = models.BooleanField(default=False)
    custom_headers = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ArticleRaw(models.Model):
    """Raw article data from RSS feed."""
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    summary_feed = models.TextField()
    raw_html = models.TextField(blank=True, null=True)
    media_assets = models.ManyToManyField('MediaAsset', blank=True, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['url']),
        ]


class MediaAsset(models.Model):
    """Media assets (images, videos) associated with articles."""
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    source_url = models.URLField()
    proxy_url = models.URLField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type}: {self.source_url}"

    class Meta:
        ordering = ['-id']


class ArticleCurated(models.Model):
    """AI-curated and enhanced article with embeddings."""
    raw_article = models.OneToOneField(
        ArticleRaw, 
        on_delete=models.CASCADE, 
        related_name='curated'
    )
    relevance_score = models.FloatField(blank=True, null=True)
    summary_short = models.TextField(max_length=500)
    summary_detailed = models.TextField()
    ai_tags = models.JSONField(default=list)
    cover_media = models.ForeignKey(
        MediaAsset, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='curated_articles'
    )
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.raw_article.title

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['relevance_score']),
        ]


class UserInteraction(models.Model):
    """Track user interactions with articles."""
    ACTION_CHOICES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('bookmark', 'Bookmark'),
    ]
    
    user_id = models.CharField(max_length=255)
    article = models.ForeignKey(
        ArticleCurated, 
        on_delete=models.CASCADE, 
        related_name='interactions'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.action} - {self.article.raw_article.title}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user_id', '-timestamp']),
            models.Index(fields=['article', '-timestamp']),
        ]


class FeedIngestionLog(models.Model):
    """Track feed ingestion attempts and results."""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
    ]
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='ingestion_logs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    articles_found = models.IntegerField(default=0)
    articles_created = models.IntegerField(default=0)
    articles_updated = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    execution_time_seconds = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.source.name} - {self.status} - {self.started_at}"

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['source', '-started_at']),
            models.Index(fields=['status']),
        ]
