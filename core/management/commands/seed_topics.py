from django.core.management.base import BaseCommand

from core.models import TopicCategory


class Command(BaseCommand):
    help = 'Seed initial topic categories'

    def handle(self, *args, **kwargs):
        topics = [
            {
                'name': 'Animals',
                'slug': 'animals',
                'icon': '🦁',
                'description': 'Learn about wildlife, pets, and creatures from around the world',
                'recommended_min_age': 3,
                'context_guidelines': 'Focus on fun facts, habitats, and behaviors. Keep language simple and wonder-filled. Avoid scary predator details for younger kids.'
            },
            {
                'name': 'Space',
                'slug': 'space',
                'icon': '🚀',
                'description': 'Explore planets, stars, astronauts, and the universe',
                'recommended_min_age': 5,
                'context_guidelines': 'Explain cosmic concepts with relatable comparisons. Encourage curiosity about exploration. Make the vastness feel exciting, not scary.'
            },
            {
                'name': 'How Things Work',
                'slug': 'how-things-work',
                'icon': '⚙️',
                'description': 'Discover how everyday objects and machines function',
                'recommended_min_age': 6,
                'context_guidelines': 'Break down mechanisms into simple steps. Use analogies kids understand. Encourage "taking things apart" thinking safely.'
            },
            {
                'name': 'Weather',
                'slug': 'weather',
                'icon': '🌦️',
                'description': 'Understand rain, snow, storms, seasons, and climate',
                'recommended_min_age': 4,
                'context_guidelines': 'Explain weather phenomena clearly without creating fear of storms. Focus on the science and beauty of nature.'
            },
            {
                'name': 'Science Experiments',
                'slug': 'science',
                'icon': '🔬',
                'description': 'Learn about chemistry, physics, and fun experiments',
                'recommended_min_age': 7,
                'context_guidelines': 'Suggest safe, parent-supervised experiments. Explain the "why" behind reactions. Encourage scientific thinking.'
            },
            {
                'name': 'History',
                'slug': 'history',
                'icon': '📜',
                'description': 'Explore past civilizations, inventions, and historical events',
                'recommended_min_age': 8,
                'context_guidelines': 'Focus on interesting stories and achievements. Age-appropriate handling of difficult topics. Emphasize learning from the past.'
            },
            {
                'name': 'Ocean Life',
                'slug': 'ocean',
                'icon': '🐠',
                'description': 'Dive into marine biology and underwater ecosystems',
                'recommended_min_age': 5,
                'context_guidelines': 'Make the ocean feel magical and worth protecting. Explain ecosystems simply. Balance wonder with conservation.'
            },
            {
                'name': 'Human Body',
                'slug': 'human-body',
                'icon': '🫀',
                'description': 'Understand how our bodies work and stay healthy',
                'recommended_min_age': 6,
                'context_guidelines': 'Use accurate but age-appropriate terminology. Focus on health and wellness. Keep it positive and empowering.'
            },
        ]

        for topic_data in topics:
            topic, created = TopicCategory.objects.get_or_create(
                slug=topic_data['slug'],
                defaults=topic_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created topic: {topic.name}')
                )
            else:
                self.stdout.write(f'Topic already exists: {topic.name}')
