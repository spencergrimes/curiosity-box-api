from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from core.models import Child, ChildTopicAccess, Family, Parent, Question, TopicCategory


class APIEndpointTests(APITestCase):
    """Tests for API endpoints"""

    def setUp(self):
        """Create test data"""
        self.client = APIClient()

        # Create authenticated user
        self.user = User.objects.create_user(
            username="parent@test.com", email="parent@test.com", password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)

        # Create family and parent
        self.family = Family.objects.create(name="Test Family")
        self.parent = Parent.objects.create(
            email="parent@test.com", name="Test Parent", family=self.family
        )

        # Create child
        self.child = Child.objects.create(
            family=self.family, name="Test Child", age=8, reading_level="intermediate"
        )

        # Create topics
        self.animals_topic = TopicCategory.objects.create(
            name="Animals",
            slug="animals",
            description="Learn about animals",
            icon="🦁",
            recommended_min_age=3,
            context_guidelines="Focus on fun facts",
        )

    def test_list_topics_public(self):
        """Test that topics can be listed without authentication"""
        response = self.client.get("/api/topics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_children_requires_auth(self):
        """Test that listing children requires authentication"""
        response = self.client.get("/api/children/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_children_with_auth(self):
        """Test listing children with authentication"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get("/api/children/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enable_topic_for_child(self):
        """Test enabling a topic for a child"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post(
            f"/api/children/{self.child.id}/topics/enable/",
            {"topic_slug": "animals"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.child.can_ask_about("animals"))

    def test_disable_topic_for_child(self):
        """Test disabling a topic for a child"""
        # First enable it
        ChildTopicAccess.objects.create(child=self.child, topic=self.animals_topic)

        # Then disable it
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post(
            f"/api/children/{self.child.id}/topics/disable/",
            {"topic_slug": "animals"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.child.can_ask_about("animals"))

    @patch("core.services.question_service.QuestionService.generate_answer")
    def test_ask_question_endpoint(self, mock_generate):
        """Test asking a question via API"""
        # Give child access to topic
        ChildTopicAccess.objects.create(child=self.child, topic=self.animals_topic)

        mock_generate.return_value = "Lions roar to communicate."

        data = {"child_id": self.child.id, "question": "Why do lions roar?"}
        response = self.client.post("/api/questions/ask/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("question", response.data)
        self.assertIn("within_boundaries", response.data)
        self.assertTrue(response.data["within_boundaries"])

    def test_mark_question_helpful(self):
        """Test marking a question as helpful"""
        question = Question.objects.create(
            child=self.child,
            text="Why do lions roar?",
            answer="Lions roar to communicate.",
        )

        response = self.client.post(
            f"/api/questions/{question.id}/mark_helpful/",
            {"helpful": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        question.refresh_from_db()
        self.assertTrue(question.child_marked_helpful)

    def test_get_child_questions(self):
        """Test getting questions for a specific child"""
        Question.objects.create(child=self.child, text="Question 1", answer="Answer 1")
        Question.objects.create(child=self.child, text="Question 2", answer="Answer 2")

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(f"/api/children/{self.child.id}/questions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
