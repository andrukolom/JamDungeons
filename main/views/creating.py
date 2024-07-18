import json
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from main.forms import CreateQuestForm, CreateLocationForm, CreateActionForm
from main.models import Hashtag
from main.models import Location, Connect_location
from main.models import Quest
from main.views.views import get_base_context, navigator_from_locations, navigator_to_locations
from main.views.checkout_tags import Tags_checkout

@login_required(redirect_field_name=None)
def create_quest(request):
    """
        Основная функция логики страницы создания квестов

        Создает базовый контекст

        Обрабатывает форму пользователя:

        Если пользователь только зашел на страницу, то
        создает пустую форму и добавляет ее в контекст.
        Если пользователь отправил форму и пришел POST-запрос, то
        проверяет форму на валидность, добавляет в форму информацию и пользователе,
        создает модель локации для базы данных и записывает в форму данные: название, описание, автор,
        id стартовой локации, состояние, выполнен ли квест.

        Перенаправляет на функцию create_location, если форма валидная и добавляет сообщение на сайт
        "Отлично, движемся дальше", иначе возвращает эту форму на страницу
        и отправляет сообщение "ОЙ, где-то ошибка!"

        :param request: запрос с сайта
        :type request: :class:`django.http.HttpRequest`
        :return: render страницы ``pages/createQuest.html`` с контекстом
        :rtype: :class:`django.http.HttpResponse`
    """

    context = get_base_context(request)
    hashtags = Hashtag.objects.all()
    context["hashtags"] = hashtags

    if request.method == "POST":
        form = CreateQuestForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():

            location_obj = Location(name="", text="", count_connections=0, quest_id=0)
            location_obj.save()

            record = Quest(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                tag=form.cleaned_data["tag"],
                author=context['user'],
                start_location=location_obj.id,
                visibility=False,
                status=False,
                image=form.cleaned_data["image"],
            )
            record.save()

            location_obj.quest_id = record.id
            location_obj.save()
            tag_text = form.cleaned_data.get("tag")
            tags = tag_text.split()
            print(tags)
            for tag in tags:
                if tag.startswith("#"):
                    tag = tag[0:]
                tags_checkout = Tags_checkout(tag)
                if (tags_checkout.can_write_tag()):
                    hashtag = Hashtag.objects.create(tag=tag)
                    hashtag.save()
            messages.add_message(request, messages.SUCCESS, "Отлично, движемся дальше!")
            return redirect("create_location", location_id=location_obj.id)
        else:
            messages.add_message(request, messages.ERROR, "ОЙ, где-то ошибка!")
            context["quest_form"] = form
            return render(request, "create_quests_pages/create_quest.html", context)
    else:
        context["quest_form"] = CreateQuestForm(initial={})
    return render(request, "create_quests_pages/create_quest.html", context)


@login_required(redirect_field_name=None)
def create_location(request, location_id: int):
    """
    Основная функция логики страницы создания локации

    Создает базовый контекст

    Обрабатывает форму пользователя:

    Если пользователь только зашел на страницу, то
    получает данные о текущей локации и список локаций, которые подключены к данной,
    добавляет список всех локаций от этого квеста в контекст; проходится по списку подключенных локаций и
    создает отдельную форму для подключения каждой локации, из этих форм создается список и добавляется в
    контекст.
    Если пользователь отправил форму и пришел POST-запрос, то
    забирает из формы локации данные об истории, количества действий и имени и сохраняет эту локацию в
    базу данных; забирает из формы список действий, проходится по нему и создает форму для каждого действия,
    также создается форму пустых действий при необходимости; далее добавляет в контекст данных о локации:
    историю, количество действий и имя, добавляет в контекст все локации квеста и id данного квеста.

    :param request: запрос с сайта
    :type request: :class:`django.http.HttpRequest`
    :return: render страницы ``pages/createLocation.html`` с контекстом
    :rtype: :class:`django.http.HttpResponse`
    """
    context = get_base_context(request)
    if request.method == "POST":
        form = CreateActionForm(request.POST)

        record = Location.objects.get(id=location_id)
        record.text = form.data["history"]
        record.count_connections = int(request.POST.get('countActions', 0))
        record.name = form.data["name"]
        the_end_value = form.data["final_location"]
        record.the_end = bool(int(the_end_value))
        form_count_actions = int(request.POST.get('countActions', 0))

        if record.the_end:
            record.count_connections = 0
            form_count_actions = 0
            Connect_location.objects.filter(from_location=record.id).delete()

        record.save()

        actions = form.data.getlist("action")
        action_records = Connect_location.objects.filter(from_location=record.id)
        action_forms = []

        counter = 0
        for action in action_records:
            action.action = actions[counter]
            action.save()

            action_forms.append(
                CreateActionForm(
                    initial={"action": action.action},
                    id=action.connect_id,
                    to_location=action.to_location,
                )
            )
            counter += 1

        for i in range(form_count_actions - counter):
            action_record = Connect_location(from_location=record.id, to_location=0)
            action_record.save()

            action_forms.append(CreateActionForm(id=action_record.connect_id, to_location=action_record.to_location))

        context["location_form"] = CreateLocationForm(
            initial={
                "history": form.data["history"],
                "countActions": form_count_actions,
                "name": form.data["name"],
            },
            actions=action_forms,
            current_min_value=int(request.POST.get('countActions', 0)),
        )
        locations = Location.objects.filter(quest_id=record.quest_id)
        nodes = []
        edges = []
        for location in locations:
            nodes.append(
                {
                    "data": {
                        "id": location.id,
                        "name": location.name,
                    }
                }
            )
            connects = Connect_location.objects.filter(from_location=location.id)
            for connect in connects:
                if connect.to_location:
                    edges.append(
                        {
                            "data": {
                                "source": connect.from_location,
                                "target": connect.to_location,
                                "name": connect.action,
                            }
                        }

                    )

        context["nodes"] = json.dumps(nodes)
        context["edges"] = json.dumps(edges)
        context['from_locations'] = navigator_from_locations(location_id)
        context['alfa_locations'] = navigator_to_locations(location_id)
        context['all_locations'] = Location.objects.filter(quest_id=record.quest_id)
        context["location_id"] = record.id
        context["location_form"].fields['final_location'].initial = [int(record.the_end)]
        context["the_end"] = record.the_end
        if record.the_end:
            context["location_form"].fields["countActions"].widget.attrs["disabled"] = True

        return render(request, "create_quests_pages/create_location.html", context)
    else:
        location = Location.objects.get(id=location_id)
        quest = Quest.objects.get(id=location.quest_id)
        if quest.author_id != context['user'].id:
            return HttpResponseNotFound('<h1>Не трожь чужое</h1>')
        actions = Connect_location.objects.filter(from_location=location_id)
        locations = Location.objects.filter(quest_id=location.quest_id)
        context['from_locations'] = navigator_from_locations(location_id)
        context['alfa_locations'] = navigator_to_locations(location_id)
        context['all_locations'] = locations
        context["location_id"] = location.id

        action_forms = []
        for action in actions:
            if action.action:
                action_forms.append(
                    CreateActionForm(
                        initial={"action": action.action},
                        id=action.connect_id,
                        to_location=action.to_location,
                    )
                )
            else:
                action_forms.append(CreateActionForm(initial={"action": action.action}, id=action.connect_id,
                                                     to_location=action.to_location))

        context["location_form"] = CreateLocationForm(
            initial={
                "history": location.text,
                "countActions": location.count_connections,
                "name": location.name,
            },
            actions=action_forms,
            current_min_value=location.count_connections,
        )

        context["location_form"].fields['final_location'].initial = [int(location.the_end)]
        context["the_end"] = int(location.the_end)

        if location.the_end:
            context["location_form"].fields["countActions"].widget.attrs["disabled"] = True
        else:
            context["location_form"].fields["countActions"].widget.attrs["disabled"] = False
        nodes = []
        edges = []
        for location in locations:
            nodes.append({"data": {"id": location.id, "name": location.name}})
            connects = Connect_location.objects.filter(from_location=location.id)
            for connect in connects:
                if connect.to_location:
                    edges.append(
                        {
                            "data": {
                                "source": connect.from_location,
                                "target": connect.to_location,
                                "name": connect.action,
                            }
                        }
                    )

        context["nodes"] = json.dumps(nodes)
        context["edges"] = json.dumps(edges)

        return render(request, "create_quests_pages/create_location.html", context)


