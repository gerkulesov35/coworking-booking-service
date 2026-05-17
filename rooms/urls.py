from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('slow/', views.slow_view, name='slow_view'),

    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/book/', views.booking_create, name='booking_create'),

    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),

    path('manage/rooms/', views.manage_rooms, name='manage_rooms'),
    path('manage/rooms/new/', views.room_create, name='room_create'),
    path('manage/rooms/<int:pk>/edit/', views.room_update, name='room_update'),
    path('manage/rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),

    path('manage/bookings/', views.manage_bookings, name='manage_bookings'),
    path('manage/bookings/<int:pk>/status/', views.booking_set_status, name='booking_set_status'),
]
