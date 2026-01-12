from django.contrib import admin

from .models import (Child, ChildTopicAccess, Family, Parent, Question,
                     TopicCategory)


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'family', 'created_at']
    list_filter = ['family']
    search_fields = ['name', 'email']

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'reading_level', 'family', 'created_at']
    list_filter = ['reading_level', 'family']
    search_fields = ['name']

@admin.register(TopicCategory)
class TopicCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'slug', 'recommended_min_age', 'is_active']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ChildTopicAccess)
class ChildTopicAccessAdmin(admin.ModelAdmin):
    list_display = ['child', 'topic', 'enabled_at']
    list_filter = ['topic', 'child__family']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['child', 'text_preview', 'detected_topic', 'was_within_boundaries', 'created_at']
    list_filter = ['was_within_boundaries', 'detected_topic', 'child__family']
    search_fields = ['text', 'answer']
    readonly_fields = ['created_at', 'response_generated_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question'
