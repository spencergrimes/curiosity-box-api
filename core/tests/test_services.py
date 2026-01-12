from django.test import TestCase
from unittest.mock import patch, MagicMock
from core.models import Family, Child, TopicCategory, ChildTopicAccess, Question
from core.services import QuestionService


class QuestionServiceTests(TestCase):
    """Tests for QuestionService business logic"""

    def setUp(self):
        """Create test data"""
        self.family = Family.objects.create(name="Test Family")
        self.child = Child.objects.create(
            family=self.family,
            name="Test Child",
            age=8,
            reading_level="intermediate"
        )
        self.animals_topic = TopicCategory.objects.create(
            name="Animals",
            slug="animals",
            description="Learn about animals",
            icon="🦁",
            recommended_min_age=3,
            context_guidelines="Focus on fun facts"
        )
        self.space_topic = TopicCategory.objects.create(
            name="Space",
            slug="space",
            description="Learn about space",
            icon="🚀",
            recommended_min_age=5,
            context_guidelines="Explain cosmic concepts"
        )
        self.service = QuestionService()

    def test_detect_topic_animals(self):
        """Test topic detection for animals"""
        topic = self.service.detect_topic("Why do lions roar?")
        self.assertEqual(topic, self.animals_topic)

    def test_detect_topic_space(self):
        """Test topic detection for space"""
        topic = self.service.detect_topic("How big is the moon?")
        self.assertEqual(topic, self.space_topic)

    def test_detect_topic_no_match(self):
        """Test topic detection when no match found"""
        topic = self.service.detect_topic("Random unrelated question")
        self.assertIsNone(topic)

    @patch('core.services.question_service.Anthropic')
    def test_generate_answer_success(self, mock_anthropic):
        """Test successful answer generation"""
        # Mock the API response
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Lions roar to communicate with their pride.")]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        # Create question
        question = Question.objects.create(
            child=self.child,
            text="Why do lions roar?",
            detected_topic=self.animals_topic,
            was_within_boundaries=True
        )

        # Generate answer
        service = QuestionService()
        answer = service.generate_answer(question)

        # Verify
        self.assertEqual(answer, "Lions roar to communicate with their pride.")
        question.refresh_from_db()
        self.assertEqual(question.answer, "Lions roar to communicate with their pride.")
        self.assertIsNotNone(question.response_generated_at)

    @patch('core.services.question_service.Anthropic')
    def test_generate_answer_api_error(self, mock_anthropic):
        """Test answer generation when API fails"""
        # Mock API error
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client

        # Create question
        question = Question.objects.create(
            child=self.child,
            text="Why do lions roar?",
            detected_topic=self.animals_topic,
            was_within_boundaries=True
        )

        # Generate answer
        service = QuestionService()
        answer = service.generate_answer(question)

        # Verify error message is saved
        self.assertIn("trouble answering", answer)
        question.refresh_from_db()
        self.assertIn("trouble answering", question.answer)

    def test_process_question_within_boundaries(self):
        """Test processing question within approved topic"""
        # Give child access to animals topic
        ChildTopicAccess.objects.create(
            child=self.child,
            topic=self.animals_topic
        )

        with patch.object(QuestionService, 'generate_answer') as mock_generate:
            mock_generate.return_value = "Lions roar to communicate."
            question, within_boundaries = self.service.process_question(
                self.child,
                "Why do lions roar?"
            )

        self.assertTrue(within_boundaries)
        self.assertEqual(question.detected_topic, self.animals_topic)
        self.assertTrue(question.was_within_boundaries)

    def test_process_question_outside_boundaries(self):
        """Test processing question outside approved topics"""
        # Don't give child access to space topic
        question, within_boundaries = self.service.process_question(
            self.child,
            "How big is the moon?"
        )

        self.assertFalse(within_boundaries)
        self.assertEqual(question.detected_topic, self.space_topic)
        self.assertFalse(question.was_within_boundaries)
        self.assertIn("I can't help you", question.answer)

    def test_process_question_outside_boundaries_with_allowed_topics(self):
        """Test that denied question suggests allowed topics"""
        # Give child access to animals topic only
        ChildTopicAccess.objects.create(
            child=self.child,
            topic=self.animals_topic
        )

        # Try to ask about space (not allowed)
        question, within_boundaries = self.service.process_question(
            self.child,
            "How big is the moon?"
        )

        # Verify question was denied
        self.assertFalse(within_boundaries)
        self.assertEqual(question.detected_topic, self.space_topic)
        self.assertFalse(question.was_within_boundaries)

        # Verify response suggests allowed topics
        self.assertIn("Instead, you can ask me about:", question.answer)
        self.assertIn("Animals", question.answer)
        self.assertIn("🦁", question.answer)

        # Verify NO answer was generated (no Claude API call)
        self.assertIsNone(question.response_generated_at)

    def test_process_question_outside_boundaries_no_allowed_topics(self):
        """Test denied question when child has no allowed topics"""
        # Don't give child access to any topics
        question, within_boundaries = self.service.process_question(
            self.child,
            "How big is the moon?"
        )

        # Verify question was denied
        self.assertFalse(within_boundaries)
        self.assertFalse(question.was_within_boundaries)

        # Verify response tells them to ask parent to unlock topics
        self.assertIn("don't have any topics unlocked yet", question.answer)
        self.assertIn("Ask your parent to unlock some topics", question.answer)

    def test_get_allowed_topics_message_with_topics(self):
        """Test generating allowed topics message"""
        # Give child access to multiple topics
        ChildTopicAccess.objects.create(child=self.child, topic=self.animals_topic)
        ChildTopicAccess.objects.create(child=self.child, topic=self.space_topic)

        message = self.service.get_allowed_topics_message(self.child)

        # Verify message includes both topics
        self.assertIn("Instead, you can ask me about:", message)
        self.assertIn("Animals", message)
        self.assertIn("Space", message)
        self.assertIn("🦁", message)
        self.assertIn("🚀", message)

    def test_get_allowed_topics_message_no_topics(self):
        """Test generating message when no topics are allowed"""
        # Don't give child any topic access
        message = self.service.get_allowed_topics_message(self.child)

        # Verify message tells them to ask parent
        self.assertIn("don't have any topics unlocked yet", message)
        self.assertIn("Ask your parent", message)

    def test_question_outside_boundaries_not_answered_by_ai(self):
        """Verify that questions outside boundaries are NOT sent to Claude API"""
        # This test ensures we don't waste API calls on denied questions
        with patch.object(QuestionService, 'generate_answer') as mock_generate:
            # Try to ask about space (not allowed)
            question, within_boundaries = self.service.process_question(
                self.child,
                "How big is the moon?"
            )

            # Verify generate_answer was NEVER called
            mock_generate.assert_not_called()

            # Verify question has an answer anyway (the denial message)
            self.assertIsNotNone(question.answer)
            self.assertIn("I can't help you", question.answer)
