from rest_framework import generics, permissions

from .api_permissions import IsManagerOrReadOnly
from .models import Booking, Room
from .serializers import BookingSerializer, RoomSerializer


class RoomListAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsManagerOrReadOnly]


class RoomDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsManagerOrReadOnly]


class BookingListAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related('room', 'user')
        profile = getattr(user, 'profile', None)
        if profile and profile.is_manager:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
