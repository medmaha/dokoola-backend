from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User

from ..models import Certificate, Talent


@pytest.fixture
def user():
    return User.objects.create_user(
        email="testuser@example.com",
        password="testpassword",
        username="testusername",
    )


@pytest.fixture
def talent(user):
    return Talent.objects.create(user=user)


@pytest.fixture
def certificate(talent):
    cert = Certificate.objects.create(
        name="Test Certificate",
        organization="Test Organization",
        url="https://example.com/cert",
        date_issued=date(2023, 1, 1),
        file_url="https://example.com/cert.pdf",
    )
    talent.certificates.add(cert)
    talent.save()
    return cert


@pytest.fixture
def api_client(user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_talent():
    other_user = User.objects.create_user(
        email="otheruser@example.com",
        password="otherpassword",
        username="otherusername",
    )
    return Talent.objects.create(user=other_user)


class TestCertificateAPI:

    @pytest.mark.django_db
    def test_get_certificates(self, api_client, talent, certificate):
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": talent.public_id}
        )
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == certificate.name

    @pytest.mark.django_db
    def test_post_certificate(self, api_client, talent):
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": talent.public_id}
        )
        data = {
            "name": "New Certificate",
            "organization": "New Organization",
            "url": "https://example.com/new-cert",
            "date_issued": "2023-02-01",
            "file_url": "https://example.com/new-cert.pdf",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == data["name"]
        assert "public_id" in response.data

        cert = Certificate.objects.get(public_id=response.data.get("public_id"))
        assert talent.public_id in cert.talent.first().public_id  # type: ignore

    @pytest.mark.django_db
    def test_put_certificate(self, api_client, talent, certificate):
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": talent.public_id}
        )
        data = {
            "name": "Updated Certificate",
            "organization": certificate.organization,
            "url": certificate.url,
            "date_issued": "2023-01-01",
            "published": True,
            "public_id": certificate.public_id,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]
        assert response.data["published"] is True

    @pytest.mark.django_db
    def test_delete_certificate(self, api_client, talent, certificate):
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": talent.public_id}
        )
        data = {"public_id": certificate.public_id}
        response = api_client.delete(url, data, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Certificate.objects.count() == 0

    @pytest.mark.django_db
    def test_published_certificate(self, api_client, other_talent, user):
        certificate_1 = Certificate.objects.create(
            name="New Certificate 1",
            organization="New Organization 1",
            url="https://example.com/new-cert1",
            date_issued="2021-02-01",
            file_url="https://example.com/new-cert1.pdf",
            published=True,
        )
        certificate_2 = Certificate.objects.create(
            name="New Certificate 2",
            organization="New Organization 2",
            url="https://example.com/new-cert2",
            date_issued="2022-02-01",
            file_url="https://example.com/new-cert2.pdf",
        )
        other_talent.certificates.set([certificate_1, certificate_2])

        # Authenticated as other_talent's user
        api_client.force_authenticate(user=other_talent.user)
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": other_talent.public_id}
        )
        response_1 = api_client.get(url)
        assert len(response_1.data) == 2

        # Authenticated as a different user
        api_client.force_authenticate(user=user)
        response_2 = api_client.get(url)
        assert len(response_2.data) == 1
        assert response_2.data[0]["published"] is True
        assert response_2.data[0]["name"] == certificate_1.name
        assert response_2.data[0]["public_id"] == certificate_1.public_id

    @pytest.mark.django_db
    def test_unauthorized_access(self, api_client, talent):
        api_client.force_authenticate(user=None)
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": talent.public_id}
        )
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_invalid_certificate_data(self, api_client, talent):
        url = reverse(
            "talent_certificate_route", kwargs={"public_id": talent.public_id}
        )
        data = {"name": "Invalid Certificate"}  # Missing required fields
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
