from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import  get_object_or_404
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db import transaction
from rest_framework import generics, permissions
from django.db import connection
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.authentication import JWTAuthentication

import pandas as pd
import requests

#---------------------------------Home---------------------------------

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def home(request):
    return Response({'message': 'Api/'})

#---------------------------------User---------------------------------

@api_view(['GET'])
def get_user(request):
    user = get_object_or_404(User, id=request.user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data)
#---------------------------------Login---------------------------------
@api_view(['POST'])
def login(request):
    try:
        user = get_object_or_404(User, email=request.data['email'])
        if user.check_password(request.data['password']):
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({'token': token.key, 'user': serializer.data})
        else:
            return Response("Invalid credentials", status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

#---------------------------------Test Token---------------------------------

@api_view(['GET'])
@authentication_classes([ TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed!")

#---------------------------------Logout---------------------------------
@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token_key = request.headers.get('Authorization').split(' ')[1]
        token = Token.objects.get(key=token_key)
        token.delete()
        return Response("Logout successful", status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response("Invalid token", status=status.HTTP_401_UNAUTHORIZED)

#---------------------------------Register---------------------------------  

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


