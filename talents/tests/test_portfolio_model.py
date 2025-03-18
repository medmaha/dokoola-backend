import time

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from talents.models import Portfolio


class PortfolioModelTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.portfolio_data = {
            "name": "Test Portfolio",
            "description": "A test portfolio description",
            "url": "https://example.com/portfolio",
            "image": "https://example.com/image.jpg",
        }
        self.portfolio = Portfolio.objects.create(**self.portfolio_data)

    def test_portfolio_creation(self):
        """Test portfolio instance creation"""
        self.assertTrue(isinstance(self.portfolio, Portfolio))
        self.assertEqual(str(self.portfolio), self.portfolio_data["name"])

    def test_portfolio_fields(self):
        """Test portfolio field values"""
        self.assertEqual(self.portfolio.name, self.portfolio_data["name"])
        self.assertEqual(self.portfolio.description, self.portfolio_data["description"])
        self.assertEqual(self.portfolio.url, self.portfolio_data["url"])
        self.assertEqual(self.portfolio.image, self.portfolio_data["image"])
        self.assertTrue(self.portfolio.published)  # Default value should be True

    def test_public_id_generation(self):
        """Test if public_id is generated correctly"""
        self.assertIsNotNone(self.portfolio.public_id)
        self.assertTrue(self.portfolio.public_id.startswith("po"))

    def test_portfolio_name_max_length(self):
        """Test name field max length validation"""
        portfolio = Portfolio(
            name="a" * 201,  # Exceeds max_length of 200
            description="Test description",
            url="https://example.com",
            image="https://example.com/image.jpg",
        )
        with self.assertRaises(ValidationError):
            portfolio.full_clean()

    def test_required_fields(self):
        """Test required fields validation"""
        required_fields = ["name", "description", "url", "image"]

        for field in required_fields:
            data = self.portfolio_data.copy()
            data[field] = ""

            portfolio = Portfolio(**data)
            with self.assertRaises(ValidationError):
                portfolio.full_clean()

    # def test_url_validation(self):
    #     """Test URL field validation"""
    #     invalid_urls = [
    #         'not-a-url',
    #         'ftp://invalid-scheme.com',
    #         'http:/missing-slash.com'
    #     ]

    #     for invalid_url in invalid_urls:
    #         portfolio = Portfolio(
    #             name='Test Portfolio',
    #             description='Test description',
    #             url=invalid_url,
    #             image='https://example.com/image.jpg'
    #         )
    #         with self.assertRaises(ValidationError):
    #             portfolio.full_clean()

    def test_timestamps(self):
        """Test if timestamps are automatically set"""
        self.assertIsNotNone(self.portfolio.created_at)
        self.assertIsNotNone(self.portfolio.updated_at)
        # Store the original name & timestamp
        original_name = self.portfolio.name
        original_updated_at = self.portfolio.updated_at
        # Update the portfolio
        self.portfolio.name = "Updated Name"
        time.sleep(0.03)
        self.portfolio.save()
        # Refresh from database to get the new timestamp
        self.portfolio.refresh_from_db()
        # Compare timestamps and updated name
        self.assertNotEqual(self.portfolio.name, original_name)
        self.assertGreater(self.portfolio.updated_at, original_updated_at)