@login_required(redirect_field_name=None)
def connect_location(request, connect_id, location_id):
    """
    Функция подключения локации к модели связи ``Connect_location``

    Берет модель из базы данных по `connect_id` и устанавливает в поле `to_location` значение
    `location_id`

    :param request: запрос с сайта
    :type request: :class:`django.http.HttpRequest`
    :param connect_id: id модели ``Connect_location`` к которой нужно присоединить id локации
    :type connect_id: int
    :param location_id: id локации, которую нужно подключить к модели ``Connect_location``
    :type location_id: int
    :return: перенаправляет запрос в функцию ``create_location``
    :rtype: None
    """

    connect = Connect_location.objects.get(connect_id=connect_id)
    connect.to_location = location_id
    connect.save()

    return redirect("create_location", location_id=connect.from_location)

@login_required(redirect_field_name=None)
def complete_quest(request, location_id):
    quest_id = Location.objects.get(id=location_id).quest_id
    all_locations = Location.objects.filter(quest_id=quest_id)
    quest = Quest.objects.get(id=quest_id)

    unfinished = []
    finished = []
    for location in all_locations:
        connects = Connect_location.objects.filter(from_location=location.id)
        if connects:
            for connect in connects:
                if not connect.to_location:
                    unfinished.append(location)
                    break
            finished.append(location)

    if unfinished or not finished:
        print(unfinished)
        errors = str()
        for location in range(len(unfinished)):
            errors += "<<" + (unfinished[location].name) + ">> "
        messages.add_message(
            request, messages.ERROR, f"Упс, вы забыли доделать локации: {errors}"
        )
        return redirect("create_location", location_id=location_id)
    else:
        messages.add_message(
            request, messages.SUCCESS, "Поздравляем, Вы создали квест!"
        )
        quest.visibility = True
        quest.save()
        return redirect("index")

@login_required(redirect_field_name=None)
def create_location_sketch(request, connect_id):
    """
    Функция создания пустой локации

    Создается пустая локация и устанавливается id квеста, к которому она относится. Также устанавливается
    id этой локации в модели ``Connect_location``, к которой нужно присоединить данную локацию.

    :param request: запрос с сайта
    :type request: :class:`django.http.HttpRequest`
    :param connect_id: id модели ``Connect_location`` к которой нужно присоединить данную локацию
    :type connect_id: int
    :return: перенаправляет запрос в функцию ``create_location``
    :rtype: None
    """
    connect = Connect_location.objects.get(connect_id=connect_id)
    quest_id = Location.objects.get(id=connect.from_location)
    quest_id = quest_id.quest_id

    location_obj = Location(
        name="",
        text="",
        count_connections=0,
        quest_id=quest_id,
    )
    location_obj.save()

    connect.to_location = location_obj.id
    connect.save()

    return redirect("create_location", location_id=location_obj.id)

