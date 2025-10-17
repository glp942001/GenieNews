from django.contrib import admin
from .models import Source, ArticleRaw, MediaAsset, ArticleCurated, UserInteraction


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'feed_url', 'active', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['name', 'feed_url', 'site_url']


@admin.register(ArticleRaw)
class ArticleRawAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'published_at', 'created_at']
    list_filter = ['source', 'published_at', 'created_at']
    search_fields = ['title', 'url', 'summary_feed']
    date_hierarchy = 'published_at'


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ['type', 'source_url', 'width', 'height', 'mime_type']
    list_filter = ['type', 'mime_type']
    search_fields = ['source_url', 'proxy_url']


@admin.register(ArticleCurated)
class ArticleCuratedAdmin(admin.ModelAdmin):
    list_display = ['raw_article', 'relevance_score', 'cover_media', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['raw_article__title', 'summary_short', 'summary_detailed']
    raw_id_fields = ['raw_article', 'cover_media']
    date_hierarchy = 'created_at'


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'article', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user_id', 'article__raw_article__title']
    raw_id_fields = ['article']
    date_hierarchy = 'timestamp'
