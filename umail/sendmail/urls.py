from django.contrib import admin
from django.urls import path
from sendmail import views


urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("process-csv/", views.process_csv, name="process_csv"),
    path("analytics/", views.analytics, name="analytics"),
    path('settings',views.settings,name='settings'),
    path('generate-text/',views.gemini_prompt,name='generate-text'),
]
