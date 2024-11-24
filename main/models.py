from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from django.contrib.auth.models import AbstractUser
from django.db import models

from questpool import settings


class User(AbstractUser):
    telegram_token = models.CharField(max_length=64, editable=False, null=True)
    telegram_lifetime = models.DateTimeField(null=True)
    telegram_id = models.IntegerField(null=True)
    experience = models.IntegerField(default=0)
    image = models.ImageField(null=True, blank=True, upload_to="images/")

    def generate_token(self):
        self.telegram_token = Fernet.generate_key().decode()
        self.telegram_lifetime = datetime.now() + timedelta(minutes=3)


class Location(models.Model):
    name = models.CharField(max_length=64)
    text = models.CharField(max_length=1024)
    count_connections = models.IntegerField()
    quest_id = models.IntegerField()
    the_end = models.BooleanField(default=False, blank=True, null=True)

    def can_edit(self, user: settings.AUTH_USER_MODEL):
        return Quest.objects.get(id=self.quest_id).author == user or user.is_staff


class Quest(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    start_location = models.IntegerField()
    visibility = models.BooleanField(default=0)
    status = models.BooleanField(default=1)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    rating = models.FloatField(default=0, null=True)
    agelimit = models.IntegerField(default=0, null=True)

    def can_edit(self, user: settings.AUTH_USER_MODEL):
        return self.author == user or user.is_staff


class Rating(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True)
    quest = models.ForeignKey(
        to=Quest, on_delete=models.CASCADE, blank=True, related_name="ratedquest"
    )
    rating = models.FloatField(default=0, null=True)


class Connect_location(models.Model):
    connect_id = models.AutoField(primary_key=True)
    from_location = models.IntegerField()
    to_location = models.IntegerField()
    action = models.CharField(max_length=64)

    def can_edit(self, user: settings.AUTH_USER_MODEL):
        location = Location.objects.get(id=self.from_location)
        quest = Quest.objects.get(id=location.quest_id)
        return quest.author == user or user.is_staff


class Complaint(models.Model):
    quest_id = models.IntegerField()
    location_id = models.IntegerField()
    message = models.CharField(max_length=1024)
    username = models.CharField(max_length=64)


class Usual_tags(models.Model):
    tag = models.CharField(max_length=32)
    base_tag = models.BooleanField(default=0)


class Tags_Connect(models.Model):
    tag = models.ForeignKey(Usual_tags, on_delete=models.CASCADE)
    quest = models.ForeignKey(
        Quest, on_delete=models.CASCADE, related_name="tags_connect"
    )


class Character(models.Model):
    name = models.CharField(max_length=16)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    quest_id = models.IntegerField()
    location_now_id = models.IntegerField()
    progress = models.IntegerField()

    def can_edit(self, user: settings.AUTH_USER_MODEL):
        quest = Quest.objects.get(id=self.quest_id)
        return quest.author == user or user.is_staff


class Support_messages(models.Model):
    email = models.EmailField(max_length=65)
    text = models.TextField(max_length=5000)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    data = models.DateTimeField()


class Favorite(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE, blank=True, null=True)


class Achievements(models.Model):
    location = models.ForeignKey(
        to=Location, on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64)


class ConnectAchievements(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    achieve = models.ForeignKey(
        to=Achievements, on_delete=models.CASCADE, blank=True, null=True
    )
    date = models.DateTimeField()
