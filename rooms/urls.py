from django.urls import path
from .views import room_list, profile_view

urlpatterns = [
    path('', room_list, name='room_list'),
    path('profile/', profile_view, name='profile'),
]
