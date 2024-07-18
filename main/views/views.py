import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect
from main.forms import Support, LoginForm, ComplaintForm
from main.models import Character
from main.models import Location, Connect_location
from main.models import Quest

def get_base_context(request):
    """
    Функция получения базового контекста

    Создает словарь базового контекста

    :param request: запрос с сайта
    :type request: :class:`django.http.HttpRequest`
    :param pagename: имя страницы
    :type pagename: str
    :return: словарь с полями `pagename`, `loginform`, `user`
    :rtype: dict
    """
    return {
        'loginform': LoginForm(),
        'supportform': Support(),
        'user': request.user,
        "complaintform": ComplaintForm(),
        "is_staff": request.user.is_staff,
    }

def index_page(request):
    """
    Основная функция логики главной страницы

    Создает базовый контекст

    Берет из базы данных список квестов и добавляет в контекст данные о квестах: id, title, author, start_location

    :param request: запрос с сайта
    :type request: :class:`django.http.HttpRequest`
    :return: render страницы ``pages/index.html`` с контекстом
    :rtype: :class:`django.http.HttpResponse`
    """

    context = get_base_context(request)
    request.session.pop("character_id", False)
    data = Quest.objects.exclude(status=0, visibility=0)
    stories = [
        {
            "id": item.id,
            "title": item.name,
            "author": item.author,
            "start_location": item.start_location,
            "image": item.image,
            "status": "",
        }
        for item in data
    ]
    if len(stories) != 0:
        stories[0]['status'] = "active"
    context["first_carousel"] = [stories[i : i + 4] for i in range(0, len(stories), 4)]

    return render(request, "pages/index.html", context)

def catalog_page(request):
    context = get_base_context(request)
    context['up_title'] = "Полный каталог квестов:"
    data = Quest.objects.exclude(status=0, visibility=0)
    stories = [
        {
            "id": item.id,
            "name": item.name,
            "author": item.author,
            "start_location": item.start_location,
            "image": item.image,
            'rating': str(round(item.rating, 1))
        }
        for item in data
    ]
    context['stories'] = stories
    context['back_btn'] = "invisible"
    return render(request, 'pages/catalog.html', context)

def navigator_to_locations(location_id: int = 0):
    connects_from = Connect_location.objects.filter(to_location=location_id)
    before_before_alfa_locations = []
    for connect in connects_from:
        for i in Connect_location.objects.filter(from_location=connect.from_location):
            before_before_alfa_locations.append(i)
    alfa_locations = []
    for connect in before_before_alfa_locations:
        for i in Location.objects.filter(id=connect.to_location):
            alfa_locations.append(i)
    return alfa_locations
def navigator_from_locations(location_id: int = 0):
    connects_from = Connect_location.objects.filter(to_location=location_id)
    from_locations = []
    for connect in connects_from:
        for i in Location.objects.filter(id=connect.from_location):
            from_locations.append(i)
    return(from_locations)

@login_required(redirect_field_name=None)
def passage_story(request, location_id):
    location = Location.objects.get(id=location_id)
    character_id = request.session.get("character_id", False)
    quest = Quest.objects.get(id=Location.objects.get(id=location_id).quest_id)

    if quest.status == 6 and request.user.is_staff != True:
        messages.add_message(request, messages.WARNING, "Данный квест был забанен")
        redirect("index")

    if not request.session.get("character_id", False):
        return redirect("character", quest_id=location.quest_id)

    context = get_base_context(request)

    character = Character.objects.get(id=character_id)
    if location_id != character.location_now_id:
        next_locations = Connect_location.objects.filter(
            from_location=character.location_now_id
        )
        next_locations_id = [location.to_location for location in next_locations]
        if location_id not in next_locations_id:
            return redirect("passage_story", location_id=character.location_now_id)

    vote1 = Location.objects.get(id=location_id)
    actions = Connect_location.objects.filter(from_location=location_id)
    context["quest_id"] = vote1.quest_id
    context["story_name"] = quest.name
    context["text"] = vote1.text
    context["story"] = vote1
    context["number_of_actions"] = vote1.count_connections
    context["actions"] = actions
    context["is_ban"] = quest.status == 1
    context["location_id"] = location_id
    context["the_end"] = vote1.the_end

    request.user.experience += 50
    request.user.save()

    character.location_now_id = location_id
    character.save()

    return render(request, "pages/passage_story.html", context)


@login_required(redirect_field_name=None)
def choose_character(request, quest_id):
    context = get_base_context(request)
    if request.method == "GET":
        characters = Character.objects.filter(user=request.user, quest_id=quest_id)

        context["quest_id"] = quest_id
        context["characters"] = characters

        return render(request, "pages/character.html", context)
    if request.method == "POST":
        character_id = request.POST.get("character", None)
        if character_id is None:
            return HttpResponseNotFound()

        quest = Quest.objects.get(id=quest_id)
        if character_id == "0":
            character_name = request.POST.get("character_name", "test")
            character_obj = Character(
                name=character_name,
                user=request.user,
                quest_id=quest_id,
                location_now_id=quest.start_location,
                progress=0
            )
            character_obj.save()
        else:
            character_obj = Character.objects.get(id=character_id)
        request.session["character_id"] = character_obj.id
        return redirect("passage_story", location_id=character_obj.location_now_id)

@login_required(redirect_field_name=None)
def activate_telegram(request):
    if request.user.telegram_id is not None:
        return JsonResponse({"error": "Тг уже подключен"})
    if not request.user.telegram_token:
        request.user.generate_token()
        request.user.save()
    return JsonResponse({"key": request.user.telegram_token})
