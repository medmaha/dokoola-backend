from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
    )
from rest_framework.response import Response

from ..models import User
from ..token import GenerateToken


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def verifyEmail(request):
    username = request.data.get('username')
    verification_code = request.data.get('code')

    user = User.objects.filter(username=username).first()

    if not user:
        return Response({'message':'This request is unauthorize/forbidden'}, status=403)

    try:
        if not int(verification_code) == 12345:
            raise ValueError('Invalid verification code')
    except Exception as e:
        return Response({'message':e}, status=400)

    user.is_active = True
    user.save()

    message = f'You\'ve successfully verify your email'

    tokens = GenerateToken().tokens(user, context={'request':request})
    return Response({'tokens':tokens, 'message':message})





