import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from clients.models import Client
from core.models import Category
from jobs.models import Job
from users.models.user import User
from utilities.time import utc_datetime


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def job_dict():
    return {
        "title": "Job 21",
        "pricing": {},
        "address": "address1",
        "country": {"code": "GM"},
        "benefits": [],
        "job_type": "other",
        "created_at": str(utc_datetime()),
        "description": "Job description",
        "third_party_address": "https://jobs.com/address1",
        "job_type_other": "Contingent",
        "required_skills": [],
        "application_deadline": str(
            utc_datetime(add_minutes=60 * 24 * 7 * 4)
        ),  # 1 month
        "third_party_metadata": {
            "company_name": "Company Name",
            "company_url": "https://company.com",
            "company_logo": "https://company.com/logo.png",
        },
    }


@pytest.fixture
def setup_data(db):
    # Create a client and category for testing
    user = User.objects.create(
        username="testuser",
        email="test@mail.com",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_client=True,
    )
    client = Client.objects.create(user=user, is_agent=True)
    category = Category.objects.create(
        name="Test Category", slug="test-category", is_agent=True
    )
    return client, category


@pytest.mark.django_db
def test_post_valid_data(api_client, job_dict, setup_data):
    url = reverse("job_scraper")
    data = {
        "site": "gamjobs",
        "third_party_jobs": [
            job_dict,
            {
                "title": "Job 22",
                "pricing": {},
                "address": "address2",
                "country": {"code": "GM"},
                "benefits": [],
                "job_type": "full-time",
                "created_at": str(utc_datetime()),
                "description": "Another job description",
                "third_party_address": "https://jobs.com/address2",
                "job_type_other": None,
                "required_skills": ["Skill 1", "Skill 2"],
                "application_deadline": str(
                    utc_datetime(add_minutes=60 * 24 * 7 * 2)
                ),  # 2 weeks
                "third_party_metadata": {
                    "company_name": "Another Company",
                    "company_url": "https://anothercompany.com",
                    "company_logo": "https://anothercompany.com/logo.png",
                },
            },
        ],
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Jobs created successfully"
    assert response.data["count"] == 2
    assert Job.objects.count() == 2

    # Verify jobs public_id and activy attributes
    job = Job.objects.last()

    assert job is not None
    assert job.get_activities is not None
    assert job.public_id is not None and job.public_id != ""
    assert job.published == True  # because we passed gamjobs as the site


@pytest.mark.django_db
def test_post_no_jobs(api_client):
    url = reverse("job_scraper")
    data = {"site": "gamjobs", "third_party_jobs": []}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "No jobs found"


@pytest.mark.django_db
def test_post_invalid_jobs(api_client, job_dict, setup_data):
    url = reverse("job_scraper")
    data = {
        "site": "gamjobs",
        "third_party_jobs": [
            job_dict,
            # missing required fields
            {
                "pricing": {},
                "address": "address2",
                "benefits": [],
                "job_type": "full-time",
                "description": "Another job description",
                "job_type_other": None,
                "required_skills": ["Skill 1", "Skill 2"],
                "third_party_metadata": {
                    "company_name": "Another Company",
                    "company_url": "https://anothercompany.com",
                    "company_logo": "https://anothercompany.com/logo.png",
                },
            },
        ],
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Jobs created successfully"
    assert response.data["count"] == 1  # Only one new job should be created
    assert Job.objects.count() == 1


@pytest.mark.django_db
def test_post_duplicate_jobs(api_client, setup_data, job_dict):
    client, category = setup_data
    # Create an existing job
    Job.objects.create(
        **job_dict,
        client=client,
        category=category,
    )

    url = reverse("job_scraper")

    data = {
        "site": "gamjobs",
        "third_party_jobs": [
            job_dict,  # this job should not be recreated
            {
                "title": "Job 22",
                "pricing": {},
                "address": "address2",
                "country": {"code": "GM"},
                "benefits": [],
                "job_type": "full-time",
                "created_at": str(utc_datetime()),
                "description": "Another job description",
                "third_party_address": "https://jobs.com/address2",
                "job_type_other": None,
                "required_skills": ["Skill 1", "Skill 2"],
                "application_deadline": str(
                    utc_datetime(add_minutes=60 * 24 * 7 * 2)
                ),  # 2 weeks
                "third_party_metadata": {
                    "company_name": "Another Company",
                    "company_url": "https://anothercompany.com",
                    "company_logo": "https://anothercompany.com/logo.png",
                },
            },
        ],
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Jobs created successfully"
    assert response.data["count"] == 1  # Only one new job should be created
    assert Job.objects.count() == 2
