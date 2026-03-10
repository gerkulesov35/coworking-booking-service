from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.name
