from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import HttpResponseNotFound, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView

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


def user_search(request):
    term = request.GET.get('q', '')
    users = get_user_model().objects.filter(username__icontains=term)[:10]
    results = [{'id': user.id, 'text': user.username} for user in users]
    return JsonResponse({'results': results})


class ShowChannelsView(DataMixin, ListView):
    template_name = 'messenger/channels.html'
    context_object_name = 'channels'
    title_page = 'Доступные чаты'
    paginate_by = 10

    def get_queryset(self):
        return Channel.public_channels.all()


class ShowChatView(DataMixin, DetailView):
    model = Channel
    template_name = 'messenger/chat.html'
    slug_url_kwarg = 'chat_slug'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(channel=context['channel']).order_by('time_create')
        # title - ключ, который сформируется
        return self.get_mixin_context(context, title=f"Чат - {context['channel'].name}")


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
