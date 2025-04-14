import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.models import Category, Feedback, Waitlist


@pytest.mark.django_db
def test_waitlist_model():
    waitlist = Waitlist.objects.create(name="John Doe", email="john@example.com")
    assert waitlist.name == "John Doe"
    assert waitlist.email == "john@example.com"
    assert waitlist.created_at is not None
    assert waitlist.updated_at is not None


@pytest.mark.django_db
def test_category_model():
    parent_category = Category.objects.create(
        name="Parent Category",
        slug="parent-category",
        keywords="test",
        image_url="http://example.com/image.jpg",
        description="Parent description",
    )
    child_category = Category.objects.create(
        name="Child Category",
        slug="child-category",
        keywords="test",
        image_url="http://example.com/image.jpg",
        description="Child description",
        parent=parent_category,
    )
    assert parent_category.name == "Parent Category"
    assert child_category.parent == parent_category


@pytest.mark.django_db
def test_feedback_model():
    feedback = Feedback.objects.create(
        message="Great service!",
        author_name="Jane Doe",
        author_email="jane@example.com",
        rating=5,
    )
    assert feedback.message == "Great service!"
    assert feedback.author_name == "Jane Doe"
    assert feedback.rating == 5


@pytest.mark.django_db
def test_waitlist_model_failure():

    # Missing name and email
    with pytest.raises(IntegrityError) as excinfo:
        Waitlist.objects.create(name=None, email=None)

    # Invalid email format
    with pytest.raises(ValidationError) as excinfo:
        Waitlist.objects.create(name="John Doe", email="invalid-email")

    with pytest.raises(IntegrityError) as excinfo:
        Category.objects.create(name=None, slug=None)

    # Invalid parent reference
    with pytest.raises(IntegrityError) as excinfo:
        Category.objects.create(
            name="Invalid Category", slug="invalid-category", parent_id=9999
        )
        Category.objects.create(
            name="Invalid Category", slug="invalid-category", parent_id=9999
        )

    with pytest.raises(IntegrityError) as excinfo:
        Feedback.objects.create(message=None, author_name=None, rating=None)

    # Invalid rating value
    with pytest.raises(ValidationError) as excinfo:
        Feedback.objects.create(
            message="Invalid rating", author_name="John Doe", rating=6
        )
    # Invalid rating value
    with pytest.raises(ValidationError) as excinfo:
        Feedback.objects.create(
            message="Invalid rating", author_name="John Doe", rating=6
        )


@pytest.mark.django_db
def test_category_model_failure():

    # Missing required fields
    with pytest.raises(IntegrityError) as excinfo:
        Category.objects.create(name=None, slug=None)

    # Duplicate slug
    with pytest.raises(IntegrityError) as excinfo:
        Category.objects.create(name="Category 1", slug="duplicate-slug")
        Category.objects.create(name="Category 2", slug="duplicate-slug")

    # Invalid parent reference
    with pytest.raises(IntegrityError) as excinfo:
        Category.objects.create(
            name="Invalid Category", slug="invalid-category", parent_id=9999
        )


@pytest.mark.django_db
def test_feedback_model_failure():

    # Missing required fields
    with pytest.raises(ValidationError) as excinfo:
        Feedback.objects.create(message=None, author_name=None, rating=None)

    # Invalid rating value (e.g., greater than the allowed maximum)
    with pytest.raises(ValidationError) as excinfo:
        feedback = Feedback.objects.create(
            message="Invalid rating", author_name="John Doe", rating=6
        )

    # Invalid rating value (e.g., less than the allowed minimum)
    with pytest.raises(ValidationError) as excinfo:
        feedback = Feedback.objects.create(
            message="Invalid rating", author_name="John Doe", rating=-1
        )

    # Missing email format validation
    with pytest.raises(ValidationError) as excinfo:
        feedback = Feedback.objects.create(
            message="Invalid email",
            author_name="John Doe",
            author_email="invalid-email",
            rating=4,
        )
