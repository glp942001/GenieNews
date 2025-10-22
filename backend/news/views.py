from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from datetime import date

from .models import ArticleCurated, UserInteraction, AudioSegment
from .serializers import (
    ArticleCuratedListSerializer,
    ArticleCuratedDetailSerializer,
    UserInteractionSerializer,
    StructuredSummarySerializer,
    ChatMessageSerializer,
    ChatResponseSerializer,
    AudioSegmentSerializer
)
from .ai_service import get_ai_service


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


class ArticleSummaryView(APIView):
    """
    Generate structured AI summary for a specific article.
    POST /api/chat/summary/<article_id>/
    """
    
    def post(self, request, article_id):
        """Generate structured summary for an article."""
        try:
            # Fetch the article
            article = get_object_or_404(
                ArticleCurated.objects.select_related('raw_article', 'raw_article__source'),
                id=article_id
            )
            
            # Prepare article data for AI service
            article_data = {
                'title': article.raw_article.title,
                'summary_short': article.summary_short,
                'summary_detailed': article.summary_detailed,
                'url': article.raw_article.url,
                'source': article.raw_article.source.name
            }
            
            # Generate structured summary using AI service
            ai_service = get_ai_service()
            structured_data = ai_service.generate_structured_summary(article_data)
            
            # Build response - ensure sections contains the keypoints array directly
            response_data = {
                'article_id': article.id,
                'title': article.raw_article.title,
                'source': article.raw_article.source.name,
                'url': article.raw_article.url,
                'sections': structured_data,  # This should contain {keypoints: [...]}
                'timestamp': timezone.now()
            }
            
            serializer = StructuredSummarySerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate summary: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatConversationView(APIView):
    """
    Handle conversational AI chat with context from top articles.
    POST /api/chat/message/
    """
    
    def post(self, request):
        """Process chat message and return AI response."""
        serializer = ChatMessageSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_message = serializer.validated_data['message']
            conversation_history = serializer.validated_data.get('history', [])
            
            # Fetch top 8 articles for context
            top_articles = ArticleCurated.objects.select_related(
                'raw_article',
                'raw_article__source'
            ).order_by('-relevance_score')[:8]
            
            # Build articles context
            articles_context = []
            for article in top_articles:
                articles_context.append({
                    'title': article.raw_article.title,
                    'source_name': article.raw_article.source.name,
                    'summary_short': article.summary_short,
                    'summary_detailed': article.summary_detailed,
                    'url': article.raw_article.url
                })
            
            # Generate AI response
            ai_service = get_ai_service()
            ai_response = ai_service.chat_with_context(
                user_message=user_message,
                articles_context=articles_context,
                conversation_history=conversation_history
            )
            
            # Build response
            response_data = {
                'response': ai_response,
                'timestamp': timezone.now()
            }
            
            response_serializer = ChatResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate chat response: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GenerateAudioSegmentView(APIView):
    """
    Retrieve the latest audio news segment.
    GET /api/audio/daily-segment/
    
    Note: Audio segments are automatically generated weekly during article curation.
    This endpoint only retrieves existing segments, it does not generate new ones.
    """
    
    def get(self, request):
        """Return the latest audio segment."""
        try:
            # Get the most recent audio segment
            latest_segment = AudioSegment.objects.order_by('-date').first()
            
            if not latest_segment:
                return Response({
                    'success': False,
                    'error': 'No audio segments available yet. Please wait for the weekly curation to complete.',
                    'segment': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Return the latest audio segment
            serializer = AudioSegmentSerializer(latest_segment, context={'request': request})
            return Response({
                'success': True,
                'segment': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to retrieve audio segment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
