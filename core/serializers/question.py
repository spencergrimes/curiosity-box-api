from rest_framework import serializers

from core.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.name', read_only=True)
    topic_name = serializers.CharField(source='detected_topic.name', read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'child_name', 'text', 'topic_name',
                  'detected_topic', 'was_within_boundaries',
                  'answer', 'child_marked_helpful', 'created_at']
        read_only_fields = ['detected_topic', 'was_within_boundaries',
                            'answer', 'created_at']


class AskQuestionSerializer(serializers.Serializer):
    child_id = serializers.IntegerField()
    question = serializers.CharField(max_length=500)
