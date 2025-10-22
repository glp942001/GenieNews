from rest_framework import serializers
from .models import Source, ArticleRaw, MediaAsset, ArticleCurated, UserInteraction, AudioSegment


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name', 'feed_url', 'site_url', 'active', 'created_at']


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='source_url', read_only=True)
    
    class Meta:
        model = MediaAsset
        fields = ['id', 'type', 'url', 'source_url', 'proxy_url', 'width', 'height', 'mime_type']


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
            'summary_detailed',  # Added detailed summary for rich excerpts
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


class StructuredSummarySerializer(serializers.Serializer):
    """Serializer for structured article summaries."""
    article_id = serializers.IntegerField()
    title = serializers.CharField()
    source = serializers.CharField()
    url = serializers.URLField()
    sections = serializers.DictField()  # Allow any dict structure
    timestamp = serializers.DateTimeField()


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for chat message requests and responses."""
    message = serializers.CharField(max_length=2000, required=True)
    history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    def validate_history(self, value):
        """Validate conversation history format."""
        for msg in value:
            if 'role' not in msg or 'content' not in msg:
                raise serializers.ValidationError(
                    "Each history item must have 'role' and 'content' fields"
                )
            if msg['role'] not in ['user', 'assistant']:
                raise serializers.ValidationError(
                    "Role must be either 'user' or 'assistant'"
                )
        return value


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat AI responses."""
    response = serializers.CharField()
    timestamp = serializers.DateTimeField()


class AudioSegmentSerializer(serializers.ModelSerializer):
    """Serializer for daily audio news segments."""
    audio_url = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AudioSegment
        fields = ['id', 'date', 'audio_url', 'script_text', 'article_count', 'duration_seconds', 'created_at']
    
    def get_audio_url(self, obj):
        """Return full URL for audio file."""
        if obj.audio_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None
    
    def get_article_count(self, obj):
        """Return count of articles in this segment."""
        return len(obj.article_ids) if obj.article_ids else 0

