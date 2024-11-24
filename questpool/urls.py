"""
URL configuration for questpool project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from main.forms import QuestInformation
from main.views import views, authorization, tech, api, creating, account

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page, name='index'),
    path('search/', tech.search_view, name='search'),
    path('catalog/', views.catalog_page, name='catalog'),

    path('create/quest', creating.create_quest, name='create_quest'),
    path('create/location/<int:location_id>', creating.create_location, name='create_location'),
    path('create/location/<int:location_id>/<int:connect_id>', creating.create_location, name='create_location'),
    path('create/location/connect/<int:connect_id>/<int:location_id>', creating.connect_location, name='connect_location'),
    path('create/complete/<int:location_id>', creating.complete_quest, name='complete_quest'),
    path('create/location/sketch/<int:connect_id>', creating.create_location_sketch, name='create_location_sketch'),
    path('create/delete_connection/<int:connect_id>', tech.delete_connect, name='delete_connection'),

    path('api/quest', api.api_get_quest_by_id),
    path('api/quest/name', api.api_get_quest_by_name),
    path('api/quest/tag', api.api_get_quest_by_tags),
    path('api/tags', api.api_get_quest_tags),
    path('api/favorite', api.api_get_favorite_quests),
    path('api/favorite/add', api.api_add_favorite),
    path('api/favorite/delete', api.api_delete_favorite),
    path('api/favorite/check', api.api_check_favorite_quest),
    path('api/achievements', api.api_get_achivements),
    path('api/location', api.api_get_location_by_id),
    path('api/get_location_and_save', api.api_get_location_and_save_progress),
    path('api/connect', api.api_get_connect_locations_by_from_location),
    path('api/passing', api.api_get_my_passings),
    path('api/character', api.api_get_character_by_telegram_and_quest),
    path('api/character/create', api.api_create_character),
    path('api/tag/base', api.api_get_tags),
    path('api/telegram/check_key', api.api_check_key),
    path('api/auth', obtain_auth_token),
    path('api/logout_user', api.api_logout_user),
    path('telegram/', views.activate_telegram),

    path('passage_story/<int:location_id>', views.passage_story, name='passage_story'),
    path('character/<int:quest_id>', views.choose_character, name='character'),

    path('registration/', authorization.registration_page, name='registration'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('login/', authorization.login_page, name='login'),
    path('me/', account.account_page, name='account'),
    path('me/<int:quest_id>', account.account_page, name='account'),

    path('tech/support', tech.support_page, name='support'),
    path('guide/', tech.guide_page, name='guide'),

    path('make_complaint/<int:quest_id>/<int:location_id>', tech.make_complaint, name='make_complaint'),
    path('view_complaint/', tech.view_complaints, name='view_complaint'),
    path('ban/<int:quest_id>', tech.ban_quest, name='ban_quest'),
    path('unban/<int:quest_id>', tech.unban_quest, name='unban_quest'),
    path('delete_complaint/<int:complaint_id>', tech.delete_complaint, name='delete_complaint'),
    path('add_favorite/<int:quest_id>', tech.add_favorite, name='add_favorite'),
    path('remove_favorite/<int:quest_id>/<int:page>', tech.remove_favorite, name='remove_favorite'),
    path('change_quest_info/<int:quest_id>', tech.change_quest_info, name='change_quest_info'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
