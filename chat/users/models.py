from django.db import models
from unidecode import unidecode
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser, BaseUserManager


# class CustomUserManager(BaseUserManager):
#     def get_by_natural_key(self, username):
#         return self.get(username=username)
#
#
# class ModeratorsManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(is_moderator=True)
#
#
# class UnblockedManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(is_blocked=False)


class User(AbstractUser):
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='url')
    is_moderator = models.BooleanField(default=False, verbose_name='модератор')
    is_blocked = models.BooleanField(default=False, verbose_name='заблокирован')
    photo = models.ImageField(blank=True, null=True, upload_to="photo/%Y/%m/%d/", verbose_name='фото')
    date_birth = models.DateField(blank=True, null=True, verbose_name='дата рождения')
    content = models.TextField(max_length=2000, blank=True, verbose_name='дополнительная информация')

    # objects = CustomUserManager()
    # moderators = ModeratorsManager()
    # unblocked = UnblockedManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Возвращается полное имя пользователя"""
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated = unidecode(self.username).lower()
            self.slug = slugify(transliterated)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']
