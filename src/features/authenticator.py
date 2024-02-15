import os

from rest_framework.authentication import BaseAuthentication
from .jwt_auth import JWTAuthentication
from .celesup_auth import CelesupClientApi

AUTH_MECHANISM = os.environ.get("AUTHENTICATION_MECHANISM")


class DokoolaAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authenticators = [CelesupClientApi()]
      
        for idx, authenticator in enumerate(authenticators):
        
            _user = authenticator.authenticate(request)

            if _user:
                user, auth = _user
                if user is not None:
                    # if idx < (len(authenticators) - 1):
                    #     continue
                    return user, auth
                else:
                    break

        return None, None
