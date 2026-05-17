from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from rooms.api_views import BookingListAPIView, RoomDetailAPIView, RoomListAPIView


urlpatterns = [
    path('rooms/', RoomListAPIView.as_view(), name='api_rooms'),
    path('rooms/<int:pk>/', RoomDetailAPIView.as_view(), name='api_room_detail'),
    path('bookings/', BookingListAPIView.as_view(), name='api_bookings'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
