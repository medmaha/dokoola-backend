from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from talents.models import Education, Talent
from users.models import User


class TalentEducationAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test user and talent
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", username="testuser"
        )
        self.talent = Talent.objects.create(user=self.user)

        # Create test education
        self.education = Education.objects.create(
            degree="Test Degree",
            institution="Test Institution",
            location="Test Location",
            start_date=date(2020, 1, 1),
            end_date=date(2024, 1, 1),
            achievements="Test Achievements",
            published=True,
        )
        self.talent.education.add(self.education)
        # Authenticate user
        self.client.force_authenticate(user=self.user)

    def test_get_education(self):
        """Test to get all educations for"""
        url = reverse("talent_education_route", args=[self.talent.public_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["degree"], "Test Degree")

    def test_post_education(self):
        """ " Test that a new education can be created"""

        data = {
            "degree": "Bachelor of Science",
            "institution": "Test University",
            "location": "Test City",
            "start_date": "2019-01-01",
            "end_date": "2023-01-01",
            "achievements": "Notable achievements",
            "published": True,
        }

        url = reverse("talent_education_route", args=[self.talent.public_id])
        response = self.client.post(url, data)
        self.assertEqual(2, Education.objects.count())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("public_id", None))
        self.assertEqual(response.data["degree"], data["degree"])

    def test_put_education(self):
        """Test that the education can be updated"""

        url = reverse("talent_education_route", args=[self.talent.public_id])

        data = {
            "degree": "Updated Degree",
            "institution": "Updated Institution",
            "location": "Updated Location",
            "end_date": "2024-01-01",  # this should be greather than the start-date
            "published": False,
            "public_id": self.education.public_id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["degree"], "Updated Degree")

    def test_delete_education(self):
        """Test that the education can be deleted"""

        url = reverse("talent_education_route", args=[self.talent.public_id])
        data = {
            "public_id": self.education.public_id,
        }
        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Education.objects.filter(id=self.education.id).exists())

    def test_create_education_max_limit(self):
        """Test that the maximum number of educations can be created"""

        # Create max allowed educations
        for i in range(3):
            education = Education.objects.create(
                degree=f"Degree {i}",
                institution=f"Institution {i}",
                location=f"Location {i}",
                start_date=date(2020, 1, 1),
                end_date=date(2024, 1, 1),
                achievements=f"Achievements {i}",
            )
            # Assign education to talent
            self.talent.education.add(education)

        # Try to create one more education
        data = {
            "degree": "Extra Degree",
            "institution": "Extra Institution",
            "location": "Extra Location",
            "start_date": "2019-01-01",
            "end_date": "2023-01-01",
            "achievements": "Extra achievements",
        }
        url = reverse("talent_education_route", args=[self.talent.public_id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Maximum number of educations reached", response.data["message"])

    def test_updating_other_users_education(self):
        """Make sure that only the owner of the education can update it"""

        new_talent = get_other_talent()
        self.client.force_authenticate(user=new_talent.user)

        # Attempt to update the self.talent education
        url = reverse("talent_education_route", args=[self.talent.public_id])
        response = self.client.put(
            url,
            {
                "degree": "Updated Education Degree",
                "public_id": self.education.public_id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the API"""

        self.client.force_authenticate(user=None)
        url = reverse("talent_education_route", args=[self.talent.public_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_published_education(self):
        """Verify education visibility rules"""

        education_1 = Education.objects.create(
            **{
                "degree": "New Degree 1",
                "institution": "Test Institution 1",
                "location": "Test Location 1",
                "start_date": "2011-01-01",
                "end_date": "2021-01-01",
                "published": True,
            }
        )
        education_2 = Education.objects.create(
            **{
                "degree": "New Degree 2",
                "institution": "Test Institution 2",
                "location": "Test Location 2",
                "start_date": "2012-01-01",
                "end_date": "2022-01-01",
            }
        )  # Published = False

        new_talent = get_other_talent()
        url = reverse(
            "talent_education_route", kwargs={"public_id": new_talent.public_id}
        )

        # Assing both educations to the new_talent
        new_talent.education.set([education_1, education_2])

        # See if new_talent can list all educations dispite publish status
        self.client.force_authenticate(new_talent.user)
        response_1 = self.client.get(url)
        response_data_1: List[dict] = response_1.data  # type: ignore
        self.assertEqual(len(response_data_1), 2)

        # Make sure other-users only access published educations
        self.client.force_authenticate(self.user)
        response_2 = self.client.get(url)
        response_data_2: List[dict] = response_2.data  # type: ignore
        self.assertEqual(len(response_data_2), 1)
        self.assertEqual(response_data_2[0].get("published"), True)
        self.assertEqual(response_data_2[0].get("degree"), education_1.degree)
        self.assertEqual(response_data_2[0].get("public_id"), education_1.public_id)

    # Failure tests
    def test_invalid_data_creation(self):
        """Test that invalid data cannot be created"""

        data = {
            "degree": "",  # Required field
            "institution": "Test Institution",
            "location": "Test Location",
            "start_date": "2019-01-01",
            "end_date": "2023-01-01",
        }

        url = reverse("talent_education_route", args=[self.talent.public_id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)

        education = Education.objects.create(
            degree="Test Degree",
            institution="Test Institution",
            location="Test Location",
            start_date=date(2020, 1, 1),
            end_date=date(2024, 1, 1),
            achievements="Test Achievements",
        )
        education.degree = "Updated Degree"
        education.save()
        self.assertEqual(
            Education.objects.get(id=education.id).degree, "Updated Degree"
        )


def get_other_talent():
    """
    Helper function to create test talent account
    - email: `otheruser@example.com`
    - username: `otheruser`
    - password: `otherpassword` Note the password is `hashed`
    """
    other_user = User.objects.create_user(
        email="otheruser@example.com",
        password="otherpassword",
        username="otherusername",
    )
    other_talent = Talent.objects.create(user=other_user)
    return other_talent
