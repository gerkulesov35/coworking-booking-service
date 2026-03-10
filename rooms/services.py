from .models import Room


def get_all_rooms():
    return Room.objects.all()
