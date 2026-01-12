from rest_framework import serializers

from core.models import Child, TopicCategory

from .topic import ChildTopicAccessSerializer, TopicCategorySerializer


class ChildSerializer(serializers.ModelSerializer):
    topic_access = ChildTopicAccessSerializer(many=True, read_only=True)
    enabled_topics = serializers.SerializerMethodField()

    class Meta:
        model = Child
        fields = ['id', 'name', 'age', 'reading_level', 'avatar_color',
                  'topic_access', 'enabled_topics']

    def get_enabled_topics(self, obj):
        """
        Get enabled topics using prefetched data to avoid N+1 queries.

        This relies on the view prefetching 'topic_access__topic'.
        """
        # Use prefetched topic_access.topic instead of making new queries
        topics = [
            access.topic
            for access in obj.topic_access.all()
            if access.topic.is_active
        ]
        return TopicCategorySerializer(topics, many=True).data
