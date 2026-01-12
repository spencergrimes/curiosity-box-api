from django.db import models

from .child import Child
from .topic import TopicCategory


class Question(models.Model):
    """Questions asked by children"""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    # Classification
    detected_topic = models.ForeignKey(
        TopicCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
    )
    was_within_boundaries = models.BooleanField(default=True)

    # Response
    answer = models.TextField(null=True, blank=True)
    response_generated_at = models.DateTimeField(null=True, blank=True)

    # Engagement
    child_marked_helpful = models.BooleanField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["child", "-created_at"]),
            models.Index(fields=["detected_topic", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.child.name}: {self.text[:50]}..."
