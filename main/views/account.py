from django.contrib import messages
from django.shortcuts import render

from main.forms import VisibilityForm, EditUserForm, QuestInformation
from main.models import (
    Quest,
    Support_messages,
    Favorite,
    User,
    Character,
    Location,
    Tags_Connect,
    ConnectAchievements,

)
from main.views.views import get_base_context, activate_telegram


def account_page(request, quest_id=None):
    context = get_base_context(request)
    favorite_quests = Favorite.objects.filter(user=context["user"])
    context["created_quests"] = Quest.objects.filter(author_id=context["user"].id)
    context["favorites"] = [quest.quest for quest in favorite_quests]
    context["experience"] = context["user"].experience % 1000
    context["level"] = context["user"].experience // 1000
    context["percent"] = context["experience"] // 10
    achievements = ConnectAchievements.objects.filter(user=context["user"])

    if quest_id:
        quest = Quest.objects.get(id=quest_id)

        tag_connect = Tags_Connect.objects.filter(quest=quest)
        tag = ""
        for item in tag_connect:
            tag += item.tag.tag

        context["quest_info_form"] = QuestInformation(
            initial={
                "name": quest.name,
                "visibility": quest.visibility,
                "image": quest.image,
                "description": quest.description,
                "agelimit": quest.agelimit,
                "tag": tag,
            },
            id=quest_id,
        )

    context["achievements"] = [
        {
            "text": item.achieve.name,
            "quest_name": Quest.objects.get(id=item.achieve.location.quest_id).name,
            "image": Quest.objects.get(id=item.achieve.location.quest_id).image,
        }
        for item in achievements
    ]

    for item in context["favorites"]:
        item.tag = [tag_connect.tag.tag for tag_connect in item.tags_connect.all()]

    context["token"] = activate_telegram(request)

    characters = Character.objects.filter(user=context["user"].id)
    for character in characters:
        character.quest = Quest.objects.get(id=character.quest_id)
        character.locations_count = Location.objects.filter(
            quest_id=character.quest_id
        ).count()
    context["users_character"] = characters

    if len(context["created_quests"]) == 0:
        context["created_quests"] = 0

    else:
        list_data = []
        for item in Quest.objects.filter(author_id=context["user"].id).prefetch_related(
            "tags_connect"
        ):
            tags_list = [tag_connect.tag.tag for tag_connect in item.tags_connect.all()]
            list_data.append(
                {
                    "tag": tags_list,
                    "name": item.name,
                    "form": VisibilityForm(),
                    "start_location": item.start_location,
                    "image": item.image,
                    "rating": str(round(item.rating, 1)),
                    "id": item.id,
                }
            )
            context["created_quests"] = list_data
    messages_data = [
        {"text": item.text, "data": item.data, "email": item.email}
        for item in Support_messages.objects.filter(user=context["user"])
    ]
    context["support_messages"] = messages_data

    if request.method == "POST":
        form = EditUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.get(id=context["user"].id)

            if len(
                User.objects.filter(username=form.data["username"]).exclude(id=user.id)
            ) or User.objects.filter(email=form.data["email"]).exclude(id=user.id):

                messages.add_message(
                    request,
                    messages.ERROR,
                    "Пользователь с такими данными уже существует!",
                )
                return render(request, "account.html", context)

            user.username = form.data["username"]
            user.email = form.data["email"]
            if form.cleaned_data["image"]:
                user.image = form.cleaned_data["image"]

            user.save()
            context["user"] = user

    context["edit_user_form"] = EditUserForm(
        initial={
            "username": context["user"].username,
            "email": context["user"].email,
            "image": context["user"].image,
        }
    )

    return render(request, "account.html", context)
