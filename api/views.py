from django.db import connection
import json
import openai
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
from openai import OpenAI
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
            return Response({'message': 'CSV Uploaded', 'columns': res})
        else:
            return JsonResponse({"error": "Failed to upload CSV", "message": res}, status=400)

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
        # Default to '=' if not provided
        operator = query_params.get('operator', '=')

        value = None if value == 'null' else value
        operator = '=' if operator == 'null' else operator

        if not field:
            return Response({'error': 'field is required'}, status=400)

        if not hasattr(GameData, field):
            return Response({'error': f'Invalid field: {field}'}, status=400)

        try:
            # Get search results
            search_results = getSearchResults(
                field, operator, value) if value is not None else None

            # Get aggregate results
            aggregate_results = getAggregateResults(field)

            # Get constrained aggregate results if applicable
            constrained_aggregate_results = None
            if GameData._meta.get_field(field).get_internal_type() in ['IntegerField', 'FloatField', 'DecimalField'] and value is not None:
                constrained_aggregate_results = getConstrainedAggregateResults(
                    field, operator, value)

            return Response({
                'search_results': search_results,
                'aggregate_results': aggregate_results,
                'constrained_aggregate_results': constrained_aggregate_results
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    def post(self, request):

        # return Response({"message":"TODO: This feature is to be implemented"}, status=200)
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({'error': 'Prompt is required'}, status=400)

        try:
            
            query = ''
            client = OpenAI(
                api_key='sk-proj-fomt6M4eUmwkz7Ja7PCDT3BlbkFJj6amgDi7u0V03jD7K8GV')

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # "gpt-3.5-turbo-0125", #"gpt-3.5-turbo",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": 'You are a Data Scientist Who wirte SQL queries for PostgreSQL'
                                'I will send you a natural language query and you need to write the sql query to get the user desired results from django sqlite the database.'
                                'the Table name: api_gamedata'
                                '''the columns of this table are 
                                AppID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=255)
    Release_date = models.DateField()
    Required_age = models.IntegerField()
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    DLC_count = models.IntegerField()
    About_the_game = models.TextField()
    Supported_languages = models.TextField()
    Windows = models.BooleanField()
    Mac = models.BooleanField()
    Linux = models.BooleanField()
    Positive = models.IntegerField()
    Negative = models.IntegerField()
    Score_rank = models.CharField(max_length=50)  # Assuming this is a string representation
    Developers = models.TextField()
    Publishers = models.TextField()
    Categories = models.TextField()
    Genres = models.TextField()
    Tags = models.TextField()
'''
                        'you need to write the sql query to get the user desired results from django sqlite the database.'
                                'Send the response in the following JSON format - { query: <Query>}'
                    },
                    {
                        "role": "user",
                        "content": f"Product: {prompt}"
                    },
                ],
                temperature=1,
                max_tokens=1024,
            )
            try:
                generated_text = response.choices[0].message.content
                # Load the JSON string into a dictionary
                data = json.loads(generated_text)
                query = data["query"]  # Extract the idea directly return idea
            except Exception as e:
                print(
                    f"An error occurred, probably openai being smart again : {e}")

            sql_query = query

            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row))
                           for row in cursor.fetchall()]

            return Response({'custom_prompt_results': results})
        except Exception as e:
            return Response({'error': f'An error occurred while processing the custom query: {str(e)}'}, status=500)
