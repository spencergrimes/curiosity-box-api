import os
import logging
from anthropic import Anthropic
from django.utils import timezone
from core.models import TopicCategory, Question

logger = logging.getLogger(__name__)


class QuestionService:
    """Handles question processing and AI integration"""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def detect_topic(self, question_text):
        """Simple keyword-based topic detection (MVP version)"""
        # TODO: Replace with ML-based classification for better accuracy
        question_lower = question_text.lower()
        
        # Get all active topics
        topics = TopicCategory.objects.filter(is_active=True)
        
        # Simple keyword matching (enhance later with AI)
        topic_keywords = {
            'animals': ['animal', 'dog', 'cat', 'lion', 'tiger', 'bird', 'fish', 'pet', 'zoo', 'wild'],
            'space': ['space', 'planet', 'star', 'moon', 'sun', 'astronaut', 'rocket', 'galaxy', 'mars'],
            'how-things-work': ['work', 'how does', 'why does', 'machine', 'engine', 'computer', 'phone'],
            'weather': ['weather', 'rain', 'snow', 'storm', 'wind', 'cloud', 'thunder', 'lightning', 'season'],
            'science': ['science', 'experiment', 'chemical', 'reaction', 'physics', 'chemistry'],
            'history': ['history', 'ancient', 'war', 'president', 'king', 'queen', 'civilization'],
            'ocean': ['ocean', 'sea', 'whale', 'shark', 'dolphin', 'coral', 'beach', 'marine'],
            'human-body': ['body', 'heart', 'brain', 'muscle', 'bone', 'blood', 'health', 'sick'],
        }
        
        for slug, keywords in topic_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                try:
                    return topics.get(slug=slug)
                except TopicCategory.DoesNotExist:
                    continue
        
        return None
    
    def generate_answer(self, question_obj):
        """Generate age-appropriate answer using Claude"""
        child = question_obj.child
        topic = question_obj.detected_topic
        
        # Build system prompt
        system_prompt = f"""You are a friendly, educational AI helping a {child.age}-year-old child learn about the world.

Reading Level: {child.get_reading_level_display()}
Topic: {topic.name if topic else 'General'}

Guidelines:
- Use simple, age-appropriate language
- Be encouraging and positive
- Keep answers concise (2-3 paragraphs max)
- Make learning fun and engaging
- Never include scary or inappropriate content
"""

        if topic:
            system_prompt += f"\n\nTopic-Specific Guidelines:\n{topic.context_guidelines}"
        
        # Call Claude API
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question_obj.text}
                ]
            )
            
            answer = message.content[0].text
            
            # Update question with answer
            question_obj.answer = answer
            question_obj.response_generated_at = timezone.now()
            question_obj.save()
            
            return answer
            
        except Exception as e:
            # Log error and save friendly message
            error_message = "I'm having trouble answering right now. Please try again in a moment!"
            logger.error(
                "Error generating answer from Claude API",
                extra={
                    'error': str(e),
                    'child_id': child.id,
                    'child_age': child.age,
                    'question_id': question_obj.id,
                    'topic': topic.slug if topic else None,
                },
                exc_info=True
            )

            # Save error message to question
            question_obj.answer = error_message
            question_obj.response_generated_at = timezone.now()
            question_obj.save()

            return error_message
    
    def get_allowed_topics_message(self, child):
        """Generate a friendly message listing allowed topics"""
        allowed_topics = TopicCategory.objects.filter(
            child_access__child=child,
            is_active=True
        ).order_by('name')

        if not allowed_topics.exists():
            return "You don't have any topics unlocked yet. Ask your parent to unlock some topics for you!"

        topic_list = ", ".join([f"{topic.icon} {topic.name}" for topic in allowed_topics])
        return f"Instead, you can ask me about: {topic_list}"

    def process_question(self, child, question_text):
        """Main method: detect topic, check boundaries, generate answer"""
        logger.info(
            "Processing question",
            extra={
                'child_id': child.id,
                'child_age': child.age,
                'child_name': child.name,
                'question_length': len(question_text),
            }
        )

        # Detect topic
        detected_topic = self.detect_topic(question_text)

        # Check if child has access to this topic
        if detected_topic and not child.can_ask_about(detected_topic.slug):
            # Question outside boundaries - suggest allowed topics
            allowed_topics = list(
                TopicCategory.objects.filter(
                    child_access__child=child,
                    is_active=True
                ).values_list('slug', flat=True)
            )

            logger.warning(
                "Question outside boundaries",
                extra={
                    'child_id': child.id,
                    'child_age': child.age,
                    'detected_topic': detected_topic.slug,
                    'allowed_topics': allowed_topics,
                }
            )

            allowed_topics_message = self.get_allowed_topics_message(child)

            question = Question.objects.create(
                child=child,
                text=question_text,
                detected_topic=detected_topic,
                was_within_boundaries=False,
                answer=f"That's a great question about {detected_topic.name}! However, I can't help you with that right now. \n\n{allowed_topics_message}"
            )
            return question, False  # False = outside boundaries

        # Create question
        logger.info(
            "Question within boundaries, generating answer",
            extra={
                'child_id': child.id,
                'detected_topic': detected_topic.slug if detected_topic else None,
            }
        )

        question = Question.objects.create(
            child=child,
            text=question_text,
            detected_topic=detected_topic,
            was_within_boundaries=True
        )

        # Generate answer
        self.generate_answer(question)

        return question, True  # True = within boundaries
