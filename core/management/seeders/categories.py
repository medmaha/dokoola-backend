from calendar import c
from core.models import Category


categories = [
    {
        'name': 'Software Development',
        'slug': 'web-development',
        'keywords': 'website, frontend, backend, full stack, database, db, cms, mobile-app, web design',
        'image_url': '/img/categories/software-development.jpg',
        'description': 'Development of software applications.',
        'disabled': False,
    },
    {
        'name': 'Graphic Design',
        'slug': 'graphic-design',
        'keywords': 'logo, branding, illustration, photoshop, vector',
        'image_url': '/img/categories/graphic-design.jpg',
        'description': 'Designing visual concepts and graphical content.',
        'disabled': False,
    },
    {
        'name': 'Writing & Translation',
        'slug': 'writing-translation',
        'keywords': 'copywriting, editing, translation, proofreading, content creation',
        'image_url': '/img/categories/writing-translation.jpg',
        'description': 'Providing written content and language translation services.',
        'disabled': False,
    },
    {
        'name': 'Digital Marketing',
        'slug': 'digital-marketing',
        'keywords': 'SEO, SEM, social media marketing, PPC, email marketing',
        'image_url': '/img/categories/digital-marketing.jpg',
        'description': 'Promoting products or services through digital channels.',
        'disabled': False,
    },
    {
        'name': 'Data Science & Analytics',
        'slug': 'data-science-analytics',
        'keywords': 'data analysis, machine learning, data visualization, data mining, statistics',
        'image_url': '/img/categories/data-science.jpg',
        'description': 'Analyzing and interpreting complex data sets.',
        'disabled': False,
    },
    {
        'name': 'Electrical Installation',
        'slug': 'electrical-installation',
        'keywords': 'wiring, lighting, electrical panel, circuit installation, electrical maintenance',
        'image_url': '/img/categories/electrical-installation.jpg',
        'description': 'Installation and maintenance of electrical systems and components.',
        'disabled': False,
    },
    {
        'name': 'Admin Support',
        'slug': 'admin-support',
        'keywords': 'virtual assistant, data entry, customer support, email handling, scheduling',
        'image_url': '/img/categories/admin-support.jpg',
        'description': 'Providing administrative assistance and support.',
        'disabled': False,
    },
    {
        'name': 'Satellite Installation',
        'slug': 'satellite-installation',
        'keywords': 'satellite dish, antenna, installation, satellite TV, satellite internet',
        'image_url': '/img/categories/satellite-installation.jpg',
        'description': 'Installation and setup of satellite equipment.',
        'disabled': False,
    },
]


def categories_seeders():
    """Seed categories."""
    
    for category in categories:
        # Check if the category already exists
        existing = Category.objects.filter(slug=category.get("slug")).exists()

        # Skip if the category already exists
        if existing:
            continue
        
        # Create the category
        Category.objects.create(**category)
