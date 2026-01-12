from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Parent
from core.serializers import (LoginSerializer, ParentSerializer,
                              RegisterSerializer)


class RegisterView(APIView):
    """Register a new parent account"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # Create auth token
        token, created = Token.objects.get_or_create(user=result['user'])

        # Get parent data
        parent_serializer = ParentSerializer(result['parent'])

        return Response({
            'token': token.key,
            'parent': parent_serializer.data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Login and get auth token"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Get or create token
        token, created = Token.objects.get_or_create(user=user)

        # Get parent profile
        try:
            parent = Parent.objects.get(email=user.email)
            parent_serializer = ParentSerializer(parent)
            return Response({
                'token': token.key,
                'parent': parent_serializer.data
            })
        except Parent.DoesNotExist:
            return Response({
                'token': token.key,
                'message': 'Parent profile not found'
            }, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    """Logout and delete auth token"""

    def post(self, request):
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})
