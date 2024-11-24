import datetime
import random

from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import (
    Character,
    Tags_Connect,
    Location,
    Connect_location,
    Quest,
    Rating,
    Favorite,
    ConnectAchievements,
    Achievements,
)
from main.forms import Support, LoginForm, ComplaintForm, RateForm, FiltersCatalog


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
    data = Quest.objects.exclude(status=0, visibility=0)
    random.seed()
    current_date_time = datetime.datetime.now()
    current_time = current_date_time.time()
    random.seed(str(current_time)[-4:-2])

    if data:

        return {
            "loginform": LoginForm(),
            "supportform": Support(),
            "user": request.user,
            "complaintform": ComplaintForm(),
            "is_staff": request.user.is_staff,
            "random": data[random.randint(0, len(data) - 1)].id,
        }
    return {
        "loginform": LoginForm(),
        "supportform": Support(),
        "user": request.user,
        "complaintform": ComplaintForm(),
        "is_staff": request.user.is_staff,
    }


def genre_sort(stories: list, genre: str):
    sorted_stories = []
    for story in stories:
        for tag in story["tags"]:
            if tag.tag.tag.lower() == genre:
                sorted_stories.append(story)

    return sorted_stories


def slide_stories(stories):
    if len(stories) != 0:
        stories[0]["status"] = "active"

    return [stories[i : i + 4] for i in range(0, len(stories), 4)]


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
    if request.user.is_authenticated:
        request.session.pop("character_id", False)
        if not context["user"].is_staff or not context["user"]:
            data = Quest.objects.exclude(visibility=0).exclude(status=0)
        else:
            data = Quest.objects.exclude(visibility=0)
        stories = [
            {
                "id": item.id,
                "title": item.name,
                "author": item.author,
                "start_location": item.start_location,
                "image": item.image,
                "status": "",
                "is_favorite": Favorite.objects.filter(
                    user=context["user"], quest=Quest.objects.get(id=item.id)
                ),
                "tags": Tags_Connect.objects.filter(quest=item),
            }
            for item in data
        ]

        first_genre = genre_sort(stories, "хоррор")
        second_genre = genre_sort(stories, "фантастика")
        third_genre = genre_sort(stories, "фентези")

        context["first_genre"] = slide_stories(first_genre)
        context["second_genre"] = slide_stories(second_genre)
        context["third_genre"] = slide_stories(third_genre)

    else:
        request.session.pop("character_id", False)
        data = Quest.objects.exclude(visibility=0)
        stories = [
            {
                "id": item.id,
                "title": item.name,
                "author": item.author,
                "start_location": item.start_location,
                "image": item.image,
                "status": "",
                "tags": Tags_Connect.objects.filter(quest=item),
            }
            for item in data
        ]
        first_genre = genre_sort(stories, "хоррор")
        second_genre = genre_sort(stories, "фантастика")
        third_genre = genre_sort(stories, "фентези")

        context["first_genre"] = slide_stories(first_genre)
        context["second_genre"] = slide_stories(second_genre)
        context["third_genre"] = slide_stories(third_genre)

    context['main_quest1'] = stories[3]
    context['main_quest2'] = stories[10]
    context['main_quest3'] = stories[8]

    return render(request, "pages/index.html", context)


def catalog_page(request):
    context = get_base_context(request)
    context["up_title"] = "Полный каталог квестов:"
    data = Quest.objects.exclude(status=0)
    data = data.exclude(visibility=0)
    duration_type: int

    for item in data:
        duration = len(Location.objects.filter(quest_id=item.id))
        if duration <= 3:
            duration_type = 1
        elif 3 < duration <= 6:
            duration_type = 2
        else:
            duration_type = 3

    stories_info = [
        {
            "duration": duration_type,
            "age_limit": item.agelimit,
            "is_passed": bool(
                Character.objects.filter(quest_id=item.id, user_id=context["user"].id)
            ),
            "is_favorite": bool(
                Favorite.objects.filter(quest=item, user=context["user"])
            ),
            "quest": item,
        }
        for item in data
    ]
    context["back_btn"] = "invisible"

    filters = {
        "duration": None,
        "age_limit": None,
        "no_passed": False,
        "only_favorite": False,
    }
    sort = 0

    if request.method == "POST":
        form = FiltersCatalog(request.POST)
        if form.is_valid():
            filters = {
                "duration": form.cleaned_data.get("duration"),
                "age_limit": form.cleaned_data.get("agelimit"),
                "no_passed": form.cleaned_data.get("completed"),
                "only_favorite": form.cleaned_data.get("favorite"),
            }

            sort = form.cleaned_data.get("sort")
        else:
            messages.add_message(request, messages.ERROR, "ОЙ, где-то ошибка!")

        context["filter_form"] = form
    else:
        context["filter_form"] = FiltersCatalog(initial={})

    context["stories"] = get_guests_by_filters(filters, sort, stories_info)

    return render(request, "pages/catalog.html", context)


def get_guests_by_filters(filters: dict, sort, stories_info):
    sorted_stories = []
    for story in stories_info:
        flag = 1
        if filters["no_passed"]:
            if story["is_passed"]:
                flag = 0
        if filters["only_favorite"]:
            if not story["is_favorite"]:
                flag = 0
        if filters["duration"]:
            if int(filters["duration"]) != story["duration"]:
                flag = 0
        if filters["age_limit"]:
            if int(filters["age_limit"]) != story["age_limit"]:
                flag = 0

        if flag:
            sorted_stories.append(story["quest"])

    if sort == "1":
        sorted_stories = sorted(sorted_stories, key=lambda d: d["rating"])
    elif sort == "2":
        sorted_stories = sorted(sorted_stories, key=lambda d: d["rating"], reverse=True)

    return sorted_stories


