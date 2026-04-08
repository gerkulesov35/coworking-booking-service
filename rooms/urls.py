from django.urls import path
from .views import room_list, slow_view

urlpatterns = [
    path('', room_list, name='room_list'),
    path('slow/', slow_view, name='slow_view'),
]