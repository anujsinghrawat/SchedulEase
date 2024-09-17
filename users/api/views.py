from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework import status

from users.api.utils import UsersUtils, EventUtils
from _sebase.api.views import BaseViewSet


class UsersViewSet(BaseViewSet):
    data_class = UsersUtils()

    def say_hi(self, request):
        resp, status_code = self.data_class.say_hi()
        return Response(resp, status=status_code)


# learn about APIViewSet
class EventViewSet(BaseViewSet):
    view_class = EventUtils()

    def get_user_events(self, request):
        response, status_code = self.view_class.get_user_events(**request.query_params)
        return Response(response, status=status_code)

    def create_event_type(self, request):
        response, status_code = self.view_class.create_event_type(
            request.user, **request.data)
        return Response(response, status=status_code)

    def create_event(self, request):
        response, status_code = self.view_class.create_event(
             **request.data)
        return Response(response, status=status_code)


class SignupView(BaseViewSet):
    view_class = UsersUtils()

    def sigup_user(self, request):
        response, status_code = self.view_class.create_user(**request.data)
        return Response(response, status=status_code)

class LoginView(BaseViewSet):
    view_class = UsersUtils()

    def login_user(self, request):
        response, status_code = self.view_class.login_user(**request.data)
        return Response(response, status=status_code)

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        payload = decode_jwt_token(refresh_token)
        if payload is None:
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        access_token, refresh_token = generate_tokens(user)
        return Response({
            'access': access_token,
            'refresh': refresh_token
        }, status=status.HTTP_200_OK)