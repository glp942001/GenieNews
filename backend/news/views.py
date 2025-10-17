from rest_framework import viewsets, filters
from .models import ArticleCurated, UserInteraction
from .serializers import (
    ArticleCuratedListSerializer,
    ArticleCuratedDetailSerializer,
    UserInteractionSerializer
)


class ArticleCuratedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing curated articles.
    
    list: Returns paginated list of curated articles with summary info
    retrieve: Returns full article details
    """
    queryset = ArticleCurated.objects.select_related(
        'raw_article', 
        'raw_article__source',
        'cover_media'
    ).all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'relevance_score', 'raw_article__published_at']
    ordering = ['-raw_article__published_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleCuratedDetailSerializer
        return ArticleCuratedListSerializer


class UserInteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking user interactions with articles.
    """
    queryset = UserInteraction.objects.select_related(
        'article',
        'article__raw_article'
    ).all()
    serializer_class = UserInteractionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
