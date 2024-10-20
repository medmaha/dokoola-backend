from calendar import c
from core.models import Category

categories = [
    {
        "name": "Software Development",
        "slug": "software-development",
        "keywords": "website, frontend, backend, full stack, database, db, cms, mobile-app, web design",
        "image_url": "/img/categories/software-development.jpg",
        "description": "Development of software applications for web, mobile, and desktop platforms.",
        "disabled": False,
    },
    {
        "name": "Graphic Design",
        "slug": "graphic-design",
        "keywords": "logo, branding, illustration, photoshop, vector, UX/UI design",
        "image_url": "/img/categories/graphic-design.jpg",
        "description": "Designing creative visual concepts, graphics, and user interfaces.",
        "disabled": False,
    },
    {
        "name": "Writing & Translation",
        "slug": "writing-translation",
        "keywords": "copywriting, content writing, editing, translation, proofreading, technical writing",
        "image_url": "/img/categories/writing-translation.jpg",
        "description": "Creating written content and providing language translation services.",
        "disabled": False,
    },
    {
        "name": "Digital Marketing",
        "slug": "digital-marketing",
        "keywords": "SEO, SEM, social media, PPC, email marketing, content marketing, influencer marketing",
        "image_url": "/img/categories/digital-marketing.jpg",
        "description": "Promoting brands through digital channels like social media, SEO, and paid advertising.",
        "disabled": False,
    },
    {
        "name": "Data Science & Analytics",
        "slug": "data-science-analytics",
        "keywords": "data analysis, machine learning, AI, data visualization, data mining, big data, statistics",
        "image_url": "/img/categories/data-science.jpg",
        "description": "Analyzing complex data sets and building predictive models to drive decision-making.",
        "disabled": False,
    },
    {
        "name": "Electrical Installation",
        "slug": "electrical-installation",
        "keywords": "wiring, lighting, electrical panel, circuit installation, electrical maintenance, power systems",
        "image_url": "/img/categories/electrical-installation.jpg",
        "description": "Installation and maintenance of electrical systems and components in residential, commercial, and industrial spaces.",
        "disabled": False,
    },
    {
        "name": "Admin Support",
        "slug": "admin-support",
        "keywords": "virtual assistant, data entry, customer support, email handling, scheduling, office management",
        "image_url": "/img/categories/admin-support.jpg",
        "description": "Providing administrative assistance, virtual office management, and customer support services.",
        "disabled": False,
    },
    {
        "name": "Satellite Installation",
        "slug": "satellite-installation",
        "keywords": "satellite dish, antenna, installation, satellite TV, satellite internet, signal repair",
        "image_url": "/img/categories/satellite-installation.jpg",
        "description": "Installation and maintenance of satellite communication equipment for television, internet, and other services.",
        "disabled": False,
    },
    {
        "name": "Video & Animation",
        "slug": "video-animation",
        "keywords": "video editing, animation, 3D modeling, motion graphics, explainer videos",
        "image_url": "/img/categories/video-animation.jpg",
        "description": "Creating engaging videos, animations, and motion graphics for various purposes.",
        "disabled": False,
    },
    {
        "name": "Music & Audio",
        "slug": "music-audio",
        "keywords": "music production, audio editing, voiceover, mixing, mastering, sound design",
        "image_url": "/img/categories/music-audio.jpg",
        "description": "Providing audio and music production services, including editing, mixing, and voiceover.",
        "disabled": False,
    },
    {
        "name": "Business Consulting",
        "slug": "business-consulting",
        "keywords": "strategy, business plan, market research, financial analysis, startup consulting",
        "image_url": "/img/categories/business-consulting.jpg",
        "description": "Offering expert advice and strategies to improve business operations and growth.",
        "disabled": False,
    },
    {
        "name": "Legal Services",
        "slug": "legal-services",
        "keywords": "legal advice, contract writing, intellectual property, business law, copyright",
        "image_url": "/img/categories/legal-services.jpg",
        "description": "Providing legal consultation and services, including contract drafting and intellectual property management.",
        "disabled": False,
    },
    {
        "name": "Photography & Videography",
        "slug": "photography-videography",
        "keywords": "photography, videography, video editing, drone footage, event photography",
        "image_url": "/img/categories/photography-videography.jpg",
        "description": "Professional photography and videography services for events, products, and more.",
        "disabled": False,
    },
    {
        "name": "Fitness & Wellness",
        "slug": "fitness-wellness",
        "keywords": "personal training, yoga, nutrition, fitness coaching, wellness consultation",
        "image_url": "/img/categories/fitness-wellness.jpg",
        "description": "Services related to fitness coaching, nutrition advice, and personal wellness.",
        "disabled": False,
    },
]


def categories_seeding():
    """Seed categories."""

    for category in categories:
        # Check if the category already exists
        slug = category.pop("slug")
        existing = Category.objects.filter(slug=slug).update(**category)

        # Skip if the category already exists
        if existing != 0:
            continue

        # Create the category
        Category.objects.create(**category)
