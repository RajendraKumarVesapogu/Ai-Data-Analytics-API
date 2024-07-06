from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from . import views
urlpatterns = [
    
    path("login/",views.user_login, name="login"),
    path("logout/",views.user_logout, name="logout"),
    path("register/",views.user_register, name="register"),
    path("user/",views.get_user, name="user"),
    path("test_token/",views.test_token, name="test_token"),
    
    path("upload/", views.upload_csv, name="upload"),
    path('query/', views.GameDataQueryView.as_view(), name='game-data-query'),


]

