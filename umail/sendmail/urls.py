from django.contrib import admin
from django.urls import path
from sendmail import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
]
