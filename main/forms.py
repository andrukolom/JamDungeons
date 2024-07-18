from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CreateQuestForm(forms.Form):
    name = forms.CharField(
        label="Название вашего квеста",
        max_length=64,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Например: Ведьминское подземелье",
                "style": "height: 3rem",
            }
        ),
    )
    description = forms.CharField(
        label="Описание вашего квеста",
        max_length=2000,
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "style": "width:fill; height: 70px;",
                "placeholder": "Например: В этом подземелье тебе придётся разгадать загадки и головоломки, которые подготовил для тебя шабаш старых ведьм.",
            }
        ),
    )
    tag = forms.CharField(
        label="Жанры, теги и ключевые слова",
        max_length=100,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "style": "width:fill; height: 50px;",
                "placeholder": "Пример: #Романтика #Драмма #Повседневность #Зомби"
            }
        ),
    )
    image = forms.ImageField(
        label="Обложка квеста:",
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        )
    )



class CreateActionForm(forms.Form):
    action = forms.CharField(
        label="Действие",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введте название, после сохранения, будет доступна настройка действий"
            }
        ),
    )
    id: int
    to_location: 0

    def __init__(self, *args, **kwargs):
        id = kwargs.pop("id", None)
        to_location = kwargs.pop("to_location", None)
        super(CreateActionForm, self).__init__(*args, **kwargs)

        if id:
            self.id = id
        if to_location:
            self.to_location = to_location

CHOICES = {0: "Сцена с действиями", 1: "Финальная сцена"}

class VisibilityForm(forms.Form):
    CHOICES_V = {0: "Приватный", 1: "Публичный"}
    visibility = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        choices=CHOICES_V
    )

class CreateLocationForm(forms.Form):

    history = forms.CharField(
        label="Описание и история к локации",
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "",
                "style": "height: 100px; min-height: 60px; width: 100%;",
            }
        ),
    )
    name = forms.CharField(
        label="Название локации",
        max_length=64,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Например: Волшебный лес эльфов",
            }
        ),
    )
    countActions = forms.IntegerField(
        label="Количество вариантов действия",
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "disabled": False,
            }
        ),
    )
    final_location = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        choices=CHOICES
    )
    actions: [CreateActionForm()]

    def __init__(self, *args, **kwargs):
        actions = kwargs.pop("actions", None)
        current_min_value = kwargs.pop("current_min_value", None)
        super(CreateLocationForm, self).__init__(*args, **kwargs)

        if actions:
            self.actions = actions
        if current_min_value:
            self.fields["countActions"].widget.attrs["min"] = current_min_value


class ComplaintForm(forms.Form):
    message = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Сообщение",
            }
        ),
    )

# РЕГИСТРАЦИЯ ЛОГИН И ПОДДЕРЖКА (ВСЁ ЧТО НА ГЛАВНОЙ СТРАНИЦЕ)

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }
        )
    )
    password = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
            }
        )
    )

class Support(forms.Form):
    email = forms.EmailField(
        label='Электронная почта',
        max_length=65,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
            }
        ),
        required=False
    )
    message = forms.CharField(
        label='Сообщение',
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder':'Подробно пишите Вашу проблему',
                'style': 'height:60px'
            }
        )
    )


class FiltersCatalog(forms.Form):
    genre = forms.ChoiceField(
        choices=[("Приключения", "Приключения"), ("Драма", "Драма"), ("Фэнтези", "Фэнтези")], widget=forms.RadioSelect,
        label="Жанр",
        required=False,
    )
    popular = forms.ChoiceField(
        choices=[(1, "1-2"), (2, "3-4"), (3, "5")], widget=forms.RadioSelect,
        label="Популярность",
        required=False,
    )
    duration = forms.ChoiceField(
        choices=[(1, "1-3"), (2, "4-6"), (3, ">= 7")], widget=forms.RadioSelect,
        label="Длительность",
        required=False,
    )
    agelimit = forms.ChoiceField(
        choices=[(1, "меньше 12"), (2, "12-16"), (3, "> 16")], widget=forms.RadioSelect,
        label="Ограничение по возрасту",
        required=False,
    )
    completed = forms.BooleanField(
        label="Отображать пройденные",
        required=False,
    )
    favourite = forms.BooleanField(
        label="Только избранные",
        required=False,
    )
    sort = forms.ChoiceField(
        choices=[
            (1, "возрастанию популярности"),
            (2, "убыванию популярности"),
        ],
        widget=forms.RadioSelect,
        label="Сортировка по",
        required=False,
    )

class EditUserForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }
        )
    )
    # image = forms.ImageField(
    #     label="Аватарка",
    #     required=False,
    #     widget=forms.FileInput(
    #         attrs={
    #             "class": "form-control",
    #         }
    #     )
    # )
    email = forms.EmailField(
        label='Адрес электронной почты',
        max_length=65,
        widget=forms.EmailInput(
        attrs={
            'class': 'form-control',
            'placeholder': "duck@dungeons.jam"
            }
        ),
    )


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({
            "class":"form-control",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
        })
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
        })
        self.fields["email"].widget.attrs.update({
            "class": "form-control",
        })

    class Meta:
        model = get_user_model()
        fields = ["username", "password1", "password2", "email"]
