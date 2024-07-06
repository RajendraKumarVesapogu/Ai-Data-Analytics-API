from django.db import connection, IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication

from openai import OpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv() 

from .models import GameData
from .serializers import GameDataSerializer, UserSerializer
from .utils import save_to_database, get_aggregate_results, get_constrained_aggregate_results, get_search_results

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

# --------------------------------- Authentication ---------------------------------

@api_view(['POST'])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = get_object_or_404(User, email=email)
        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({'detail': 'Token is valid'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        token_key = request.headers.get('Authorization').split(' ')[1]
        token = Token.objects.get(key=token_key)
        token.delete()
        return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def user_register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --------------------------------- CSV Upload ---------------------------------

@api_view(['POST'])
def upload_csv(request):
    csv_url = request.data.get('url')
    if not csv_url:
        return JsonResponse({"error": "CSV URL is required"}, status=400)
    
    try:
        result = save_to_database(csv_url)
        if result:
            return Response({'message': 'CSV Uploaded', 'columns': result})
        return JsonResponse({"error": "Failed to upload CSV", "message": result}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# --------------------------------- Game Data ---------------------------------

class GameDataQueryView(APIView):

    @staticmethod
    def _get_system_message():
        return (
            'You are a Data Scientist Who writes SQL queries for PostgreSQL. '
            'I will send you a natural language query and you need to write the SQL query to get the user desired results from the Django SQLite database. '
            'The table name: api_gamedata '
            'The columns of this table are: '
            'AppID (IntegerField, primary_key=True), '
            'Name (CharField), '
            'Release_date (DateField), '
            'Required_age (IntegerField), '
            'Price (DecimalField), '
            'DLC_count (IntegerField), '
            'About_the_game (TextField), '
            'Supported_languages (TextField), '
            'Windows (BooleanField), '
            'Mac (BooleanField), '
            'Linux (BooleanField), '
            'Positive (IntegerField), '
            'Negative (IntegerField), '
            'Score_rank (CharField), '
            'Developers (TextField), '
            'Publishers (TextField), '
            'Categories (TextField), '
            'Genres (TextField), '
            'Tags (TextField). '
            'Send the response in the following JSON format - { query: <Query>}'
        )

    def get(self, request, *args, **kwargs):
        query_params = request.query_params

        if not query_params:
            return Response({'error': 'No query parameters provided'}, status=status.HTTP_400_BAD_REQUEST)

        field = query_params.get('field')
        value = query_params.get('value')
        operator = query_params.get('operator', '=')

        if not field:
            return Response({'error': 'Field is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not hasattr(GameData, field):
            return Response({'error': f'Invalid field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            search_results = get_search_results(field, operator, value) if value is not None else None
            aggregate_results = get_aggregate_results(field)
            constrained_aggregate_results = None

            if GameData._meta.get_field(field).get_internal_type() in ['IntegerField', 'FloatField', 'DecimalField'] and value is not None:
                constrained_aggregate_results = get_constrained_aggregate_results(field, operator, value)

            return Response({
                'search_results': search_results,
                'aggregate_results': aggregate_results,
                'constrained_aggregate_results': constrained_aggregate_results
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            
            query = ''
            client = OpenAI(
                api_key= str(os.getenv('OPENAI_API_KEY')),)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # "gpt-3.5-turbo-0125", #"gpt-3.5-turbo",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_message()
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
                data = json.loads(generated_text)
                query = data["query"] 
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