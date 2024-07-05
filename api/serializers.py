from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GameData

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class GameDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameData
        fields = '__all__'