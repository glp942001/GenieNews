from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Source, ArticleRaw, MediaAsset, ArticleCurated, UserInteraction, FeedIngestionLog


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'feed_url', 'active', 'last_fetched_at', 'error_count', 'created_at']
    list_filter = ['active', 'requires_javascript', 'created_at', 'last_fetched_at']
    search_fields = ['name', 'feed_url', 'site_url']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'feed_url', 'site_url', 'active')
        }),
        ('Ingestion Settings', {
            'fields': ('fetch_interval_minutes', 'max_articles_per_fetch', 'requires_javascript', 'custom_headers')
        }),
        ('Status', {
            'fields': ('last_fetched_at', 'last_error', 'error_count')
        }),
    )


@admin.register(ArticleRaw)
class ArticleRawAdmin(admin.ModelAdmin):
    list_display = ['title_short', 'source', 'is_curated', 'published_at', 'created_at']
    list_filter = ['source', 'published_at', 'created_at']
    search_fields = ['title', 'url', 'summary_feed']
    date_hierarchy = 'published_at'
    actions = ['curate_selected_articles']
    
    def title_short(self, obj):
        """Display truncated title."""
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    title_short.short_description = 'Title'
    
    def is_curated(self, obj):
        """Show if article has been curated."""
        try:
            if hasattr(obj, 'curated') and obj.curated:
                return format_html('<span style="color: green;">✓ Curated</span>')
            return format_html('<span style="color: orange;">⧗ Pending</span>')
        except:
            return format_html('<span style="color: orange;">⧗ Pending</span>')
    is_curated.short_description = 'Status'
    
    def curate_selected_articles(self, request, queryset):
        """Admin action to manually trigger curation for selected articles."""
        from .tasks import curate_articles_task
        
        # Filter only uncurated articles
        uncurated = []
        for article in queryset:
            try:
                if not hasattr(article, 'curated') or not article.curated:
                    uncurated.append(article.id)
            except:
                uncurated.append(article.id)
        
        if uncurated:
            # Trigger curation task
            curate_articles_task.delay(batch_size=len(uncurated))
            self.message_user(
                request, 
                f"Curation task queued for {len(uncurated)} article(s)."
            )
        else:
            self.message_user(
                request,
                "All selected articles are already curated.",
                level='warning'
            )
    curate_selected_articles.short_description = "Curate selected articles with AI"


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ['type', 'source_url', 'width', 'height', 'mime_type']
    list_filter = ['type', 'mime_type']
    search_fields = ['source_url', 'proxy_url']


@admin.register(ArticleCurated)
class ArticleCuratedAdmin(admin.ModelAdmin):
    list_display = ['article_title', 'relevance_score_colored', 'tags_display', 'has_cover', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['raw_article__title', 'summary_short', 'summary_detailed', 'ai_tags']
    raw_id_fields = ['raw_article', 'cover_media']
    date_hierarchy = 'created_at'
    readonly_fields = ['summary_preview', 'tags_display', 'embedding_info']
    
    fieldsets = (
        ('Article Info', {
            'fields': ('raw_article', 'cover_media')
        }),
        ('AI-Generated Content', {
            'fields': ('summary_short', 'summary_detailed', 'summary_preview')
        }),
        ('AI Analysis', {
            'fields': ('relevance_score', 'ai_tags', 'tags_display')
        }),
        ('Technical', {
            'fields': ('embedding_info',),
            'classes': ('collapse',)
        }),
    )
    
    def article_title(self, obj):
        """Display article title with link to raw article."""
        title = obj.raw_article.title[:60]
        if len(obj.raw_article.title) > 60:
            title += '...'
        url = reverse('admin:news_articleraw_change', args=[obj.raw_article.id])
        return format_html('<a href="{}">{}</a>', url, title)
    article_title.short_description = 'Article'
    
    def relevance_score_colored(self, obj):
        """Display relevance score with color coding."""
        if obj.relevance_score is None:
            return '-'
        score = obj.relevance_score
        if score >= 0.7:
            color = 'green'
        elif score >= 0.4:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color, score
        )
    relevance_score_colored.short_description = 'Relevance'
    relevance_score_colored.admin_order_field = 'relevance_score'
    
    def tags_display(self, obj):
        """Display AI tags as badges."""
        if not obj.ai_tags:
            return '-'
        tags_html = ' '.join([
            f'<span style="background-color: #e3f2fd; padding: 3px 8px; '
            f'border-radius: 3px; margin: 2px; display: inline-block; '
            f'font-size: 11px;">{tag}</span>'
            for tag in obj.ai_tags[:8]
        ])
        return format_html(tags_html)
    tags_display.short_description = 'AI Tags'
    
    def has_cover(self, obj):
        """Show if article has cover media."""
        if obj.cover_media:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">-</span>')
    has_cover.short_description = 'Cover'
    
    def summary_preview(self, obj):
        """Display preview of summaries."""
        return format_html(
            '<div style="margin-bottom: 10px;">'
            '<strong>Short:</strong><br/><div style="padding: 10px; background: #f5f5f5; '
            'border-radius: 4px; margin: 5px 0;">{}</div>'
            '<strong>Detailed (preview):</strong><br/><div style="padding: 10px; '
            'background: #f5f5f5; border-radius: 4px; margin: 5px 0;">{}</div>'
            '</div>',
            obj.summary_short,
            obj.summary_detailed[:300] + '...' if len(obj.summary_detailed) > 300 else obj.summary_detailed
        )
    summary_preview.short_description = 'Summary Preview'
    
    def embedding_info(self, obj):
        """Display embedding information."""
        if obj.embedding:
            dim = len(obj.embedding) if isinstance(obj.embedding, list) else 'N/A'
            return format_html(
                '<div>Embedding dimension: {}<br/>Vector stored: ✓</div>',
                dim
            )
        return 'No embedding generated'
    embedding_info.short_description = 'Embedding Info'


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'article', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user_id', 'article__raw_article__title']
    raw_id_fields = ['article']
    date_hierarchy = 'timestamp'


@admin.register(FeedIngestionLog)
class FeedIngestionLogAdmin(admin.ModelAdmin):
    list_display = ['source', 'status', 'articles_found', 'articles_created', 'started_at', 'execution_time_seconds']
    list_filter = ['status', 'started_at', 'source']
    search_fields = ['source__name', 'error_message']
    raw_id_fields = ['source']
    date_hierarchy = 'started_at'
    readonly_fields = ['started_at', 'completed_at', 'execution_time_seconds']
