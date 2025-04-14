import pytest
from rest_framework.test import APIClient

from core.models import Category, Feedback, Waitlist


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.mark.django_db
def test_waitlist_api(api_client):
    response = api_client.post(
        "/api/waitlist/", {"name": "John Doe", "email": "john@example.com"}
    )
    assert response.status_code == 201
    assert response.data["message"] == "Thank you for joining our waiting list"
    assert Waitlist.objects.filter(email="john@example.com").exists()


@pytest.mark.django_db
def test_waitlist_api_failure(api_client):
    # Missing both name and email
    response = api_client.post("/api/waitlist/", {"name": "", "email": ""})
    assert response.status_code == 400
    assert "message" in response.data

    # Invalid email format
    response = api_client.post(
        "/api/waitlist/", {"name": "John Doe", "email": "invalid-email"}
    )
    assert response.status_code == 400
    assert "message" in response.data


@pytest.mark.django_db
def test_category_api(api_client):
    parent_category = Category.objects.create(
        name="Parent Category",
        slug="parent-category",
        keywords="test",
        image_url="http://example.com/image.jpg",
        description="Parent description",
    )
    Category.objects.create(
        name="Child Category",
        slug="child-category",
        keywords="test",
        image_url="http://example.com/image.jpg",
        description="Child description",
        parent=parent_category,
    )
    response = api_client.get("/api/categories/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == parent_category.name


@pytest.mark.django_db
def test_category_api_failure(api_client):
    # Invalid query parameter
    response = api_client.get("/api/categories/?child=invalid")
    assert response.status_code == 200
    assert len(response.data) == 0

    # No categories available
    response = api_client.get("/api/categories/")
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_feedback_api(api_client):
    response = api_client.post(
        "/api/feedbacks/",
        {"message": "Great service!", "author_name": "Jane Doe", "rating": 5},
    )
    assert response.status_code == 200
    assert Feedback.objects.filter(author_name="Jane Doe").exists()

    response = api_client.get("/api/feedbacks/")
    assert response.status_code == 200
    assert len(response.data) > 0


@pytest.mark.django_db
def test_feedback_api_failure(api_client):
    # Missing required fields
    response = api_client.post(
        "/api/feedbacks/",
        {"message": "", "author_name": ""},
    )
    assert response.status_code == 400
    assert "message" in response.data

    # Invalid rating value
    response = api_client.post(
        "/api/feedbacks/",
        {"message": "Great service!", "author_name": "Jane Doe", "rating": 6},
    )
    assert response.status_code == 400
    assert "Rating must be between 1 and 5." == response.data.get("message")

    # Empty feedback list
    response = api_client.get("/api/feedbacks/")
    assert response.status_code == 200
    assert len(response.data) == 0
