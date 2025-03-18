import time
from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Certificate


class CertificateModelTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.certificate_data = {
            "name": "Test Certificate",
            "organization": "Test Organization",
            "url": "https://example.com/cert",
            "date_issued": date(2023, 1, 1),
            "file_url": "https://example.com/cert.pdf",
        }
        self.certificate = Certificate.objects.create(**self.certificate_data)

    def test_certificate_creation(self):
        """Test certificate instance creation"""
        self.assertTrue(isinstance(self.certificate, Certificate))
        self.assertEqual(str(self.certificate), self.certificate_data["name"])

    def test_certificate_fields(self):
        """Test certificate field values"""
        self.assertEqual(self.certificate.name, self.certificate_data["name"])
        self.assertEqual(
            self.certificate.organization, self.certificate_data["organization"]
        )
        self.assertEqual(self.certificate.url, self.certificate_data["url"])
        self.assertEqual(
            self.certificate.date_issued, self.certificate_data["date_issued"]
        )
        self.assertEqual(self.certificate.file_url, self.certificate_data["file_url"])
        self.assertFalse(self.certificate.published)  # Default value should be False

    def test_public_id_generation(self):
        """Test if public_id is generated correctly"""
        self.assertIsNotNone(self.certificate.public_id)
        self.assertTrue(self.certificate.public_id.startswith("ce"))

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

    def test_required_fields(self):
        """Test required fields validation"""
        required_fields = ["organization", "url", "date_issued"]

        for field in required_fields:
            data = self.certificate_data.copy()
            data[field] = ""

            certificate = Certificate(**data)
            with self.assertRaises(ValidationError):
                certificate.full_clean()

    def test_timestamps(self):
        """Test if timestamps are automatically set"""
        self.assertIsNotNone(self.certificate.created_at)
        self.assertIsNotNone(self.certificate.updated_at)

        # Store the original organization & timestamp
        original_org = self.certificate.organization
        original_updated_at = self.certificate.updated_at

        # Update the certificate
        self.certificate.organization = "Updated Organization"

        time.sleep(0.01)
        self.certificate.save()

        # Refresh from database
        self.certificate.refresh_from_db()

        # Compare timestamps and updated organization
        self.assertNotEqual(self.certificate.organization, original_org)
        self.assertGreater(self.certificate.updated_at, original_updated_at)
