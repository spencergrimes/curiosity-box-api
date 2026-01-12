from django.db import models


class Family(models.Model):
    """Container for parent(s) and children"""
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Families"

    def __str__(self):
        return self.name


class Parent(models.Model):
    """Parent user account"""
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='parents'
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
