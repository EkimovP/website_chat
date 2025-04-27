menu = [{'title': 'Главная страница', 'url_name': 'home'},
        {'title': 'Просмотр доступных чатов', 'url_name': 'channels'},
        {'title': 'Создание канала', 'url_name': 'add_channel'},
        {'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Обратная связь', 'url_name': 'feedback'}]


class DataMixin:
    title_page = None
    extra_context = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page

        # Если не изменяемое меню
        if 'menu' not in self.extra_context:
            self.extra_context['menu'] = menu

    def get_mixin_context(self, context, **kwargs):
        context['menu'] = menu
        context.update(kwargs)

        return context
