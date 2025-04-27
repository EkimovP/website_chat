from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


class PublicManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_private=Channel.Status.PUBLIC)


class Channel(models.Model):
    class Status(models.IntegerChoices):
        PUBLIC = 0, 'Публичный'
        PRIVATE = 1, 'Приватный'

    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='название канала')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='url')
    description = models.TextField(blank=True, verbose_name='описание канала')
    is_private = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                     default=Status.PUBLIC, verbose_name="статус канала")
    creation = models.DateTimeField(auto_now_add=True, verbose_name='создан')
    users = models.ManyToManyField(get_user_model(), related_name='member_of_channels', verbose_name='участники')

    objects = models.Manager()
    public_channels = PublicManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('chat', kwargs={'chat_slug': self.slug})

    class Meta:
        verbose_name = 'Канал'
        verbose_name_plural = 'Каналы'
        ordering = ['-creation', 'name']


class Message(models.Model):
    content = models.TextField(verbose_name='сообщение')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='создано')
    time_update = models.DateTimeField(auto_now=True, verbose_name='обновлено')
    is_edited = models.BooleanField(default=False, verbose_name='редактировано')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='messages', verbose_name='автор')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages', verbose_name='канал')

    def __str__(self):
        author = self.user.username if self.user else "Удалённый пользователь"
        short_content = (self.content[:17] + "...") if len(self.content) > 20 else self.content
        return f"{author} в {self.channel.name}: {short_content}"

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-time_create']
        indexes = [models.Index(fields=['channel', '-time_create'])]