def navigator_to_locations(location_id: int = 0):
    connects_from = Connect_location.objects.filter(to_location=location_id)
    before_before_alfa_locations = set()
    for connect in connects_from:
        for i in Connect_location.objects.filter(from_location=connect.from_location):
            before_before_alfa_locations.add(i)
    alfa_locations = set()
    for connect in before_before_alfa_locations:
        for i in Location.objects.filter(id=connect.to_location):
            alfa_locations.add(i)
    return list(alfa_locations)


def navigator_from_locations(location_id: int = 0):
    connects_from = Connect_location.objects.filter(to_location=location_id)
    from_locations = []
    for connect in connects_from:
        for i in Location.objects.filter(id=connect.from_location):
            from_locations.append(i)
    return from_locations


def check_achieve(context, location):
    achieve = Achievements.objects.filter(location=location).first()

    if not achieve:
        return False

    connect = ConnectAchievements.objects.filter(
        user=context["user"], achieve=achieve
    ).first()
    if connect is None:
        achieve = ConnectAchievements.objects.create(
            user=context["user"], achieve=achieve, date=datetime.datetime.now()
        )
        achieve.save()

        return achieve.achieve.name

    return False


def add_rating(request, location):
    form = RateForm(request.POST)
    if form.is_valid():
        user_id = request.user
        rating = form.data["rate"]
        if Rating.objects.filter(user_id=user_id, quest_id=location.quest_id).exists():
            rate = Rating.objects.filter(user_id=user_id).first()
            rate.rating = rating
            rate.save()
        else:
            Rating(
                user=request.user,
                quest=Quest.objects.get(id=location.quest_id),
                rating=rating,
            ).save()

        quest = Quest.objects.get(id=location.quest_id)
        rate = Rating.objects.filter(quest=location.quest_id)
        total_rating = rate.aggregate(total_rating=Sum("rating"))["total_rating"]
        count = Rating.objects.filter(quest=location.quest_id).count()
        quest.rating = round(total_rating / count, 2)
        quest.save()
        return 0

    messages.add_message(request, messages.ERROR, "Некорректные данные")
    return redirect("index")


@login_required(redirect_field_name=None)
def passage_story(request, location_id):
    context = get_base_context(request)
    quest = Quest.objects.get(id=Location.objects.get(id=location_id).quest_id)
    location = Location.objects.get(id=location_id)
    character_id = request.session.get("character_id", False)

    if quest.status == 0 and request.user.is_staff is not True:
        messages.add_message(
            request,
            messages.WARNING,
            "Данный квест заблокирован из-за нарушений правил сайта.",
        )
        redirect("index")
    if not request.session.get("character_id", False):
        return redirect("character", quest_id=location.quest_id)

    achieve = check_achieve(context=context, location=location)
    if achieve:
        messages.add_message(
            request, messages.SUCCESS, f"Вы получили достижение: {achieve}"
        )

    character = Character.objects.get(id=character_id)
    if location_id != character.location_now_id:
        request.user.experience += 50
        request.user.save()
        next_locations = Connect_location.objects.filter(
            from_location=character.location_now_id
        )
        next_locations_id = [location.to_location for location in next_locations]
        if location_id not in next_locations_id:
            return redirect("passage_story", location_id=character.location_now_id)

    character.progress += 1
    character.save()
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

    if request.method == "POST" and vote1.the_end:
        add_rating(request, vote1)

    context["quest"] = quest
    context["location"] = location
    context["actions"] = [
        {
            "data": actions[i],
            "index": i + 1,
            "to_location": actions[i].to_location,
            "action": actions[i].action,
        }
        for i in range(len(actions))
    ]
    context["is_ban"] = quest.status == 0

    character.location_now_id = location_id
    character.save()

    return render(request, "pages/passage_story.html", context)


@login_required(redirect_field_name=None)
def choose_character(request, quest_id):
    context = get_base_context(request)
    if request.method == "POST":
        character_id = request.POST.get("character", None)
        if character_id is None:
            return HttpResponseNotFound()

        quest = Quest.objects.get(id=quest_id)
        character_name = request.POST.get("character_name", "test")
        if character_id == "0":
            if character_name != "":
                character_obj = Character(
                    name=character_name,
                    user=request.user,
                    quest_id=quest_id,
                    location_now_id=quest.start_location,
                    progress=0,
                )
                character_obj.save()
            else:
                print(request.GET)
                messages.add_message(
                    request, messages.ERROR, "Имя персонажа не может быть пустотой!"
                )
            return redirect("character", quest_id=quest_id)

        character_obj = Character.objects.get(id=character_id)
        request.session["character_id"] = character_obj.id
        return redirect("passage_story", location_id=character_obj.location_now_id)

    characters = Character.objects.filter(user=request.user, quest_id=quest_id)

    context["quest_id"] = quest_id
    context["characters"] = [
        {"data": characters[i], "index": i + 1} for i in range(len(characters))
    ]
    item = Quest.objects.prefetch_related("tags_connect").get(id=quest_id)
    context["story"] = {
        "id": item.id,
        "title": item.name,
        "author": item.author.username if item.author else "",
        "description": item.description,
        "image": item.image,
        "rating": str(round(item.rating, 1)),
        "tag": [tag_connect.tag.tag for tag_connect in item.tags_connect.all()],
    }

    return render(request, "pages/character.html", context)


@login_required(redirect_field_name=None)
def activate_telegram(request):
    if request.user.telegram_id is not None:
        return {"error": "Тг уже подключен"}
    if not request.user.telegram_token:
        request.user.generate_token()
        request.user.save()
    return {"key": request.user.telegram_token, "date": request.user.telegram_lifetime}
