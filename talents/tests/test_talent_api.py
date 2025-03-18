from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from talents.models import Talent
from users.models import User


class TalentAPITest(APITestCase):
    def setUp(self):

        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", username="testuser"
        )
        self.talent = Talent.objects.create(
            user=self.user,
            title="Software Developer",
            bio="Experienced developer",
            skills="Python, Django, React",
            pricing="150",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_talent_list(self):
        """Test getting talent list"""

        url = reverse("talent_route_noparam")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["payload"]), 1)

    def test_get_talent_detail(self):
        """Test getting talent detail"""

        def process_response(response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["title"], self.talent.title)
            self.assertIn("badge", response.data)
            self.assertIn("avatar", response.data)
            self.assertNotIn("id", response.data)
            self.assertNotIn("password", response.data)
            self.assertIn("public_id", response.data)

        url = reverse("talent_route", kwargs={"public_id": self.talent.public_id})
        response = self.client.get(url)
        process_response(response)

        mini_response = self.client.get(f"{url}?s_type=mini")
        process_response(mini_response)

        detail_response = self.client.get(f"{url}?s_type=detail")
        process_response(detail_response)
        self.assertIn("updated_at", detail_response.data)
        self.assertIn("date_joined", detail_response.data)

    def test_post_talent(self):
        """Test creating new talent"""

        url = reverse("talent_route_noparam")
        data = {
            "email": "new@example.com",
            "password": "newpass123",
            "username": "newuser",
            "title": "New Developer",
            "bio": "New bio",
            "skills": "New skills",
            "pricing": "200",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Talent.objects.count(), 2)
        self.assertNotIn("id", response.data)
        self.assertNotIn("password", response.data)
        self.assertIn("public_id", response.data)
        self.assertIn("avatar", response.data)
        self.assertIn("date_joined", response.data)

    def test_put_talent(self):
        """Test updating talent"""

        url = reverse("talent_route", kwargs={"public_id": self.talent.public_id})
        data = {
            "bio": "Updated bio",
            "title": "Updated Developer",
            "skills": "Python, Django, React, Javascript",
        }
        response = self.client.put(f"{url}?s_type=detail", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.talent.refresh_from_db()
        self.assertEqual(self.talent.title, data["title"])
        self.assertEqual(self.talent.skills, data["skills"])

    def test_delete_talent(self):
        """Test soft deleting talent"""

        self.assertIsNone(self.talent.deleted_at)

        url = reverse("talent_route", kwargs={"public_id": self.talent.public_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.talent.refresh_from_db()
        self.assertIsNotNone(self.talent.deleted_at)

    def test_unauthorized_access(self):
        """Test unauthorized access to talent detail"""

        self.client.force_authenticate(user=None)
        url = reverse("talent_route", kwargs={"public_id": self.talent.public_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_other_user_talent(self):
        """Test updating other user's talent"""

        self.client.force_authenticate(user=self.user)

        other_user = User.objects.create_user(
            email="other@example.com", password="otherpass123", username="otheruser"
        )
        other_talent = Talent.objects.create(user=other_user)
        url = reverse("talent_route", kwargs={"public_id": other_talent.public_id})
        data = {"title": "Unauthorized Update"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
