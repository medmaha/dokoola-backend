import time
from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import User

from ..models import Certificate, Talent


class CertificateAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test user and talent
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            username="testusername",
        )
        self.talent = Talent.objects.create(user=self.user)

        # Create test certificate
        self.certificate = Certificate.objects.create(
            name="Test Certificate",
            organization="Test Organization",
            url="https://example.com/cert",
            date_issued=date(2023, 1, 1),
            file_url="https://example.com/cert.pdf",
        )
        self.talent.certificates.add(self.certificate)

        # Authenticate client
        self.client.force_authenticate(user=self.user)

    def test_get_certificates(self):
        """Test getting certificates list"""

        url = reverse(
            "talent_certificate_route", kwargs={"public_id": self.talent.public_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.certificate.name)

    def test_post_certificate(self):
        """Test creating a new certificate"""

        url = reverse(
            "talent_certificate_route", kwargs={"public_id": self.talent.public_id}
        )
        data = {
            "name": "New Certificate",
            "organization": "New Organization",
            "url": "https://example.com/new-cert",
            "date_issued": "2023-02-01",
            "file_url": "https://example.com/new-cert.pdf",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Certificate.objects.count(), 2)
        self.assertEqual(response.data["name"], data["name"])
        self.assertIn("public_id", response.data)

        # Get the newly created certificate
        cert = Certificate.objects.get(public_id=response.data.get("public_id"))

        cert_talent__public_ids: list[str] = cert.talent.filter().values_list(
            "public_id", flat=True
        )

        # Check the talent of this certificate was set by the api-handler
        self.assertIn(self.talent.public_id, cert_talent__public_ids)

    def test_put_certificate(self):
        """Test updating a certificate"""

        url = reverse(
            "talent_certificate_route", kwargs={"public_id": self.talent.public_id}
        )
        data = {
            "name": "Updated Certificate",
            "organization": self.certificate.organization,
            "url": self.certificate.url,
            "date_issued": "2023-01-01",
            "published": True,
            "public_id": self.certificate.public_id,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], data["name"])
        self.assertTrue(response.data["published"])

    def test_delete_certificate(self):
        """Test deleting a certificate"""

        url = reverse(
            "talent_certificate_route", kwargs={"public_id": self.talent.public_id}
        )
        data = {"public_id": self.certificate.public_id}
        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Certificate.objects.count(), 0)

    def test_published_certificate(self):
        """Verify certificate visibility rules"""

        certificate_1 = Certificate.objects.create(
            **{
                "name": "New Certificate 1",
                "organization": "New Organization 1",
                "url": "https://example.com/new-cert1",
                "date_issued": "2021-02-01",
                "file_url": "https://example.com/new-cert1.pdf",
                "published": True,
            }
        )
        certificate_2 = Certificate.objects.create(
            **{
                "name": "New Certificate 2",
                "organization": "New Organization 2",
                "url": "https://example.com/new-cert1",
                "date_issued": "2022-02-01",
                "file_url": "https://example.com/new-cert2.pdf",
            }
        )  # Default Published = False

        new_talent = get_other_talent()
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": new_talent.public_id}
        )

        # Assing both certificates to the new_talent
        new_talent.certificates.set([certificate_1, certificate_2])

        # See if new_talent can list all certificates dispite publish status
        self.client.force_authenticate(new_talent.user)
        response_1 = self.client.get(url)
        response_data_1: List[dict] = response_1.data  # type: ignore
        self.assertEqual(len(response_data_1), 2)

        # Make sure other-users only access published certificates
        self.client.force_authenticate(self.user)
        response_2 = self.client.get(url)
        response_data_2: List[dict] = response_2.data  # type: ignore
        self.assertEqual(len(response_data_2), 1)
        self.assertEqual(response_data_2[0].get("published"), True)
        self.assertEqual(response_data_2[0].get("name"), certificate_1.name)
        self.assertEqual(response_data_2[0].get("public_id"), certificate_1.public_id)

    def test_max_certificates_limit(self):
        """Test maximum certificates limit"""

        url = reverse(
            "talent_certificate_route", kwargs={"public_id": self.talent.public_id}
        )

        # Create maximum allowed certificates
        certs = []
        for i in range(5):  # Already has 1 certificate, adding 5 more to reach limit
            cert = Certificate(
                name=f"Certificate {i}",
                organization="Test Org {i}",
                url=f"https://example.com/cert{i}",
                date_issued=date(2023, 1, 1),
            )
            certs.append(cert)

        __certs = Certificate.objects.bulk_create(certs)
        for _cert in __certs:
            self.talent.certificates.add(_cert)

        time.sleep(0.03)  # wait for many-to-many manager takes effects
        self.talent.refresh_from_db()

        # Try to create one more
        data = {
            "name": "One More Certificate",
            "organization": "Test Organization",
            "url": "https://example.com/cert",
            "date_issued": "2023-01-01",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Maximum number of certificates reached", response.data["message"]
        )

    def test_published_certificates(self):
        """Verify certificates visibility rules"""

        certificate_1 = Certificate.objects.create(
            name="New Certificate 2",
            organization="New Organization",
            url="https://example1.com/cert",
            date_issued=date(2021, 1, 1),
            file_url="https://example1.com/cert.pdf",
            published=True,
        )
        certificate_2 = Certificate.objects.create(
            name="New Certificate 2",
            organization="New Organization 2",
            url="https://example2.com/cert",
            date_issued=date(2022, 1, 1),
            file_url="https://example2.com/cert.pdf",
        )  # Default Published = False

        new_talent = get_other_talent()
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": new_talent.public_id}
        )

        # Assing both certificates to the new_talent
        new_talent.certificates.set([certificate_1, certificate_2])

        # See if new_talent can list all certificates dispite publish status
        self.client.force_authenticate(new_talent.user)
        response_1 = self.client.get(url)
        response_data_1: List[dict] = response_1.data  # type: ignore
        self.assertEqual(len(response_data_1), 2)

        # Make sure other-users only access published certificates
        self.client.force_authenticate(self.user)
        response_2 = self.client.get(url)
        response_data_2: List[dict] = response_2.data  # type: ignore
        self.assertEqual(len(response_data_2), 1)
        self.assertEqual(response_data_2[0].get("published"), True)
        self.assertEqual(response_data_2[0].get("name"), certificate_1.name)
        self.assertEqual(response_data_2[0].get("public_id"), certificate_1.public_id)

    def test_unauthorized_access(self):
        """Test unauthorized access"""

        self.client.force_authenticate(user=None)
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": self.talent.public_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Failed Tests
    def test_invalid_certificate_data(self):
        """Test creating certificate with invalid data"""

        url = reverse(
            "talent_certificate_route", kwargs={"public_id": self.talent.public_id}
        )
        data = {
            "name": "Invalid Certificate",
            # Missing required fields
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
