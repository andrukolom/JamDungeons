import datetime

from rest_framework import serializers

from main.models import (
    Location,
    Quest,
    Connect_location,
    Character,
    Achievements,
    ConnectAchievements,
)


class QuestSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username")

    class Meta:
        model = Quest
        fields = (
            "id",
            "name",
            "description",
            "author_name",
            "start_location",
            "image",
            "visibility",
            "status",
            "rating",
            "agelimit",
        )


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class LocationWithAchievementsSerializer(serializers.ModelSerializer):
    achievement = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ["id", "name", "text", "quest_id", "the_end", "achievement"]

    def get_achievement(self, location):
        achievement = Achievements.objects.filter(location=location).first()
        if achievement is None:
            return ""
        user = user = self.context.get("user")
        is_achieved = ConnectAchievements.objects.filter(
            achieve=achievement, user=user
        ).first()
        if is_achieved is None:
            new_connect = ConnectAchievements.objects.create(
                achieve=achievement, user=user, date=datetime.datetime.now()
            )
            new_connect.save()
            return AchievementSerializer(achievement, context=self.context).data
        return ""


class AchievementSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = Achievements
        fields = ["id", "name", "description", "date"]

    def get_date(self, achievement):
        try:
            achievement_date = ConnectAchievements.objects.get(
                user=self.context.get("user"), achieve=achievement.id
            )
        except ConnectAchievements.DoesNotExist:
            data = datetime.datetime.now()
            return data.strftime("%d.%m.%y")
        return achievement_date.date.strftime("%d.%m.%y")


class QuestWithAchievementsSerializer(serializers.ModelSerializer):
    achievements = serializers.SerializerMethodField()
    author_name = serializers.CharField(source="author.username")

    class Meta:
        model = Quest
        fields = ["id", "name", "description", "rating", "author_name", "achievements"]

    def get_achievements(self, quest):
        locations = Location.objects.filter(quest_id=quest.id).values("id").distinct()
        locations = [x["id"] for x in locations]
        achievements = ConnectAchievements.objects.filter(achieve__location__in=locations, user=self.context.get('user'))
        result = []
        for achievement in achievements:
            result.append(AchievementSerializer(achievement.achieve, context=self.context).data)
        return result


class ConnectLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connect_location
        fields = "__all__"


class CharacterSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="user.username")
    location_now_name = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            "id",
            "name",
            "quest_id",
            "location_now_id",
            "location_now_name",
            "author_name",
        ]

    def get_location_now_name(self, character):
        return Location.objects.get(id=character.location_now_id).name


class PassingSerializer(serializers.ModelSerializer):
    characters = serializers.SerializerMethodField()
    author_name = serializers.CharField(source="author.username")

    class Meta:
        model = Quest
        fields = ["id", "name", "description", "rating", "author_name", "characters"]

    def get_characters(self, quest):
        characters = Character.objects.filter(
            quest_id=quest.id, user=self.context.get("user")
        )
        result = []
        for character in characters:
            result.append(CharacterSerializer(character).data)
        return result
