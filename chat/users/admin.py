from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_html_photo', 'is_moderator', 'is_blocked', 'is_active', 'email')
    list_display_links = ('username', )
    search_fields = ('^username', '^email')
    list_editable = ('is_moderator', 'is_blocked', 'is_active')
    list_filter = ('is_moderator', 'is_blocked', 'is_active')
    fieldsets = (
        ('Основная информация',
         {'fields': ('username', 'slug', 'first_name', 'last_name', 'email', 'date_birth', 'content')}),
        ('Фото', {'fields': ('photo', 'get_html_photo')}),
        ('Права доступа', {'fields': ('is_staff', 'is_superuser', 'is_active', 'is_moderator', 'is_blocked')}),
        ('Пароль', {'fields': ('password',)}),
        ('Даты и статусы', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('get_html_photo', )
    # readonly_fields = ('username', 'slug', 'first_name', 'last_name', 'email', 'date_birth', 'content',
    #                    'photo', 'get_html_photo', 'password', 'last_login', 'date_joined')
    ordering = ['date_joined', 'username']
    list_per_page = 15
    actions = ['set_moderator', 'remove_moderator', 'set_blocked', 'set_unblocked', 'set_active', 'set_inactive']
    save_on_top = True

    @admin.display(description="Мини фото")
    def get_html_photo(self, user: User):
        """Отображение мини фото в админке"""
        if user.photo:
            return mark_safe(f"<img src='{user.photo.url}' width=50 height=50>")
        return "Фото отсутствует"

    @admin.action(description="Назначить выбранных пользователей модераторами")
    def set_moderator(self, request, queryset):
        count = queryset.update(is_moderator=True)
        self.message_user(request, f"Назначено модераторами: {count} пользователей")

    @admin.action(description="Снять выбранных пользователей из модераторов")
    def remove_moderator(self, request, queryset):
        count = queryset.update(is_moderator=False)
        self.message_user(request, f"Снято из модераторов: {count} пользователей", messages.WARNING)

    @admin.action(description="Заблокировать выбранных пользователей")
    def set_blocked(self, request, queryset):
        count = queryset.update(is_blocked=True)
        self.message_user(request, f"Заблокировано: {count} пользователей", messages.WARNING)

    @admin.action(description="Разблокировать выбранных пользователей")
    def set_unblocked(self, request, queryset):
        count = queryset.update(is_blocked=False)
        self.message_user(request, f"Разблокировано: {count} пользователей")

    @admin.action(description="Сделать активными выбранных пользователей")
    def set_active(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Сделано активными: {count} пользователей")

    @admin.action(description="Сделать неактивными выбранных пользователей")
    def set_inactive(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"Сделано неактивными: {count} пользователей", messages.WARNING)

    class Media:
        js = ('js/admin/slug_autofill_user.js',)
