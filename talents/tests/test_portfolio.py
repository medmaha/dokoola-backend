from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from talents.models import Portfolio, Talent
from users.models import User


class TalentPortfolioAPITestCase(APITestCase):

    def setUp(self):
        client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            username="testusername",
        )
        self.talent = Talent.objects.create(user=self.user)
        self.portfolio = Portfolio.objects.create(
            name="Test Portfolio",
            description="Test Description",
            url="http://example.com",
            image="http://example.com/image.jpg",
        )
        self.talent.portfolio.set([self.portfolio])
        self.client = client
        self.client.force_authenticate(user=self.user)

    def test_get_portfolio(self):
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})
        response = self.client.get(url)
        response_data: List[dict] = response.data  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 1)
        first_item = response_data[0]
        self.assertTrue(first_item["published"])
        self.assertIsNotNone(first_item.get("public_id"))
        self.assertEqual(first_item["name"], self.portfolio.name)

    def test_post_portfolio(self):
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})
        data = {
            "name": "New Portfolio",
            "description": "New Description",
            "url": "http://example.com/new",
            "image": "http://example.com/new_image.jpg",
        }
        response = self.client.post(url, data, format="json")
        response_data: dict = response.data  # type: ignore

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Portfolio.objects.count(), 2)
        self.assertTrue(response_data["published"])
        self.assertIsNotNone(response_data.get("public_id"))
        self.assertEqual(response_data["name"], data.get("name"))

    def test_put_portfolio(self):
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})
        data = {
            "published": False,
            "name": "Updated Portfolio",
            "public_id": self.portfolio.public_id,
        }
        response = self.client.put(url, data, format="json")
        response_data: dict = response.data  # type: ignore

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("published"), False)
        self.assertEqual(response_data.get("name"), data.get("name"))
        self.assertEqual(response_data.get("public_id"), self.portfolio.public_id)
        self.assertNotEqual(response_data.get("name"), self.portfolio.public_id)
        self.assertNotEqual(response_data.get("published"), self.portfolio.published)

        self.portfolio.refresh_from_db()

    def test_delete_portfolio(self):
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})

        data = {"public_id": self.portfolio.public_id}

        count = Portfolio.objects.count()

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Portfolio.objects.count(), count - 1)

        response = self.client.get(url, data, format="json")
        response_data = response.data  # type: ignore

        for item in response_data:
            self.assertNotEqual(self.portfolio.public_id, item.get("public_id"))

    # Failure tests
    def test_get_portfolio_unauthorized(self):
        self.client.force_authenticate(user=None)  # type: ignore
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_portfolio_invalid_data(self):
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})
        data = {
            "name": "New Test",
            "description": "New Description",
            "url": "http://example.com/new",
            "image": "http://example.com/new_image.jpg",
        }

        for index, entry in enumerate(data.items()):
            key, value = entry

            if index == 0:
                value = ""
            if index == 1:
                value = ""
            if index == 2:
                value = ""
            if index == 3:
                value = ""

            _data = data.copy()
            _data[key] = value

            # try creating with invalid data! all fields are required
            response = self.client.post(url, _data, format="json")
            response_data: dict = response.data  # type: ignore
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIsInstance(response_data, dict)
            self.assertIn("message", response_data)
            self.assertIn("blank", response_data.get("message", "").lower())
            self.assertIn(key.lower(), response_data.get("message", "").lower())

    def test_put_portfolio_other_user(self):
        other_talent = get_other_talent()
        url = reverse("portfolio_route", kwargs={"public_id": other_talent.public_id})

        data = {
            "published": False,
            "name": "Updated Portfolio",
            "public_id": self.portfolio.public_id,
        }
        response = self.client.delete(url, data, format="json")
        response_data: dict = response.data  # type: ignore
        self.assertIsNotNone(response_data.get("message"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_portfolio_non_existent(self):
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})
        data = {
            "published": False,
            "name": "Updated Portfolio",
            "public_id": "non_existent_public_id",
        }
        response = self.client.delete(url, data, format="json")
        response_data: dict = response.data  # type: ignore
        self.assertIsNotNone(response_data.get("message"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_portfolio_non_existent(self):
        url = reverse("portfolio_route", kwargs={"public_id": self.talent.public_id})
        data = {"public_id": "non_existent_public_id"}
        response = self.client.delete(url, data, format="json")
        response_data: dict = response.data  # type: ignore
        self.assertIsNotNone(response_data.get("message"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_portfolio_other_user(self):
        other_talent = get_other_talent()
        url = reverse("portfolio_route", kwargs={"public_id": other_talent.public_id})

        data = {"public_id": self.portfolio.public_id}
        response = self.client.delete(url, data, format="json")
        response_data: dict = response.data  # type: ignore
        self.assertIsNotNone(response_data.get("message"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


def get_other_talent():
    """
    Create a new talent account for every test_case
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
