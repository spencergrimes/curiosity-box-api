from rest_framework import serializers

from core.models import ChildTopicAccess, TopicCategory


class TopicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "recommended_min_age",
            "is_active",
        ]


class ChildTopicAccessSerializer(serializers.ModelSerializer):
    topic = TopicCategorySerializer(read_only=True)

    class Meta:
        model = ChildTopicAccess
        fields = ["id", "topic", "enabled_at"]
