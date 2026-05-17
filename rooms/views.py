import logging
import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm, RoomForm
from .models import Booking, Room
from .permissions import manager_required
from .services import get_all_rooms


logger = logging.getLogger("app")


def home(request):
    featured_rooms = Room.objects.filter(is_active=True).order_by('-created_at')[:3]
    return render(request, 'home.html', {'featured_rooms': featured_rooms})


# ---------- existing endpoints (kept from earlier practicums) ----------

def room_list(request):
    rooms = get_all_rooms()

    logger.info(
        "Room list requested",
        extra={
            "path": request.path,
            "method": request.method,
            "status_code": 200,
        },
    )

    return render(request, 'rooms/room_list.html', {'rooms': rooms})


def slow_view(request):
    time.sleep(8)

    logger.info(
        "Slow request completed",
        extra={
            "path": request.path,
            "method": request.method,
            "status_code": 200,
        },
    )

    return HttpResponse("Slow request finished")


# ---------- room detail / booking flow ----------

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'rooms/room_detail.html', {'room': room})


@login_required
def booking_create(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method != 'POST':
        return redirect('room_detail', pk=room.pk)

    form = BookingForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Проверьте даты бронирования.')
        return redirect('room_detail', pk=room.pk)

    booking = form.save(commit=False)
    booking.room = room
    booking.user = request.user
    try:
        booking.save()
    except ValidationError as exc:
        for error in exc.messages:
            messages.error(request, error)
        return redirect('room_detail', pk=room.pk)

    messages.success(request, 'Бронирование создано.')
    return redirect('my_bookings')


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room')
    return render(request, 'rooms/booking_list.html', {
        'bookings': bookings,
        'manager_view': False,
    })


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        messages.success(request, 'Бронирование отменено.')
    return redirect('my_bookings')


# ---------- manager CRUD ----------

@manager_required
def manage_rooms(request):
    rooms = Room.objects.all()
    return render(request, 'rooms/manage_rooms.html', {'rooms': rooms})


@manager_required
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Переговорная создана.')
            return redirect('manage_rooms')
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form, 'room': None})


@manager_required
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Переговорная обновлена.')
            return redirect('manage_rooms')
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html', {'form': form, 'room': room})


@manager_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Переговорная удалена.')
        return redirect('manage_rooms')
    return render(request, 'rooms/room_confirm_delete.html', {'room': room})


@manager_required
def manage_bookings(request):
    bookings = Booking.objects.select_related('room', 'user').all()
    return render(request, 'rooms/booking_list.html', {
        'bookings': bookings,
        'manager_view': True,
        'status_choices': Booking.STATUS_CHOICES,
    })


@manager_required
def booking_set_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = {key for key, _ in Booking.STATUS_CHOICES}
        if new_status in valid:
            booking.status = new_status
            booking.save()
            messages.success(request, 'Статус обновлён.')
    return redirect('manage_bookings')
