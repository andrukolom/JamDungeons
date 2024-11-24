from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from main.models import (
    Quest,
    Location,
    Connect_location,
    User,
    Character,
    Usual_tags,
    Favorite,
    Tags_Connect,
    ConnectAchievements,
)
from main.serializers import (
    QuestSerializer,
    LocationSerializer,
    ConnectLocationSerializer,
    CharacterSerializer,
    PassingSerializer,
    QuestWithAchievementsSerializer,
    LocationWithAchievementsSerializer,
)


def get_paginate_data(data, per_page, page):
    paginator = Paginator(data, per_page)
    return Response(
        {"pages": paginator.num_pages, "result": paginator.page(page).object_list}
    )


def get_api_data(request, model, serializer, query, context={}):
    page = request.GET.get("page", "")
    per_page = request.GET.get("per_page", 10)
    for key in query:
        if query[key] is None:
            data = model.objects.all()
            break
    else:
        data = model.objects.all().filter(**query)

    response = []
    for element in data:
        response.append(serializer(element, context=context).data)

    if page.isdigit():
        return get_paginate_data(response, per_page, page)
    return Response(response)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_quest_by_id(request):
    return get_api_data(request, Quest, QuestSerializer, {"id": request.GET.get("id")})


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_location_by_id(request):
    return get_api_data(
        request, Location, LocationSerializer, {"id": request.GET.get("id")}
    )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_connect_locations_by_from_location(request):
    return get_api_data(
        request,
        Connect_location,
        ConnectLocationSerializer,
        {"from_location": request.GET.get("from_location")},
    )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_achivements(request):
    user = User.objects.filter(telegram_id=request.GET.get("telegram_id", 0)).first()
    if not user:
        return Response([])
    connect_achievements = ConnectAchievements.objects.filter(user=user)
    quests = set()
    for connect in connect_achievements:
        quests.add(connect.achieve.location.quest_id)
    result = []
    context = {"user": user}
    for quest_id in quests:
        result.append(
            QuestWithAchievementsSerializer(
                Quest.objects.get(id=quest_id), context=context
            ).data
        )
    return get_paginate_data(result, 10, request.GET.get("page", 1))


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_favorite_quests(request):
    user = User.objects.filter(telegram_id=request.GET.get("telegram_id", "")).first()
    if not user:
        return Response([])
    favorite_quests = Favorite.objects.filter(user=user)
    result = []
    for quest in favorite_quests:
        result.append(QuestSerializer(quest.quest).data)

    return get_paginate_data(result, 10, request.GET.get("page", 1))


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_check_favorite_quest(request):
    user = User.objects.filter(telegram_id=request.GET.get("telegram_id", "")).first()
    quest_id = request.GET.get("quest_id", "")
    return Response(Favorite.objects.filter(user=user, quest_id=quest_id).exists())


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_character_by_telegram_and_quest(request):
    telegram_id = request.GET.get("telegram_id")
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return Response([])
    return get_api_data(
        request,
        Character,
        CharacterSerializer,
        {"user": user, "quest_id": request.GET.get("quest_id")},
    )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_tags(request):
    tags = Usual_tags.objects.filter(base_tag=True)
    result = []
    for tag in tags:
        result.append(tag.tag)
    return Response(result)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_quest_tags(request):
    quest_id = request.GET.get("quest_id", 0)
    tags = Tags_Connect.objects.filter(quest_id=quest_id)
    result = []
    for connect in tags[:10]:
        result.append(connect.tag.tag)
    return Response(result)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_quest_by_name(request):
    return get_api_data(
        request,
        Quest,
        QuestSerializer,
        {"name__icontains": request.GET.get("name", "")},
    )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_quest_by_tags(request):
    count_tags = request.GET.get("count", 0)
    page = request.GET.get("page", 1)
    tags = []
    for i in range(int(count_tags)):
        tags.append(request.GET.get(f"tag{i}", ""))
    quest_with_all_tags = Quest.objects.all()
    for tag in tags:
        quest_with_all_tags = quest_with_all_tags.filter(tags_connect__tag__tag=tag)
    quests = quest_with_all_tags.filter(visibility=True, status=True).distinct()
    result = []
    for quest in quests:
        result.append(QuestSerializer(quest).data)

    return get_paginate_data(result, 10, page)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_my_passings(request):
    telegram_id = request.GET.get("telegram_id", 0)
    page = request.GET.get("page", 1)
    user = User.objects.get(telegram_id=telegram_id)

    quests = Character.objects.filter(user=user).values("quest_id").distinct()
    result = []
    context = {"user": user}
    for quest_id in quests:
        result.append(
            PassingSerializer(
                Quest.objects.get(id=quest_id["quest_id"]), context=context
            ).data
        )

    return get_paginate_data(result, 5, page)


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def api_add_favorite(request):
    quest_id = request.POST.get("quest_id", 0)
    telegram_id = request.POST.get("telegram_id", 0)
    user = User.objects.filter(telegram_id=telegram_id).first()
    if not user or not quest_id:
        return HttpResponseBadRequest("I need telegram_id and quest_id")

    quest = Quest.objects.filter(id=quest_id).first()
    if not quest:
        return Response({"error": "incorrect data"})

    check = Favorite.objects.filter(user=user, quest=quest).first()
    if check:
        return Response({"error": "incorrect data"})

    Favorite.objects.create(quest=quest, user=user).save()
    return Response({"success": "true"})


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def api_delete_favorite(request):
    quest_id = request.POST.get("quest_id", 0)
    telegram_id = request.POST.get("telegram_id", 0)
    user = User.objects.filter(telegram_id=telegram_id).first()
    if not user or not quest_id:
        return HttpResponseBadRequest("I need telegram_id and quest_id")

    quest = Quest.objects.filter(id=quest_id).first()
    if not quest:
        return Response({"error": "incorrect data"})

    favorites = Favorite.objects.filter(user=user, quest=quest).first()
    if favorites:
        favorites.delete()
        return Response({"success": "true"})
    return Response({"error": "incorrect data"})


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def api_get_location_and_save_progress(request):
    location_id = request.POST.get("id")
    character_id = request.POST.get("character_id")
    try:
        character = Character.objects.get(id=character_id)
    except Character.DoesNotExist:
        return Response({"error": "incorrect data"})

    character.location_now_id = location_id
    character.save()

    return get_api_data(
        request,
        Location,
        LocationWithAchievementsSerializer,
        {"id": location_id},
        context={"user": character.user},
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def api_create_character(request):
    telegram_id = request.POST.get("telegram_id", False)
    quest_id = request.POST.get("quest_id", False)
    character_name = request.POST.get("character_name", False)

    if not telegram_id or not quest_id or not character_name:
        return HttpResponseBadRequest("I need telegram_id, quest_id and character_name")

    user = User.objects.get(telegram_id=telegram_id)
    quest = Quest.objects.get(id=quest_id)
    character = Character(
        name=character_name,
        user=user,
        quest_id=quest_id,
        location_now_id=quest.start_location,
        progress=1,
    )
    character.save()
    serializer = CharacterSerializer(character)
    return Response([serializer.data])


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def api_check_key(request):
    token = request.POST.get("key", False)
    telegram_id = request.POST.get("telegram_id", False)
    if not token or not telegram_id:
        return Response({"error": "incorrect data"})

    auth_user = User.objects.filter(telegram_token=token).first()
    if not auth_user:
        return Response({"error": "incorrect data"})

    auth_user.telegram_id = telegram_id
    auth_user.save()
    return Response({"success": "true"})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def api_logout_user(request):
    telegram_id = request.POST.get("telegram_id", False)
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return Response({"error": "incorrect data"})
    user.telegram_id = None
    user.telegram_token = None
    user.telegram_lifetime = None
    user.save()
    return Response({"success": "true"})
