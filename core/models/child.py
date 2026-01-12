from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .family import Family


class Child(models.Model):
    """Child profile"""
    READING_LEVELS = [
        ('early', 'Early Reader (5-7)'),
        ('intermediate', 'Intermediate (8-10)'),
        ('advanced', 'Advanced (11+)'),
    ]

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='children'
    )
    name = models.CharField(max_length=50)
    age = models.IntegerField(
        validators=[MinValueValidator(3), MaxValueValidator(18)]
    )
    reading_level = models.CharField(
        max_length=20,
        choices=READING_LEVELS,
        default='intermediate'
    )
    avatar_color = models.CharField(
        max_length=7,
        default='#4A90E2'
    )  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Children"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (age {self.age})"

    def can_ask_about(self, topic_slug):
        """Check if child has access to topic"""
        return self.topic_access.filter(
            topic__slug=topic_slug,
            topic__is_active=True
        ).exists()
