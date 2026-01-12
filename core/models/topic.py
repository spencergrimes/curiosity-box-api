from django.db import models
from .child import Child


class TopicCategory(models.Model):
    """Pre-defined safe learning categories"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='📚')
    recommended_min_age = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)

    # For AI prompt engineering
    context_guidelines = models.TextField(
        help_text="How Claude should approach questions in this category"
    )

    class Meta:
        verbose_name_plural = "Topic Categories"
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"


class ChildTopicAccess(models.Model):
    """Which topics each child can explore"""
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='topic_access'
    )
    topic = models.ForeignKey(
        TopicCategory,
        on_delete=models.CASCADE,
        related_name='child_access'
    )
    enabled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['child', 'topic']
        verbose_name_plural = "Child Topic Access"

    def __str__(self):
        return f"{self.child.name} → {self.topic.name}"
