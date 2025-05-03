from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView

from .forms import AddChannelForm, FeedbackForm
from .models import Channel, Message
from .utils import DataMixin


class HomeView(DataMixin, TemplateView):
    template_name = 'messenger/index.html'
    title_page = 'Главная страница'


class AboutView(DataMixin, TemplateView):
    template_name = 'messenger/about.html'
    title_page = 'О сайте'


class FeedbackFormView(DataMixin, FormView):
    form_class = FeedbackForm
    template_name = 'messenger/feedback.html'
    success_url = reverse_lazy('home')
    title_page = 'Обратная связь'

    def form_valid(self, form):
        print(form.cleaned_data)
        return redirect('home')


# class AddChannelFormView(LoginRequiredMixin, DataMixin, FormView):
#     form_class = AddChannelForm
#     template_name = 'messenger/add_channel.html'
#     success_url = reverse_lazy('channels')
#     title_page = 'Создание канала'
#
#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)


class AddChannelFormView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddChannelForm
    template_name = 'messenger/add_channel.html'
    title_page = 'Создание канала'

    def form_valid(self, form):
        channel = form.save(commit=False)
        channel.creator = self.request.user
        channel.save()
        # Т.к. имеется поле многие ко многим
        form.save_m2m()
        return super().form_valid(form)


@login_required
def user_search(request):
    term = request.GET.get('q', '')
    users = get_user_model().objects.filter(username__icontains=term)[:10]
    results = [{'id': user.id, 'text': user.username} for user in users]
    return JsonResponse({'results': results})


class UpdateChannelFormView(LoginRequiredMixin, DataMixin, UpdateView):
    form_class = AddChannelForm
    template_name = 'messenger/add_channel.html'
    title_page = 'Редактирование канала'
    slug_url_kwarg = 'update_slug'

    def get_queryset(self):
        return Channel.objects.filter(creator=self.request.user)

    def get_success_url(self):
        return reverse_lazy('chat', kwargs={'chat_slug': self.object.slug})

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Channel.DoesNotExist:
            return HttpResponseNotFound('Канал не найден')


class DeleteChannelView(LoginRequiredMixin, DataMixin, DeleteView):
    model = Channel
    template_name = 'messenger/delete_channel.html'
    success_url = reverse_lazy('channels')
    title_page = 'Удаление канала'
    slug_url_kwarg = 'delete_slug'

    def get_queryset(self):
        return Channel.objects.filter(creator=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.creator != request.user:
            return HttpResponseNotFound('У вас нет прав для удаления этого канала')
        return super().get(request, *args, **kwargs)


class ShowChannelsView(DataMixin, ListView):
    template_name = 'messenger/channels.html'
    context_object_name = 'channels'
    title_page = 'Доступные чаты'
    paginate_by = 10

    def get_queryset(self):
        return Channel.public_channels.all()


class ShowChatView(LoginRequiredMixin, DataMixin, DetailView):
    model = Channel
    template_name = 'messenger/chat.html'
    slug_url_kwarg = 'chat_slug'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = (Message.objects.filter(channel=context['channel']).select_related('user')
                               .order_by('time_create')[:100])
        # title - ключ, который сформируется
        return self.get_mixin_context(context, title=f"Чат - {context['channel'].name}")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.users.filter(id=request.user.id).exists():
            return HttpResponseForbidden("Вы не участник этого канала")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
