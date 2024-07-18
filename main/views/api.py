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

from main.models import Quest, Location, Connect_location, User, Character
from main.serializers import (
    QuestSerializer,
    LocationSerializer,
    ConnectLocationSerializer, CharacterSerializer,
)


def get_api_data(request, model, serializer, query):
    page = request.GET.get('page', '')
    per_page = request.GET.get('per_page', 5)
    for key in query:
        if query[key] is None:
            data = model.objects.all()
            break
    else:
        data = model.objects.all().filter(**query)

    response = []
    for element in data:
        response.append(serializer(element).data)

    if page.isdigit():
        paginator = Paginator(response, per_page)
        return Response({"pages": paginator.num_pages, "result": paginator.page(page).object_list})
    return Response(response)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_quest_by_id(request):
    return get_api_data(request, Quest, QuestSerializer, {'id': request.GET.get('id')})


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_location_by_id(request):
    return get_api_data(request, Location, LocationSerializer, {'id': request.GET.get('id')})


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_connect_locations_by_from_location(request):
    return get_api_data(request, Connect_location, ConnectLocationSerializer, {"from_location": request.GET.get("from_location") })


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_character_by_telegram_and_quest(request):
    telegram_id = request.GET.get("telegram_id")
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return Response(False)
    return get_api_data(request, Character, CharacterSerializer, {"user": user, "quest_id": request.GET.get("quest_id")})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def api_get_location_and_save_progress(request):
    location_id = request.GET.get('id')
    character_id = request.GET.get('character_id')
    character = Character.objects.get(id=character_id)

    character.location_now_id = location_id
    character.save()

    return get_api_data(request, Location, LocationSerializer, {'id': location_id})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def api_create_character(request):
    telegram_id = request.POST.get("telegram_id", False)
    quest_id = request.POST.get("quest_id", False)
    character_name = request.POST.get("character_name", False)
    print(telegram_id)
    if not telegram_id or not quest_id or not character_name:
        return HttpResponseBadRequest("I need telegram_id, quest_id and character_name")

    user = User.objects.get(telegram_id=telegram_id)
    quest = Quest.objects.get(id=quest_id)
    character = Character(name=character_name, user=user, quest_id=quest_id, location_now_id=quest.start_location)
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
        return Response(False)

    auth_user = User.objects.filter(telegram_token=token).first()
    if not auth_user:
        return Response(False)

    auth_user.telegram_id = telegram_id
    auth_user.save()
    return Response(True)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def api_logout_user(request):
    telegram_id = request.POST.get("telegram_id", False)
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return Response(False)
    user.telegram_id = None
    user.telegram_token = None
    user.telegram_lifetime = None
    user.save()
    return Response(True)