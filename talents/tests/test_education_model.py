from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from talents.models import Education, Talent
from users.models import User


class EducationModelTest(TestCase):
    def setUp(self):
        self.education_data = {
            "degree": "Bachelor of Science",
            "institution": "Test University",
            "location": "Test City",
            "start_date": date(2020, 1, 1),
            "end_date": date(2024, 1, 1),
            "achievements": "Test achievements",
            "published": False,
        }
        self.education = Education.objects.create(**self.education_data)

    def test_create_education(self):
        education = Education.objects.create(**self.education_data)
        self.assertIsNotNone(education.public_id)
        self.assertEqual(education.degree, self.education_data["degree"])
        self.assertEqual(education.institution, self.education_data["institution"])

    def test_certificate_fields(self):
        """Test certificate field values"""
        self.assertTrue("ed" in self.education.public_id)
        self.assertEqual(self.education.degree, self.education_data["degree"])
        self.assertEqual(self.education.institution, self.education_data["institution"])
        self.assertEqual(self.education.location, self.education_data["location"])
        self.assertEqual(self.education.start_date, self.education_data["start_date"])
        self.assertEqual(self.education.end_date, self.education_data["end_date"])
        self.assertFalse(self.education.published)  # Default value should be False

    def test_education_str_method(self):
        education = Education.objects.create(**self.education_data)
        name_strnig = (
            self.education_data["degree"]
            + " | "
            + self.education_data["institution"][:25]
        )
        self.assertEqual(str(education), name_strnig)

    def test_education_dates_validation(self):
        self.education_data["start_date"] = date(2024, 1, 1)
        self.education_data["end_date"] = date(2020, 1, 1)
        education = Education(**self.education_data)
        with self.assertRaises(ValidationError):
            education.full_clean()
