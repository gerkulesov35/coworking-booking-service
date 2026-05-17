from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Room(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')
    location = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Локация',
    )
    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Цена за час',
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    image = models.ImageField(
        upload_to='rooms/',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Переговорная'
        verbose_name_plural = 'Переговорные'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_CONFIRMED, 'Подтверждено'),
        (STATUS_CANCELLED, 'Отменено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Пользователь',
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Переговорная',
    )
    start_time = models.DateTimeField(verbose_name='Начало')
    end_time = models.DateTimeField(verbose_name='Окончание')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.room}: {self.user} ({self.start_time:%Y-%m-%d %H:%M})'

    def clean(self):
        errors = {}

        if self.start_time and self.end_time and self.end_time <= self.start_time:
            errors['end_time'] = 'Окончание должно быть позже начала.'

        if self.room_id and not self.room.is_active:
            errors['room'] = 'Нельзя бронировать неактивную переговорную.'

        if self.room_id and self.start_time and self.end_time:
            overlap_qs = Booking.objects.filter(
                room=self.room,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(status=self.STATUS_CANCELLED)
            if self.pk:
                overlap_qs = overlap_qs.exclude(pk=self.pk)
            if overlap_qs.exists():
                errors['__all__'] = 'Это время уже занято для выбранной переговорной.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
