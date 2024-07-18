from django.contrib import admin

from main.models import Location, Quest, Connect_location, Hashtag
from django.contrib.auth.admin import UserAdmin
from main.models import User

admin.site.register(User, UserAdmin)

admin.site.register(Location)
admin.site.register(Quest)
admin.site.register(Connect_location)
admin.site.register(Hashtag)
