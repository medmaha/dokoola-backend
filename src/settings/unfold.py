import os
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "Dokoola",
    "SITE_HEADER": "Dokoola",
    "SITE_URL": "/",
    # "SITE_ICON": lambda request: static("assets/logo.ico"),  # both modes, optimise for 32px height
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),  # light mode
    #     "dark": lambda request: static("icon-dark.svg"),  # dark mode
    # },
    "SITE_LOGO": lambda request: static(
        "./logo.png"
    ),  # both modes, optimise for 32px height "
    # "SITE_LOGO": {
    #     "light": lambda request:  static("logo.png"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("./favicon.ico"),
        },
    ],
    "SHOW_HISTORY": True,  # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": False,  # show/hide "View on site" button, default: True
    "ENVIRONMENT": ["Production", "danger"],
    # "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
    # "THEME": "dark", # Force theme: "dark" or "light". Will disable theme switcher
    "LOGIN": {
        "redirect_after": lambda request: reverse_lazy("admin:index"),
        "image": None,
        # "image": lambda request: static("assets/hero.png"),
    },
    # "STYLES": [
    #     lambda request: static("css/style.css"),
    # ],
    # "SCRIPTS": [
    #     lambda request: static("js/script.js"),
    # ],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": None,
                "separator": False,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    # {
                    #     "title": _("Dashboard"),
                    #     "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                    #     "link": "/lll" or reverse_lazy("admin:index"),
                    #     "badge": 3,
                    #     "permission": lambda request: request.user.is_superuser,
                    # },
                    # {
                    #     "title": _("Auth Groups"),
                    #     "icon": "security",  # Supported icon set: https://fonts.google.com/icons
                    #     "link": reverse_lazy("admin:auth_group_changelist"),
                    #     # "badge": 3,
                    #     "permission": lambda request: request.user.is_superuser,
                    # },
                    {
                        "title": _("Auth Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": _("Clients"),
                        "icon": "people",
                        "link": reverse_lazy("admin:clients_client_changelist"),
                    },
                    {
                        "title": _("Talents"),
                        "icon": "people",
                        "link": reverse_lazy("admin:talents_talent_changelist"),
                    },
                    {
                        "title": _("Job"),
                        "icon": "work",
                        "link": reverse_lazy("admin:jobs_job_changelist"),
                    },
                    {
                        "title": _("Proposals"),
                        "icon": "article",
                        "link": reverse_lazy("admin:proposals_proposal_changelist"),
                    },
                    {
                        "title": _("Contacts"),
                        "icon": "contract",
                        "link": reverse_lazy("admin:contracts_contract_changelist"),
                    },
                    {
                        "title": _("Projects"),
                        "icon": "badge",
                        "link": reverse_lazy("admin:projects_project_changelist"),
                    },
                    {
                        "title": _("Notifications"),
                        "icon": "notifications",
                        "link": reverse_lazy(
                            "admin:notifications_notification_changelist"
                        ),
                    },
                    {
                        "title": _("Messaging"),
                        "icon": "chat",
                        "link": reverse_lazy("admin:messaging_message_changelist"),
                    },
                    {
                        "title": _("Reviews"),
                        "icon": "reviews",
                        "link": reverse_lazy("admin:reviews_review_changelist"),
                    },
                    {
                        "title": _("Blacklisted Tokens"),
                        "icon": "security",
                        "link": reverse_lazy(
                            "admin:token_blacklist_blacklistedtoken_changelist"
                        ),
                    },
                    # {
                    #     "title": _("Outstanding Tokens"),
                    #     "icon": "security",
                    #     "link": reverse_lazy("admin:token_blacklist_outstandingtoken_changelist"),
                    # },
                ],
            },
        ],
    },
}


def dashboard_callback(request, context):
    """
    Callback to prepare custom variables for index template which is used as dashboard
    template. It can be overridden in application by creating custom admin/index.html.
    """
    context.update(
        {
            "sample": "example",  # this will be injected into templates/admin/index.html
        }
    )
    return context


def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Production", "danger"]  # info, danger, warning, success


def badge_callback(request):
    return 3


# def permission_callback(request):
#     return request.user.has_perm("sample_app.change_model")
