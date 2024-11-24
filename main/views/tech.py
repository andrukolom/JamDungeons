import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from main.forms import Support, ComplaintForm, QuestInformation
from main.models import (
    Quest,
    Complaint,
    Connect_location,
    Location,
    Favorite,
    Usual_tags,
    Tags_Connect,
    Support_messages
)
from main.views.checkout_tags import Tags_checkout
from main.views.views import get_base_context


def support_page(request):
    if request.method == "POST":
        support_form = Support(request.POST)
        if support_form.is_valid():
            if request.user.is_authenticated:
                user_object = request.user
            else:
                user_object = None
            text = Support_messages(
                email=request.POST["email"],
                text=request.POST["message"],
                user=user_object,
                data=datetime.datetime.now(),
            )
            print(request.POST["email"], request.POST["message"])
            text.save()
            messages.add_message(
                request, messages.SUCCESS, "Ваше обращение успешно отправлен"
            )
            return redirect("index")

        messages.add_message(
            request, messages.ERROR, "Некорректные данные в вопросе"
        )
        return redirect("support")

    return redirect("index")


def guide_page(request):
    context = get_base_context(request)
    return render(request, "pages/guide.html", context)


def search_view(request):
    """
    Основная функция логики страницы поиска

    Получает строку для поиска GET-методом из HTML-запроса, находит квестов, которые совпадают
    со строкой для поиска и записывает их в контекст

    :param request: запрос с сайта
    :type request: :class:`django.http.HttpRequest`
    :return: render страницы ``pages/search_results.html`` с контекстом
    :rtype: :class:`django.http.HttpResponse`
    """
    query = request.POST.get("search", "")
    context = {
        "up_title": 'Результаты поиска "' + str(query) + '":',
        "back_btn": "visible",
    }
    if query.startswith("#"):
        query = query.lstrip("#")
        query.replace("#", "")
        tags = query.split()
        quest_with_all_tags = Quest.objects.all()
        for tag in tags:
            quest_with_all_tags = quest_with_all_tags.filter(tags_connect__tag__tag=tag)
        quest_with_all_tags = quest_with_all_tags.filter(visibility=True)
        results = quest_with_all_tags.filter(status=True).distinct()
    else:
        results = Quest.objects.filter(name__icontains=query)
    stories = [
        {
            "id": item.id,
            "name": item.name,
            "author": item.author,
            "start_location": item.start_location,
            "image": item.image,
            "rating": str(round(item.rating, 1)),
        }
        for item in results
    ]
    context["stories"] = stories
    return render(request, "pages/catalog.html", context)


def set_quest_state(quest_id, status):
    quest = Quest.objects.get(id=quest_id)
    quest.status = status
    quest.save()


def unban_quest(request, quest_id: int):
    if request.user.is_staff:
        set_quest_state(quest_id, status=True)
        messages.add_message(
            request,
            messages.WARNING,
            "Квест разбанен, установлен статус 'готов к прохождению'",
        )
    else:
        messages.add_message(request, messages.WARNING, "Вы не являетесь модератором")

    return redirect("index")


def make_complaint(request, quest_id, location_id):
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            message = form.data["message"]
            username = request.user.username

            complaint_obj = Complaint(
                username=username,
                location_id=location_id,
                quest_id=quest_id,
                message=message,
            )
            complaint_obj.save()

            messages.add_message(request, messages.SUCCESS, "Жалоба отправлена")
        else:
            messages.add_message(
                request, messages.ERROR, "Некорректные данные в форме авторизации"
            )
    return redirect("passage_story", location_id=location_id)


def ban_quest(request, quest_id: int):
    if request.user.is_staff:
        set_quest_state(quest_id, status=False)
        messages.add_message(request, messages.SUCCESS, "Квест забанен")
    else:
        messages.add_message(request, messages.WARNING, "Вы не являетесь модератором")

    return redirect("index")


def view_complaints(request):
    if request.user.is_staff:
        context = get_base_context(request)
        list_complaints = Complaint.objects.all()
        context["complaints"] = [
            {
                "username": item.username,
                "quest_id": item.quest_id,
                "location_id": item.location_id,
                "message": item.message,
                "id": item.id,
            }
            for item in list_complaints
        ]
        return render(request, "pages/view_complaints.html", context)

    messages.add_message(request, messages.WARNING, "Вы не являетесь модератором")
    return redirect("index")


def delete_complaint(request, complaint_id: int):
    if request.user.is_staff:
        complaint_obj = Complaint.objects.filter(id=complaint_id)
        complaint_obj.delete()
        messages.add_message(request, messages.SUCCESS, "Жалоба закрыта")

        return redirect("view_complaint")

    messages.add_message(request, messages.WARNING, "Вы не являетесь модератором")
    return redirect("index")


def delete_connect(request, connect_id: int):
    connect = Connect_location.objects.get(connect_id=connect_id)
    location_id = connect.from_location
    location = Location.objects.get(id=location_id)

    location.count_connections -= 1

    location.save()
    connect.delete()
    return redirect("create_location", location_id=location_id)


def delete_to_location(request, connect_id: int):
    connect = Connect_location.objects.get(connect_id=connect_id)
    location_id = connect.from_location

    connect.to_location = 0
    connect.save()

    return redirect("create_location", location_id=location_id)


def add_favorite(request, quest_id: int):
    quest = Quest.objects.get(id=quest_id)
    context = get_base_context(request)

    record = Favorite(user=context["user"], quest=quest)

    record.save()
    return redirect("index")


def remove_favorite(request, quest_id: int, page: int = 1):
    context = get_base_context(request)
    quest = Quest.objects.get(id=quest_id)

    Favorite.objects.get(user=context["user"], quest=quest).delete()
    if page:
        return redirect("index")

    return redirect("account")


def change_quest_info(request, quest_id):
    if request.method == "POST":
        form = QuestInformation(request.POST, request.FILES)
        if form.is_valid():
            quest = Quest.objects.get(id=quest_id)
            quest.name = form.cleaned_data.get("name")
            quest.description = form.cleaned_data.get("description")
            quest.visibility = form.cleaned_data.get("visibility")
            if form.cleaned_data["image"]:
                quest.image = form.cleaned_data["image"]

            quest.agelimit = form.cleaned_data.get("agelimit")

            quest.save()

            Tags_Connect.objects.filter(quest_id=quest).delete()

            tag_text = form.cleaned_data.get("tag")
            tags = tag_text.split()
            for tag in tags:
                if tag.startswith("#"):
                    tag = tag[1:]
                tag_obj, created = Usual_tags.objects.get_or_create(tag=tag)
                Tags_Connect.objects.create(tag=tag_obj, quest=quest)
                if created:
                    print(f"Tag {tag} was created.")
                tags_checkout = Tags_checkout(tag)
                if tags_checkout.can_write_tag():
                    tag_obj.base_tag = True
                    tag_obj.save()

        return redirect("account")

    return redirect("account")
