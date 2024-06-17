REST_FRAMEWORK = {
    "PAGE_SIZE": 15,
    "DEFAULT_PAGINATION_CLASS": "src.features.paginator.DokoolaPaginator",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "src.features.dokoola_auth.DokoolaAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}


__all__ = ["REST_FRAMEWORK"]
