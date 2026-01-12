from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from core.models import Child, Question
from core.serializers import QuestionSerializer, AskQuestionSerializer
from core.services import QuestionService
from core.throttles import AIQuestionRateThrottle


class QuestionViewSet(viewsets.ModelViewSet):
    """Ask and view questions"""
    permission_classes = [AllowAny]
    queryset = Question.objects.select_related('child', 'detected_topic')
    serializer_class = QuestionSerializer

    def get_queryset(self):
        """Optionally filter by child"""
        queryset = super().get_queryset()
        child_id = self.request.query_params.get('child_id')
        if child_id:
            queryset = queryset.filter(child_id=child_id)
        return queryset

    @action(detail=False, methods=['post'], throttle_classes=[AIQuestionRateThrottle])
    def ask(self, request):
        """
        Main endpoint: child asks a question.

        Rate limited to 20 requests per minute per child to:
        - Prevent abuse
        - Control Anthropic API costs
        - Ensure fair usage across children
        """
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        child_id = serializer.validated_data['child_id']
        question_text = serializer.validated_data['question']

        # Get child
        child = get_object_or_404(Child, id=child_id)

        # Process question through service
        service = QuestionService()
        question, within_boundaries = service.process_question(child, question_text)

        # Return response
        response_serializer = QuestionSerializer(question)
        return Response({
            'question': response_serializer.data,
            'within_boundaries': within_boundaries
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Child marks answer as helpful/not helpful"""
        question = self.get_object()
        helpful = request.data.get('helpful', True)
        question.child_marked_helpful = helpful
        question.save()
        return Response({'message': 'Feedback recorded'})
