from django.contrib import admin

from .models import Booking, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'capacity', 'location', 'price_per_hour', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'room')
    search_fields = ('user__username', 'room__title')
    date_hierarchy = 'start_time'
