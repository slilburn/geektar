from django.forms import *
from geektar.home.models import SONG_RATING_CHOICES

class RegisterForm(Form):
    username = CharField()
    email = EmailField()
    password = CharField(widget=PasswordInput)

class LoginForm(Form):
    username = CharField()
    password = CharField(widget=PasswordInput)

class AddSongForm(Form):
    artist = CharField()
    title = CharField()
    tab = CharField(widget=Textarea(attrs={'rows':'20','cols':'80'}),
                                    required=False)
    tags = CharField(required=False)
    ability = ChoiceField(choices=SONG_RATING_CHOICES)
    private = BooleanField(required=False)
