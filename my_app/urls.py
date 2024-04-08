from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('details/<path:repo_url>/', views.repo_details, name='repo_details'),
]
