from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistrationSerializer, LoginSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Create your views here.


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        # an obj holding raw input from client
        serializer = RegistrationSerializer(data=request.data)
        # is_valid validates data through RegisterSerializer validation logic
        if serializer.is_valid():
            #.save() finally triggers create()
            serializer.save()
            return Response({'message': 'Registration successful!'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Registration failed!', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'msg': 'Login successful',
            'data':{
                'token':{
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
                }}

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            token_data = self.get_jwt_token(user)
            token_data["data"]["user"] = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
            }

            return Response(token_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
class UserProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)