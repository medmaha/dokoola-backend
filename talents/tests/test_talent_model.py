from django.core.exceptions import ValidationError
from django.test import TestCase

from reviews.models import Review
from talents.models import Talent
from users.models import User


class TalentModelTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", username="testuser"
        )
        self.talent_data = {
            "user": self.user,
            "title": "Software Developer",
            "bio": "Experienced developer",
            "skills": "Python, Django, React",
            "pricing": "150",
            "bits": 100,
            "badge": "premium",
        }
        self.talent = Talent.objects.create(**self.talent_data)
        self.user.refresh_from_db()

    def test_talent_creation(self):
        """Test talent instance creation"""

        self.assertTrue(isinstance(self.talent, Talent))
        self.assertTrue(self.talent.public_id.startswith("tal"))

    def test_user_fields(self):
        """Test talent instance creation"""

        self.assertTrue(self.user.is_talent)
        self.assertEqual(self.user.public_id, self.talent.public_id)

    def test_talent_fields(self):
        """Test talent field values"""

        self.assertEqual(self.talent.title, self.talent_data["title"])
        self.assertEqual(self.talent.bio, self.talent_data["bio"])
        self.assertEqual(self.talent.skills, self.talent_data["skills"])
        self.assertEqual(self.talent.pricing, self.talent_data["pricing"])
        self.assertEqual(self.talent.bits, self.talent_data["bits"])
        self.assertEqual(self.talent.badge, self.talent_data["badge"])
        self.assertEqual(self.talent.jobs_completed, 0)

    def test_talent_properties(self):
        """Test talent property methods"""
        self.assertEqual(self.talent.name, self.user.name)
        self.assertEqual(self.talent.email, self.user.email)

    def test_average_rating(self):
        """Test average rating calculation"""

        # Test default rating
        self.assertEqual(self.talent.average_rating(), 3.6)

        review_user = User.objects.create_user(
            email="review@example.com", password="reviewpass123", username="reviewuser"
        )
        # Create and add reviews
        review1 = Review.objects.create(rating=5, author=review_user)
        review2 = Review.objects.create(rating=4, author=review_user)
        self.talent.reviews.add(review1, review2)

        # Test calculated average
        self.assertEqual(self.talent.average_rating(), 4.5)
