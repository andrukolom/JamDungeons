from rest_framework import serializers

from main.models import Location, Quest, Connect_location, Character


class QuestSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username')
    class Meta:
        model = Quest
        fields = ("id", "name", "description", "author_name", "start_location", "is_completed", "state", "tag")


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class ConnectLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connect_location
        fields = "__all__"

class CharacterSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(source='user.telegram_id')
    class Meta:
        model = Character
        fields = ['id', 'telegram_id', 'name', 'quest_id', 'location_now_id']
