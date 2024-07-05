from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from . import views
urlpatterns = [
    
    path("login/",views.login, name="login"),
    path("logout/",views.logout, name="logout"),
    path("register/",views.register, name="register"),
    path("user/",views.get_user, name="user"),
    path("test_token/",views.test_token, name="test_token"),
    
    path("upload/", views.csv_upload, name="upload")
]

