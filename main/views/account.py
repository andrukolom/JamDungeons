from django.contrib import messages

from main.forms import VisibilityForm, EditUserForm
from main.models import Quest, Support_messages, Favorite, User, Character, Location
from django.shortcuts import render, redirect
from main.views.views import get_base_context

def account_page(request):
    context = get_base_context(request)
    favorite_quests = Favorite.objects.filter(user=context['user'])
    context['created_quests'] = Quest.objects.filter(author_id=context['user'].id)
    context['favorites'] = [quest.quest for quest in favorite_quests]
    context['experience'] = context['user'].experience % 1000
    context['level'] = context['user'].experience // 1000
    context['percent'] = context['experience'] // 10

    characters = Character.objects.filter(user=context["user"].id)
    for character in characters:
        character.quest = Quest.objects.get(id=character.quest_id)
        character.locations_count = Location.objects.filter(
            quest_id=character.quest_id
        ).count()
    context["users_character"] = characters


    if len(context['created_quests']) == 0:
        context['created_quests'] = 0
    else:
        list_data = []
        for item in Quest.objects.filter(author_id=context['user'].id):
            list_data.append(
                {'tag': item.tag.split(' '),
                 'name': item.name,
                 'form': VisibilityForm(),
                 'start_location': item.start_location,
                 'image': item.image,
                 'rating': str(round(item.rating, 1))})
            context['created_quests'] = list_data

    messages_data = [{'text': item.text, 'data': item.data,
                      'email': item.email} for item in Support_messages.objects.filter(user=context['user'])]
    context['support_messages'] = messages_data
    context['visibility_form'] = VisibilityForm()

    if request.method == "POST":
        form = EditUserForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=context['user'].id)

            if (len(User.objects.filter(username=form.data['username']).exclude(id=user.id)) or
                    User.objects.filter(email=form.data['email']).exclude(id=user.id)):

                messages.add_message(request, messages.ERROR, "Пользователь с такими данными уже существует!")
                return render(request, 'account.html', context)

            user.username = form.data['username']
            user.email = form.data['email']

            user.save()
            context['user'] = user

    context['edit_user_form'] = EditUserForm(initial={
        'username': context['user'].username,
        'email': context['user'].email
    }
    )

    return render(request, 'account.html', context)