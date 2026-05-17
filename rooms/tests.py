from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Booking, Room


def make_room(**kwargs):
    defaults = {
        'title': 'Test Room',
        'capacity': 4,
        'price_per_hour': 100,
        'is_active': True,
    }
    defaults.update(kwargs)
    return Room.objects.create(**defaults)


def make_user(username='user', password='pass12345', role=None):
    user = User.objects.create_user(username=username, password=password)
    if role:
        user.profile.role = role
        user.profile.save()
    return user


class BookingModelTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.room = make_room()
        self.now = timezone.now().replace(microsecond=0)

    def test_create_booking_ok(self):
        b = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2),
        )
        self.assertEqual(b.status, Booking.STATUS_PENDING)

    def test_end_before_start_invalid(self):
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                user=self.user,
                room=self.room,
                start_time=self.now + timedelta(hours=2),
                end_time=self.now + timedelta(hours=1),
            )

    def test_overlap_rejected(self):
        Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=3),
        )
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                user=self.user,
                room=self.room,
                start_time=self.now + timedelta(hours=2),
                end_time=self.now + timedelta(hours=4),
            )

    def test_inactive_room_rejected(self):
        self.room.is_active = False
        self.room.save()
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                user=self.user,
                room=self.room,
                start_time=self.now + timedelta(hours=1),
                end_time=self.now + timedelta(hours=2),
            )

    def test_cancelled_does_not_block_new(self):
        b1 = Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=3),
        )
        b1.status = Booking.STATUS_CANCELLED
        b1.save()
        Booking.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.now + timedelta(hours=2),
            end_time=self.now + timedelta(hours=4),
        )


class RoleAccessTests(TestCase):
    def setUp(self):
        self.user = make_user('plain')
        self.manager = make_user('mgr', role='manager')

    def test_anonymous_cannot_open_manage(self):
        resp = self.client.get(reverse('manage_rooms'))
        self.assertEqual(resp.status_code, 302)

    def test_plain_user_forbidden_manage(self):
        self.client.login(username='plain', password='pass12345')
        resp = self.client.get(reverse('manage_rooms'))
        self.assertEqual(resp.status_code, 403)

    def test_manager_can_open_manage(self):
        self.client.login(username='mgr', password='pass12345')
        resp = self.client.get(reverse('manage_rooms'))
        self.assertEqual(resp.status_code, 200)


class APITests(TestCase):
    def setUp(self):
        self.user = make_user('apiuser')
        self.manager = make_user('apimgr', role='manager')
        self.room = make_room()
        self.client = APIClient()

    def test_rooms_list_public(self):
        resp = self.client.get('/api/rooms/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_room_create_requires_manager(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post('/api/rooms/', {
            'title': 'X', 'capacity': 1, 'price_per_hour': 10,
        }, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_room_create_as_manager(self):
        self.client.force_authenticate(self.manager)
        resp = self.client.post('/api/rooms/', {
            'title': 'X', 'capacity': 1, 'price_per_hour': 10,
        }, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_bookings_requires_auth(self):
        resp = self.client.get('/api/bookings/')
        self.assertIn(resp.status_code, (401, 403))

    def test_user_sees_only_own_bookings(self):
        other = make_user('other')
        now = timezone.now()
        Booking.objects.create(
            user=other, room=self.room,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
        )
        Booking.objects.create(
            user=self.user, room=self.room,
            start_time=now + timedelta(hours=3),
            end_time=now + timedelta(hours=4),
        )
        self.client.force_authenticate(self.user)
        resp = self.client.get('/api/bookings/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_create_booking_via_api(self):
        self.client.force_authenticate(self.user)
        now = timezone.now()
        resp = self.client.post('/api/bookings/', {
            'room': self.room.pk,
            'start_time': (now + timedelta(hours=1)).isoformat(),
            'end_time': (now + timedelta(hours=2)).isoformat(),
        }, format='json')
        self.assertEqual(resp.status_code, 201, resp.content)

    def test_create_booking_overlap_rejected_via_api(self):
        now = timezone.now()
        Booking.objects.create(
            user=self.user, room=self.room,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3),
        )
        self.client.force_authenticate(self.user)
        resp = self.client.post('/api/bookings/', {
            'room': self.room.pk,
            'start_time': (now + timedelta(hours=2)).isoformat(),
            'end_time': (now + timedelta(hours=4)).isoformat(),
        }, format='json')
        self.assertEqual(resp.status_code, 400)
