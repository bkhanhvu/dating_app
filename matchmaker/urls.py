from django.urls import path
from . import views

urlpatterns = [
    path('profile/create/', views.profile_create, name='profile_create'),
    path('matches/', views.matches_list, name='matches_list'),
]
