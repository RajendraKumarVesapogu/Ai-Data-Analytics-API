from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db import transaction
from rest_framework_simplejwt.authentication import JWTAuthentication
import pandas as pd
import requests
from io import StringIO
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import GameData
from .serializers import GameDataSerializer
from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from .models import GameData
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest

from .utils import saveToDatabase, getAggregateResults, getConstrainedAggregateResults, getSearchResults

import pandas as pd
from bs4 import BeautifulSoup
from .serializers import UserSerializer
from .models import GameData
import pandas as pd
import requests
from io import StringIO
# --------------------------------- Home ---------------------------------

@api_view(['GET'])
def home(request):
    return Response({'message': 'Api/'})

# --------------------------------- User ---------------------------------

@api_view(['GET'])
@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = get_object_or_404(User, id=request.user.id)
    serializer = UserSerializer(user)
    return Response(serializer.data)

# --------------------------------- Login ---------------------------------

@api_view(['POST'])
def login(request):
    try:
        user = get_object_or_404(User, email=request.data.get('email'))
        if user.check_password(request.data.get('password')):
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# --------------------------------- Test Token ---------------------------------

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({'detail': 'Token is valid'}, status=status.HTTP_200_OK)

# --------------------------------- Logout ---------------------------------

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token_key = request.headers.get('Authorization').split(' ')[1]
        token = Token.objects.get(key=token_key)
        token.delete()
        return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

# --------------------------------- Register ---------------------------------

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --------------------------------- CSV Upload ---------------------------------

@api_view(['POST'])
def csv_upload(request):
    csv_url = request.data.get('url')
    if not csv_url:
        return JsonResponse({"error": "CSV URL is required"}, status=400)
    try:        
        res = saveToDatabase(csv_url)
        if res:
            return Response({'message': 'CSV Uploaded'})
        else:
            return JsonResponse({"error": "Failed to upload CSV", "message":res}, status=400)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
        
# --------------------------------- Game Data ---------------------------------

class GameDataQueryView(APIView):
    def get(self, request, *args, **kwargs):
        query_params = request.query_params
        
        if not query_params:
            return Response({'error': 'No query parameters provided'}, status=400)
        
        field = query_params.get('field')
        value = query_params.get('value')
        operator = query_params.get('operator', '=')  # Default to '=' if not provided
        
        if not field or value is None:
            return Response({'error': 'Both field and value are required'}, status=400)
        
        if not hasattr(GameData, field):
            return Response({'error': f'Invalid field: {field}'}, status=400)
        
        try:
            # Get search results
            search_results = getSearchResults(field, operator, value)
            
            # Get aggregate results
            aggregate_results = getAggregateResults(field)
            
            # Get constrained aggregate results if applicable
            constrained_aggregate_results = None
            if GameData._meta.get_field(field).get_internal_type() in ['IntegerField', 'FloatField', 'DecimalField']:
                constrained_aggregate_results = getConstrainedAggregateResults(field, operator, value)
            
            return Response({
                'search_results': search_results,
                'aggregate_results': aggregate_results,
                'constrained_aggregate_results': constrained_aggregate_results
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
