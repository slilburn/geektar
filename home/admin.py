from django.contrib import admin
from geektar.home.models import *

admin.site.register(UserProfile)
admin.site.register(Song)
admin.site.register(Tag)
admin.site.register(UserSong)
