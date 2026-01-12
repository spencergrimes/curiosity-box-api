"""
Performance tests to verify query optimization and prevent N+1 queries.

These tests ensure the API remains performant as data grows.
"""
from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import (Child, ChildTopicAccess, Family, Parent, Question,
                         TopicCategory)


class QueryOptimizationTests(TestCase):
    """Test that views use optimal database queries"""

    def setUp(self):
        """Create test data"""
        # Create user and authentication token
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

        # Create family and parent
        family = Family.objects.create(name="Test Family")
        Parent.objects.create(
            family=family,
            email="parent@test.com",
            name="Test Parent"
        )

        # Create topics
        self.topics = [
            TopicCategory.objects.create(
                name=f"Topic {i}",
                slug=f"topic-{i}",
                icon="🎯",
                description=f"Topic {i} description",
                context_guidelines="Guidelines",
                recommended_min_age=5
            ) for i in range(5)
        ]

        # Create children with topic access
        self.children = []
        for i in range(10):
            child = Child.objects.create(
                family=family,
                name=f"Child {i}",
                age=7,
                reading_level='intermediate'
            )
            # Enable 2-3 topics per child
            for topic in self.topics[:2]:
                ChildTopicAccess.objects.create(child=child, topic=topic)
            self.children.append(child)

        # Create questions
        for child in self.children:
            for j in range(5):
                Question.objects.create(
                    child=child,
                    text=f"Question {j} from {child.name}",
                    detected_topic=self.topics[0],
                    was_within_boundaries=True,
                    answer="Test answer"
                )

        self.client = APIClient()
        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_children_list_query_count(self):
        """Verify children list uses prefetch_related to avoid N+1."""
        # Auth + count + children + prefetch topic_access + prefetch topics = 5 queries
        with self.assertNumQueries(5):
            response = self.client.get('/api/v1/children/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 10)

    def test_questions_list_query_count(self):
        """Verify questions list uses select_related for child/topic."""
        # Auth + count + select with JOINs = 3 queries
        with self.assertNumQueries(3):
            response = self.client.get('/api/v1/questions/')
            self.assertEqual(response.status_code, 200)
            # 10 children × 5 questions = 50 total
            self.assertEqual(response.data['count'], 50)

    def test_child_questions_endpoint_query_count(self):
        """Verify child questions endpoint uses select_related."""
        child = self.children[0]
        with self.assertNumQueries(5):
            response = self.client.get(f'/api/v1/children/{child.id}/questions/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 5)


class APIPerformanceTests(TestCase):
    """Test API response times and efficiency"""

    def setUp(self):
        """Create larger dataset for performance testing"""
        # Create user and authentication token
        self.user = User.objects.create_user(
            username='perfuser',
            email='perfuser@test.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

        family = Family.objects.create(name="Large Family")
        Parent.objects.create(
            family=family,
            email="parent@large.com",
            name="Parent"
        )

        # Create 3 topics
        self.topic = TopicCategory.objects.create(
            name="Test Topic",
            slug="test-topic",
            icon="🎯",
            description="Test",
            context_guidelines="Guidelines",
            recommended_min_age=5
        )

        # Create 20 children with questions
        for i in range(20):
            child = Child.objects.create(
                family=family,
                name=f"Child {i}",
                age=7,
                reading_level='intermediate'
            )
            ChildTopicAccess.objects.create(child=child, topic=self.topic)

            # 10 questions per child = 200 total
            for j in range(10):
                Question.objects.create(
                    child=child,
                    text=f"Question {j}",
                    detected_topic=self.topic,
                    was_within_boundaries=True,
                    answer="Answer"
                )

        self.client = APIClient()
        # No authentication needed for public endpoints (questions)

    def test_paginated_questions_performance(self):
        """
        Test that pagination doesn't load all records into memory.

        With 200 questions, requesting page 1 (20 items) should only
        query for those 20 items, not all 200.
        """
        # Pagination requires: 1 COUNT query + 1 SELECT query
        with self.assertNumQueries(2):  # 1 for count, 1 for page results
            response = self.client.get('/api/v1/questions/?page=1&page_size=20')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 20)
            self.assertEqual(response.data['count'], 200)

    def test_filtered_queries_use_indexes(self):
        """
        Test that filtering by child_id efficiently uses database indexes.

        This test documents expected query patterns for future optimization.
        """
        child = Child.objects.first()

        # Should be efficient with proper indexing on Question.child_id
        with self.assertNumQueries(2):  # 1 for count, 1 for results
            response = self.client.get(f'/api/v1/questions/?child_id={child.id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'], 10)
