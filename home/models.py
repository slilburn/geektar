from django.db import models
from django.db.models.signals import post_save
from django.contrib.admin.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

SONG_RATING_CHOICES = (
    ('C', "Can't play"),
    ('S', "Need tab"),
    ('M', "Memorized"),
)

class Song(models.Model):
    title  = models.CharField(max_length=50)
    artist = models.CharField(max_length=50)

    def __unicode__(self):
        return self.artist + " - " + self.title

class UserProfile(models.Model):
    songs = models.ManyToManyField(Song)
    user = models.ForeignKey(User, unique=True)

    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

class UserSong(models.Model):
    song = models.ForeignKey(Song)
    user = models.ForeignKey(User)
    tab = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)
    ability = models.CharField(max_length=1, choices=SONG_RATING_CHOICES)
    private = models.BooleanField()

    def __unicode__(self):
        return (self.user.username + ": " + self.song.artist
               + " - " + self.song.title)
