from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from rooms.models import Booking, Room
from users.models import Profile


ROOMS = [
    {
        'title': 'Tokyo',
        'description': 'Уютная переговорная для небольших встреч в восточном стиле.',
        'capacity': 4,
        'location': 'Москва, ул. Тверская, 1',
        'price_per_hour': 500,
    },
    {
        'title': 'Berlin',
        'description': 'Просторная переговорная с панорамными окнами.',
        'capacity': 10,
        'location': 'Москва, ул. Арбат, 24',
        'price_per_hour': 1200,
    },
    {
        'title': 'Lisbon',
        'description': 'Тихая переговорная для индивидуальных интервью.',
        'capacity': 2,
        'location': 'Санкт-Петербург, Невский, 100',
        'price_per_hour': 300,
    },
    {
        'title': 'New York',
        'description': 'Большой зал для презентаций и тренингов.',
        'capacity': 20,
        'location': 'Москва, Пресненская наб., 12',
        'price_per_hour': 2400,
    },
    {
        'title': 'Reykjavik',
        'description': 'Архивная переговорная, временно не активна.',
        'capacity': 6,
        'location': 'Казань, Баумана, 19',
        'price_per_hour': 700,
        'is_active': False,
    },
]


USERS = [
    {'username': 'user1', 'password': 'user12345', 'email': 'user1@example.com', 'role': Profile.ROLE_USER},
    {'username': 'manager1', 'password': 'manager12345', 'email': 'manager1@example.com', 'role': Profile.ROLE_MANAGER},
    {'username': 'admin1', 'password': 'admin12345', 'email': 'admin1@example.com', 'role': Profile.ROLE_ADMIN, 'is_staff': True, 'is_superuser': True},
]


class Command(BaseCommand):
    help = 'Создаёт идемпотентный набор тестовых данных (комнаты, пользователи, бронирования).'

    def handle(self, *args, **options):
        rooms = self._seed_rooms()
        users = self._seed_users()
        self._seed_bookings(users, rooms)
        self.stdout.write(self.style.SUCCESS('seed_data: готово.'))

    def _seed_rooms(self):
        rooms = {}
        for data in ROOMS:
            room, created = Room.objects.update_or_create(
                title=data['title'],
                defaults=data,
            )
            rooms[room.title] = room
            self.stdout.write(f'  room {"+" if created else "="} {room.title}')
        return rooms

    def _seed_users(self):
        users = {}
        for data in USERS:
            username = data['username']
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': data.get('email', ''),
                    'is_staff': data.get('is_staff', False),
                    'is_superuser': data.get('is_superuser', False),
                },
            )
            if created:
                user.set_password(data['password'])
                user.save()
            user.profile.role = data['role']
            user.profile.save()
            users[username] = user
            self.stdout.write(f'  user {"+" if created else "="} {username} ({data["role"]})')
        return users

    def _seed_bookings(self, users, rooms):
        user1 = users['user1']
        manager1 = users['manager1']

        # Демо-брони хранятся «на завтра/послезавтра» относительно текущего дня —
        # чтобы данные оставались актуальными при повторных запусках. Чтобы
        # время не плавало по часам внутри одного дня, сначала удаляем старые
        # тестовые брони этих пользователей и создаём свежие.
        Booking.objects.filter(user__in=[user1, manager1]).delete()

        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        scenarios = [
            (user1,    rooms['Tokyo'],    today + timedelta(days=1, hours=10), today + timedelta(days=1, hours=11), Booking.STATUS_CONFIRMED),
            (user1,    rooms['Berlin'],   today + timedelta(days=2, hours=14), today + timedelta(days=2, hours=16), Booking.STATUS_CONFIRMED),
            (manager1, rooms['New York'], today + timedelta(days=3, hours=9),  today + timedelta(days=3, hours=11), Booking.STATUS_PENDING),
        ]
        for owner, room, start, end, status in scenarios:
            Booking.objects.create(
                user=owner,
                room=room,
                start_time=start,
                end_time=end,
                status=status,
            )
            self.stdout.write(f'  booking = {owner.username} {room.title} {start:%Y-%m-%d %H:%M}')
