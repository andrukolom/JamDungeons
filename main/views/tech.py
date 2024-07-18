import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from main.forms import Support
from main.models import Support_messages
from main.forms import ComplaintForm
from main.models import Quest, Complaint, Connect_location, Location, Favorite
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
        else:
            messages.add_message(
                request, messages.ERROR, "Некорректные данные в вопросе"
            )
            return redirect("support")
    return redirect("index")

def guide_page(request):
    context = get_base_context(request)
    return render(request, 'pages/guide.html', context)

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
    results = Quest.objects.filter(name__icontains=query)
    context = {'up_title': 'Результаты поиска "'+str(query)+'":', 'back_btn': "visible"}
    stories = [
        {
            "id": item.id,
            "name": item.name,
            "author": item.author,
            "start_location": item.start_location,
            "image": item.image,
            'rating': str(round(item.rating, 1))
        }
        for item in results
    ]
    context['stories'] = stories
    return render(request, 'pages/catalog.html', context)


def set_quest_state(quest_id, state):
    quest = Quest.objects.get(id=quest_id)
    quest.state = state
    quest.save()


def unban_quest(request, quest_id: int):
    if request.user.is_staff:
        set_quest_state(quest_id, 3)
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
                quest_id=quest_id,
                location_id=location_id,
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
        set_quest_state(quest_id, 6)
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
    else:
        messages.add_message(request, messages.WARNING, "Вы не являетесь модератором")
        return redirect("index")


def delete_complaint(request, complaint_id: int):
    if request.user.is_staff:
        complaint_obj = Complaint.objects.filter(id=complaint_id)
        location_id = complaint_obj[0].location_id
        complaint_obj.delete()
        messages.add_message(request, messages.SUCCESS, "Жалоба закрыта")

        return redirect("passage_story", location_id=location_id)
    else:
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

    record = Favorite(
        user=context['user'],
        quest=quest
    )

    record.save()
    return redirect('index')
