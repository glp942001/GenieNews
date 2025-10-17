from rest_framework import serializers
from .models import Source, ArticleRaw, MediaAsset, ArticleCurated, UserInteraction


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name', 'feed_url', 'site_url', 'active', 'created_at']


class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ['id', 'type', 'source_url', 'proxy_url', 'width', 'height', 'mime_type']


class ArticleRawSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)

    class Meta:
        model = ArticleRaw
        fields = ['id', 'source', 'title', 'url', 'published_at', 'summary_feed', 'created_at']


class ArticleCuratedListSerializer(serializers.ModelSerializer):
    """Serializer for article list view (summary)."""
    source_name = serializers.CharField(source='raw_article.source.name', read_only=True)
    title = serializers.CharField(source='raw_article.title', read_only=True)
    url = serializers.CharField(source='raw_article.url', read_only=True)
    published_at = serializers.DateTimeField(source='raw_article.published_at', read_only=True)
    cover_media = MediaAssetSerializer(read_only=True)

    class Meta:
        model = ArticleCurated
        fields = [
            'id',
            'title',
            'url',
            'source_name',
            'published_at',
            'relevance_score',
            'summary_short',
            'ai_tags',
            'cover_media',
            'created_at',
        ]


class ArticleCuratedDetailSerializer(serializers.ModelSerializer):
    """Serializer for article detail view (full content)."""
    raw_article = ArticleRawSerializer(read_only=True)
    cover_media = MediaAssetSerializer(read_only=True)

    class Meta:
        model = ArticleCurated
        fields = [
            'id',
            'raw_article',
            'relevance_score',
            'summary_short',
            'summary_detailed',
            'ai_tags',
            'cover_media',
            'created_at',
            'updated_at',
        ]


class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = ['id', 'user_id', 'article', 'action', 'timestamp']

