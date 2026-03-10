from django.shortcuts import render
from .services import get_all_rooms


def room_list(request):
    rooms = get_all_rooms()
    return render(request, 'rooms/room_list.html', {'rooms': rooms})


def profile_view(request):
    return render(request, 'rooms/profile.html')
