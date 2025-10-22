from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticleCuratedViewSet, 
    UserInteractionViewSet,
    ArticleSummaryView,
    ChatConversationView,
    GenerateAudioSegmentView
)

router = DefaultRouter()
router.register(r'articles', ArticleCuratedViewSet, basename='article')
router.register(r'interactions', UserInteractionViewSet, basename='interaction')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/summary/<int:article_id>/', ArticleSummaryView.as_view(), name='article-summary'),
    path('chat/message/', ChatConversationView.as_view(), name='chat-message'),
    path('audio/daily-segment/', GenerateAudioSegmentView.as_view(), name='daily-audio-segment'),
]

