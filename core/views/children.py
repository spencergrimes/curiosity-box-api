from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Child, TopicCategory, ChildTopicAccess
from core.serializers import ChildSerializer, QuestionSerializer


class ChildViewSet(viewsets.ReadOnlyModelViewSet):
    """View and manage children"""
    queryset = Child.objects.prefetch_related(
        'topic_access__topic'  # Optimize enabled_topics serializer field
    )
    serializer_class = ChildSerializer

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get all questions for a child"""
        child = self.get_object()
        questions = child.questions.select_related('child', 'detected_topic').all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='topics/enable')
    def enable_topic(self, request, pk=None):
        """Enable a topic for this child"""
        child = self.get_object()
        topic_slug = request.data.get('topic_slug')

        try:
            topic = TopicCategory.objects.get(slug=topic_slug, is_active=True)
            access, created = ChildTopicAccess.objects.get_or_create(
                child=child,
                topic=topic
            )
            return Response({
                'message': f'Topic "{topic.name}" enabled for {child.name}',
                'created': created
            })
        except TopicCategory.DoesNotExist:
            return Response(
                {'error': 'Topic not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='topics/disable')
    def disable_topic(self, request, pk=None):
        """Disable a topic for this child"""
        child = self.get_object()
        topic_slug = request.data.get('topic_slug')

        deleted_count, _ = ChildTopicAccess.objects.filter(
            child=child,
            topic__slug=topic_slug
        ).delete()

        return Response({
            'message': f'Topic access removed',
            'deleted': deleted_count > 0
        })
