import os


def application_environment(request=None):
    """
    Return the application environment variables to be used in the templates
    """

    return {
        "DEBUG": os.getenv("DEBUG"),
        "BASE_URL": os.getenv("BASE_URL"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT"),
        "FRONTEND_URL": os.getenv("FRONTEND_URL"),
        "APPLICATION_NAME": os.getenv("APPLICATION_NAME"),
        "APPLICATION_LOGO_URL": os.getenv("APPLICATION_LOGO_URL"),
        "APPLICATION_SUPPORT_EMAIL": os.getenv("APPLICATION_SUPPORT_EMAIL"),
        "APPLICATION_PRIVACY_POLICY_URL": os.getenv("APPLICATION_PRIVACY_POLICY_URL"),
        "APPLICATION_TERMS_OF_SERVICE_URL": os.getenv(
            "APPLICATION_TERMS_OF_SERVICE_URL"
        ),
    }


def email_environment():
    """
    Return the application email environment variables to be used in the templates
    """

    environment = application_environment()

    return {
        **environment,
    }
