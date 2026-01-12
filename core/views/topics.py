from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from core.models import TopicCategory
from core.serializers import TopicCategorySerializer


class TopicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Browse available topics"""
    permission_classes = [AllowAny]
    queryset = TopicCategory.objects.filter(is_active=True)
    serializer_class = TopicCategorySerializer
    lookup_field = 'slug'
