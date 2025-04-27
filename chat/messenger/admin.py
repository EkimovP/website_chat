from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Channel, Message


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_private', 'short_description', 'creation', 'display_users')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name', 'creation', 'is_private')
    list_editable = ('is_private',)
    readonly_fields = ('creation',)
    fields = ('name', 'slug', 'description', 'is_private', 'users')
    filter_horizontal = ('users',)
    ordering = ['-creation', 'name']
    list_per_page = 15
    actions = ['set_private', 'remove_private']

    @admin.display(description="Краткое описание канала")
    def short_description(self, channel: Channel):
        """Отображение краткого описания канала"""
        if channel.description:
            if len(channel.description) > 30:
                return channel.description[:30] + "..."
            else:
                return channel.description
        else:
            return "Описание канала отсутствует"

    @admin.display(description="Участники")
    def display_users(self, channel: Channel):
        """Отображение списка пользователей в канале"""
        return ", ".join([user.username for user in channel.users.all()])

    @admin.action(description="Сделать выбранные каналы приватными")
    def set_private(self, request, queryset):
        count = queryset.update(is_private=True)
        self.message_user(request, f"Сделано приватными: {count} каналов")

    @admin.action(description="Сделать выбранные каналы публичными")
    def remove_private(self, request, queryset):
        count = queryset.update(is_private=False)
        self.message_user(request, f"Сделано публичными: {count} каналов", messages.WARNING)

    class Media:
        js = ('js/admin/slug_autofill_channel.js',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'channel', 'user', 'time_create', 'time_update', 'is_edited')
    list_display_links = ('short_content', )
    search_fields = ('^user__username', 'channel__name')
    list_filter = ('time_create', 'time_update')
    fields = ('content', 'channel', 'user', 'time_create', 'time_update', 'is_edited')
    # readonly_fields = ('channel', 'user', 'time_create', 'time_update', 'is_edited')
    readonly_fields = ('time_create', 'time_update', 'is_edited')
    ordering = ['time_create']
    list_per_page = 15

    @admin.display(description="Краткое сообщение")
    def short_content(self, message: Message):
        """Отображение краткого сообщения"""
        return message.content[:20] + "..." if len(message.content) > 20 else message.content

    def save_model(self, request, message: Message, form, change):
        if message.user not in message.channel.users.all():
            raise ValidationError("Этот пользователь не является участником канала и не может отправлять сообщения.")
        if change:
            message.is_edited = True
        super().save_model(request, message, form, change)
