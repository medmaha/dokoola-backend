from django.utils.text import slugify

from core.models import Category

default_categories = [
    {
        "name": "Third Party",
        "slug": "third-party",
        "image_url": "",
        "is_agent": True,
        "description": "Providing top jobs from third party sources by Dokoola Agent.",
        "keywords": "legal advice, contract writing, intellectual property, business law, copyright",
    },
    {
        "name": "Software Development & IT",
        "image_url": "/img/categories/software-development.jpg",
        "description": "Development of software applications, IT services, cloud solutions, and cybersecurity.",
        "keywords": "software development, IT services, cloud computing, cybersecurity, DevOps",
        "children": [
            "Web Development",
            "Mobile App Development",
            "Desktop Software Development",
            "DevOps & Cloud Engineering",
            "Cybersecurity",
            "Database Development",
            "QA & Software Testing",
        ],
    },
    {
        "name": "Design & Creative",
        "image_url": "/img/categories/graphic-design.jpg",
        "description": "Graphic design, UI/UX, video editing, animation, and creative visual services.",
        "keywords": "graphic design, UI/UX, video editing, animation, 3D modeling, photography",
        "children": [
            "Graphic Design",
            "UI/UX Design",
            "Video & Animation",
            "3D Modeling & Rendering",
            "Photography",
            "Illustration & Art",
        ],
    },
    {
        "name": "Writing & Translation",
        "image_url": "/img/categories/writing-translation.jpg",
        "description": "Creating written content, copywriting, and language translation services.",
        "keywords": "copywriting, content writing, technical writing, translation, proofreading",
        "children": [
            "Copywriting",
            "Content Writing",
            "Technical Writing",
            "Translation & Localization",
            "Proofreading & Editing",
        ],
    },
    {
        "name": "Marketing & Sales",
        "image_url": "/img/categories/digital-marketing.jpg",
        "description": "SEO, social media marketing, advertising, lead generation, and branding services.",
        "keywords": "SEO, social media marketing, advertising, branding, sales, lead generation",
        "children": [
            "SEO & SEM",
            "Social Media Marketing",
            "Email Marketing",
            "Advertising & PPC",
            "Branding & Strategy",
            "Sales & Lead Generation",
        ],
    },
    {
        "name": "Business & Finance",
        "image_url": "/img/categories/business-consulting.jpg",
        "description": "Business consulting, accounting, finance, investment, and corporate strategy.",
        "keywords": "business consulting, finance, investment, accounting, HR, legal services",
        "children": [
            "Business Consulting",
            "Financial Advisory & Investment",
            "Accounting & Bookkeeping",
            "HR & Recruiting",
            "Legal Consulting",
        ],
    },
    {
        "name": "Engineering & Technical",
        "image_url": "/img/categories/electrical-installation.jpg",
        "description": "Electrical, satellite installation, mechanical, and civil engineering services.",
        "keywords": "electrical engineering, mechanical engineering, civil engineering, CAD, satellite installation",
        "children": [
            "Electrical Engineering",
            "Mechanical Engineering",
            "Civil & Structural Engineering",
            "Satellite Installation",
            "CAD & 3D Drafting",
        ],
    },
    {
        "name": "Admin & Customer Support",
        "image_url": "/img/categories/admin-support.jpg",
        "description": "Administrative assistance, virtual office management, and customer support.",
        "keywords": "virtual assistance, customer support, data entry, project management, technical support",
        "children": [
            "Virtual Assistance",
            "Customer Support",
            "Data Entry",
            "Project Management",
            "Technical Support",
        ],
    },
]


def __get_item_slug(item: dict):
    _slug = item.get("slug", None)

    if _slug:
        return _slug

    return slugify(item.get("name"))


category_slugs = lambda: [__get_item_slug(item) for item in default_categories]


def cleanup_categories():
    all_slugs = category_slugs()

    existing_slugs = (
        Category.objects.only("slug", "pk").distinct().values_list("slug", flat=True)
    )

    unique_slugs = [slug for slug in all_slugs if slug not in existing_slugs]

    filtered_categories = [
        item for item in default_categories if __get_item_slug(item) in unique_slugs
    ]

    return filtered_categories


def categories_seeding():
    """Seed categories."""

    from django.db import transaction

    data = cleanup_categories()

    child_count = 0
    parent_count = 0

    with transaction.atomic():
        for category_data in data:
            parent_category, created = Category.objects.get_or_create(
                name=category_data["name"],
                defaults={
                    "slug": __get_item_slug(category_data),
                    "image_url": category_data["image_url"],
                    "description": category_data["description"],
                    "keywords": category_data["keywords"],
                    "disabled": False,
                    "is_agent": category_data.get("is_agent", False),
                },
            )

            if created:
                parent_count += 1

            for child_name in category_data.get("children", []):
                _, _created = Category.objects.get_or_create(
                    name=child_name,
                    defaults={
                        "slug": slugify(child_name),
                        "parent": parent_category,
                        "image_url": category_data["image_url"],
                        "description": f"Subcategory of {category_data['name']}",
                        "keywords": category_data["keywords"],
                        "is_agent": False,
                    },
                )
                if _created:
                    child_count += 1

        print(
            {
                "Category Seeding": {
                    "results": {
                        "child_count": child_count,
                        "parent_count": parent_count,
                    }
                }
            }
        )
