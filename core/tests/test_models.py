from django.test import TestCase

from core.models import (Child, ChildTopicAccess, Family, Parent, Question,
                         TopicCategory)


class ModelTests(TestCase):
    """Tests for database models"""

    def setUp(self):
        """Create test data"""
        self.family = Family.objects.create(name="Test Family")
        self.parent = Parent.objects.create(
            family=self.family,
            email="parent@test.com",
            name="Test Parent"
        )
        self.child = Child.objects.create(
            family=self.family,
            name="Test Child",
            age=8,
            reading_level="intermediate"
        )
        self.topic = TopicCategory.objects.create(
            name="Animals",
            slug="animals",
            description="Learn about animals",
            icon="🦁",
            recommended_min_age=3,
            context_guidelines="Focus on fun facts"
        )

    def test_family_creation(self):
        """Test family model creation"""
        self.assertEqual(str(self.family), "Test Family")
        self.assertIsNotNone(self.family.created_at)

    def test_parent_creation(self):
        """Test parent model creation"""
        self.assertEqual(str(self.parent), "Test Parent (parent@test.com)")
        self.assertEqual(self.parent.family, self.family)

    def test_child_creation(self):
        """Test child model creation"""
        self.assertEqual(str(self.child), "Test Child (age 8)")
        self.assertEqual(self.child.reading_level, "intermediate")
        self.assertEqual(self.child.age, 8)

    def test_child_age_validation(self):
        """Test child age validators"""
        # This should work
        child = Child(family=self.family, name="Young", age=5)
        child.full_clean()  # Should not raise

    def test_topic_category_creation(self):
        """Test topic category creation"""
        self.assertEqual(str(self.topic), "🦁 Animals")
        self.assertEqual(self.topic.slug, "animals")
        self.assertTrue(self.topic.is_active)

    def test_child_topic_access(self):
        """Test child topic access relationship"""
        access = ChildTopicAccess.objects.create(
            child=self.child,
            topic=self.topic
        )
        self.assertEqual(str(access), "Test Child → Animals")
        self.assertTrue(self.child.can_ask_about("animals"))

    def test_child_cannot_ask_about_unapproved_topic(self):
        """Test that child cannot ask about topics without access"""
        self.assertFalse(self.child.can_ask_about("space"))

    def test_question_creation(self):
        """Test question model creation"""
        question = Question.objects.create(
            child=self.child,
            text="Why do lions roar?",
            detected_topic=self.topic,
            was_within_boundaries=True,
            answer="Lions roar to communicate!"
        )
        self.assertIn("Why do lions roar?", str(question))
        self.assertEqual(question.child, self.child)
        self.assertEqual(question.detected_topic, self.topic)

    def test_question_ordering(self):
        """Test that questions are ordered by creation date (newest first)"""
        q1 = Question.objects.create(
            child=self.child,
            text="First question"
        )
        q2 = Question.objects.create(
            child=self.child,
            text="Second question"
        )
        questions = Question.objects.all()
        self.assertEqual(questions[0], q2)  # Newest first
        self.assertEqual(questions[1], q1)
