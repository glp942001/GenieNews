from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleCuratedViewSet, UserInteractionViewSet

router = DefaultRouter()
router.register(r'articles', ArticleCuratedViewSet, basename='article')
router.register(r'interactions', UserInteractionViewSet, basename='interaction')

urlpatterns = [
    path('', include(router.urls)),
]

