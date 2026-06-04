from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.
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