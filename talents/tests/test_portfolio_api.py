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
        """Verify GET portfolios endpoint"""

        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )
        response = self.client.get(url)
        response_data: List[dict] = response.data  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 1)
        first_item = response_data[0]
        self.assertTrue(first_item["published"])
        self.assertIsNotNone(first_item.get("public_id"))
        self.assertEqual(first_item["name"], self.portfolio.name)

    def test_post_portfolio(self):
        """Verify POST portfolio creation"""

        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )
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
        """Verify PUT portfolio update"""

        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )
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
        """Verify DELETE portfolio removal"""

        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )

        data = {"public_id": self.portfolio.public_id}

        count = Portfolio.objects.count()

        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Portfolio.objects.count(), count - 1)

    def test_published_portfolio(self):
        """Verify portfolio visibility rules"""

        portfolio_1 = Portfolio.objects.create(
            name="New Portfolio 1",
            description="New Description 1",
            url="http://example1.com",
            image="http://example1.com/image.jpg",
        )
        portfolio_2 = Portfolio.objects.create(
            name="New Portfolio 2",
            description="New Description 2",
            url="http://example2.com",
            image="http://example2.com/image.jpg",
            published=False,
        )  # Published = False

        new_talent = get_other_talent()
        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": new_talent.public_id}
        )

        # Assing both portfolios to the new_talent
        new_talent.portfolio.set([portfolio_1, portfolio_2])

        # See if new_talent can list all portfolios dispite publish status
        self.client.force_authenticate(new_talent.user)
        response_1 = self.client.get(url)
        response_data_1: List[dict] = response_1.data  # type: ignore
        self.assertEqual(len(response_data_1), 2)

        # Make sure other-users only access published portfolios
        self.client.force_authenticate(self.user)
        response_2 = self.client.get(url)
        response_data_2: List[dict] = response_2.data  # type: ignore
        self.assertEqual(len(response_data_2), 1)
        self.assertEqual(response_data_2[0].get("published"), True)
        self.assertEqual(response_data_2[0].get("name"), portfolio_1.name)
        self.assertEqual(response_data_2[0].get("public_id"), portfolio_1.public_id)

    # Failure tests
    def test_get_portfolio_unauthorized(self):
        """Verify unauthorized access handling"""

        self.client.force_authenticate(user=None)  # type: ignore
        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_portfolio_invalid_data(self):
        """Verify invalid data handling"""

        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )
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
        """Verify other user's portfolio update protection"""

        other_talent = get_other_talent()
        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": other_talent.public_id}
        )

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
        """Verify non-existent portfolio update handling"""

        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )
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
        """Verify non-existent portfolio deletion handling"""

        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": self.talent.public_id}
        )
        data = {"public_id": "non_existent_public_id"}
        response = self.client.delete(url, data, format="json")
        response_data: dict = response.data  # type: ignore
        self.assertIsNotNone(response_data.get("message"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_portfolio_other_user(self):
        """Verify other user's portfolio deletion protection"""

        other_talent = get_other_talent()
        url = reverse(
            "talent_portfolio_route", kwargs={"public_id": other_talent.public_id}
        )

        data = {"public_id": self.portfolio.public_id}
        response = self.client.delete(url, data, format="json")
        response_data: dict = response.data  # type: ignore
        self.assertIsNotNone(response_data.get("message"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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
