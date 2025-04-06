from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models import User

from ..models import  Talent


class TalentApplicationIdsAPIView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        try:
            user: User = request.user
            assert user.is_talent, "403: Forbidden request!"
            talent = Talent.objects.get(user=user)
            return Response(talent.applications_ids or [], status=200)
        except Talent.DoesNotExist:
            return AssertionError("403: Forbidden request!")
        except AssertionError as e:
            return Response(
                {"message": str(e)},
                status=403,
            )
        except Exception as e:
            return Response(
                {"message": "INternal Server Error"},
                status=500,
            )
