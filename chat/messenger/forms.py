from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField, CaptchaTextInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Channel


class AddChannelForm(forms.ModelForm):
    # Конструктор класса
    # def __init__(self, *arg, **kwargs):
    #     # Вызываем конструктор базового класса
    #     super().__init__(*arg, **kwargs)
    #     # Меняем свойства полей
    #     # При выпадении списка, в начале вместо "----" пишется это:
    #     self.fields['cat'].empty_label = "Категория не выбрана"

    class Meta:
        model = Channel
        fields = ['name', 'slug', 'description', 'is_private', 'users']
        # Стили оформления
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название канала'}),
            'slug': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Заполниться автоматически, можно редактировать'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'type': 'text',
                                                 'rows': 5,
                                                 'placeholder': 'Любая информация о канале'}),
            'is_private': forms.Select(attrs={'class': 'form-select'}),
            'users': forms.SelectMultiple(attrs={'class': 'form-select select2-users'}),
        }

    def clean_name(self):
        # Получаем данные поля
        name = self.cleaned_data['name']
        if len(name) > 200:
            # Генерируется исключение
            raise ValidationError('Длина превышает 200 символов')

        return name


class FeedbackForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=255,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Ваше имя'}))
    email = forms.CharField(label='Email',
                            widget=forms.EmailInput(attrs={'class': 'form-control',
                                                           'placeholder': 'Почта для связи'}))
    content = forms.CharField(label='Информация',
                              widget=forms.Textarea(attrs={'class': 'form-control',
                                                           'type': 'text',
                                                           'rows': 5,
                                                           'placeholder': 'Любая информация'}))
    # графическая картинка с кодом
    captcha = CaptchaField(label='Введите текст с картинки',
                           widget=CaptchaTextInput(attrs={'class': 'form-control',
                                                          'placeholder': 'Введите текст с картинки'}))
