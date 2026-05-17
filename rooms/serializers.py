from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Booking, Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id', 'title', 'description', 'capacity', 'location',
            'price_per_hour', 'is_active', 'image', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    room_title = serializers.CharField(source='room.title', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'room', 'room_title',
            'start_time', 'end_time', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'room_title']

    def validate(self, attrs):
        instance = Booking(
            user=self.context['request'].user,
            room=attrs.get('room'),
            start_time=attrs.get('start_time'),
            end_time=attrs.get('end_time'),
        )
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)
        return attrs
