from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import auth
from geektar.home.forms import *
from django import forms
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from geektar.home.models import *
from urllib2 import urlopen
import re

def index(request):
    if request.user.is_authenticated():
        return logged_in(request)
    else:
        return welcome(request)

def logged_in(request):
    user_songs = UserSong.objects.filter(user=request.user).all()
    return render_to_response("home.html", {"user_songs": user_songs,
                                            "own_songs": True,
                                            "request": request})

def login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect("/")
            else:
                login_form.errors.setdefault("username", []).append(
                                    "Bad username / password combination.")
                return render_to_response("registration/login.html",
                              { 'login_form': login_form , },
                              context_instance=RequestContext(request))
    else:
        login_form = LoginForm()
        return render_to_response("registration/login.html",
                                  { 'login_form': login_form , },
                                  context_instance=RequestContext(request))

def render_to_response_context(template, context, request):
    context['request'] = request
    return render_to_response(template, context,
                              context_instance = RequestContext(request))
    
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

def welcome(request):
    login_form = LoginForm()
    return render_to_response("registration/login.html",
                              { 'login_form': login_form , },
                              context_instance = RequestContext(request), )

def register(request):
    form_template = "registration/register.html"
    form_name = "register_form"
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            cd = register_form.cleaned_data
            # check to see if username already taken
            if not User.objects.filter(username=cd['username']):
                new_user = User.objects.create_user(cd['username'],cd['email'],
                                                    cd['password'])
                return render_to_response_context("registration/login.html",
                        { 'login_form': LoginForm(),
                          'newly_registered': True}, request)
            else:
                register_form = RegisterForm()
                register_form.errors.setdefault('username',[]).append("Username already in use.")
                return render_to_response_context(form_template,
                                                  {
                                                      form_name: register_form
                                                  },
                                                 request)
        else:
            return render_to_response_context(form_template,
                                      { form_name: register_form , }, request)
    else:
        register_form = RegisterForm()
        return render_to_response_context(form_template,
                                  { form_name: register_form , }, request )


def thanks(request):
    return HttpResponse("Thanks for signing up!")

@login_required
def add_song(request):
    form_template = 'add_song.html'
    form_name = 'add_song_form'
    # if something was submitted...
    if request.method == "POST":
        add_song_form = AddSongForm(request.POST)
        if add_song_form.is_valid():
            cd = add_song_form.cleaned_data
            song_exists = Song.objects.filter(title=cd['title'],
                                              artist=cd['artist'])
            if song_exists:
                form_song = song_exists[0]
            else:
                form_song = Song.objects.create(title=cd['title'],
                                                  artist=cd['artist'])
            raw_tags = cd['tags'].split(',')
            user_song_exists = UserSong.objects.filter(song=form_song,
                                              user=request.user)
            if user_song_exists: # check for duplicate songs:
                if add_song_form.errors.get("artist", None):
                    add_song_form.errors["artist"].append("You've\
                                                already added this song.")
                else:
                    add_song_form._errors["artist"] = ["You've already \
                                                already added this song."]
                return render_to_response_context(form_template,
                                                  {form_name: add_song_form},
                                                  request)
            user_song = UserSong.objects.create(song=form_song,
                            user=request.user, tab=cd['tab'],
                            ability=cd['ability'], private=cd['private'])
            for raw_tag in raw_tags:
                if raw_tag:
                    user_song.tags.add(
                        Tag.objects.get_or_create(name=raw_tag)[0])
            return HttpResponseRedirect("/")
            # if the song doesn't exist, create it
            # in any case, create UserSong
        else:
            return render_to_response_context(form_template,
                                      { form_name: add_song_form , }, request)
    else:
        add_song_form = AddSongForm()
        return render_to_response_context(form_template,
                                  { form_name: add_song_form , }, request)
            
def added(request):
    return HttpResponse("Thanks for adding a song.")

def edit_song(request, user_song_id):
    form_template = 'add_song.html'
    form_name = 'add_song_form'
    user_song = UserSong.objects.filter(id=user_song_id)[0]
    if request.method == "POST":
        song_form = AddSongForm(request.POST)
        if song_form.is_valid():
            cd = song_form.cleaned_data
            user_song.song = Song.objects.get_or_create(artist=cd['artist'],
                                           title=cd['title'])[0]
            user_song.tab = cd['tab']
            user_song.private = cd['private']
            user_song.ability = cd['ability']
            raw_tags = [tag.strip() for tag in cd['tags'].split(',')]
            user_song.tags.clear()
            for tag_name in raw_tags:
                if tag_name:
                    tag = Tag.objects.get_or_create(name=tag_name)[0]
                    if not user_song.tags.filter(name=tag_name):
                        user_song.tags.add(tag)
            user_song.save()
            return HttpResponseRedirect("/")
        else:
            return render_to_response_context(form_template,
                                {form_name: song_form, 'edit': True}, request)
    song = user_song.song
    song_form = AddSongForm()
    tags = ', '.join([tag['name'] for tag in user_song.tags.values()])
    song_details = {'title': song.title,
                    'artist': song.artist,
                    'tab': user_song.tab,
                    'private': user_song.private,
                    'ability': user_song.ability,
                    'tags': tags,
    }
    song_form = AddSongForm(song_details)
    return render_to_response_context(form_template,
                        {form_name: song_form, 'edit': True}, request)

def view_user(request, username):
    user_to_view = User.objects.filter(username=username)[0]
    if user_to_view == request.user:
        not_own_songs = False
    else:
        not_own_songs = True
    user_songs = UserSong.objects.filter(user=user_to_view)
    if user_songs:
        print user_songs
    return render_to_response_context("view_user.html",
                              {"user_songs": user_songs,
                              "not_own_songs": not_own_songs},
                              request)

def view_song(request, user_song_id):
    user_song = UserSong.objects.filter(id=user_song_id)[0]
    if user_song.private and user_song.user != request.user:
        return HttpResponse("That song's private!")
    return render_to_response("view_song.html",
        {"user_song": user_song, 'request': request},)
    
def scrape_ug(request):
    if not request.is_ajax() or not request.POST:
        return HttpResponseBadRequest()
    url = request.POST['url']
    if not 'ultimate-guitar.com' in url:
        return HttpResponseBadRequest()
    if '_tab' in url:
        pattern = "<title>(.*) {1,2}tab .*by (.*) @"
    elif '_btab' in url:
        pattern = "<title>(.*) {1,2}bass tab .*by (.*) @"
    elif '_crd' in url:
        pattern = "<title>(.*)  C.* by (.*) @"
    tit_art_regex = re.compile(pattern)
    html = urlopen(url).read()
    title, artist = tit_art_regex.search(html).groups()
    artist = artist.strip()
    title = title.strip()
    print "got this far"
    tab = re.search("<pre>(.*)</pre>", html, re.DOTALL).groups()[0]
    tab = re.sub("<span>|</span>", "", tab)
    if ("the " + artist).lower() in tab.lower():
        artist = " ".join([word.capitalize() for word in artist.split()])
        artist = "The " + artist.capitalize() # fuck you 'z'
    return HttpResponse("%s|||%s|||%s" % (title, artist, tab))

def delete_song(request):
    if (not request.is_ajax()) or (not request.POST):
        print "not ajax not post"
        return HttpResponseBadRequest()
    user_song_id = int(request.POST['song_id'])
    print user_song_id
    user_song = UserSong.objects.filter(id=user_song_id)[0]
    print user_song.user
    if user_song.user == request.user:
        user_song.delete()
        return HttpResponse("1")
    else:
        print "not correct user"
        return HttpResponseBadRequest()

def sort_dict(d):
    from operator import itemgetter
    sorted_d = sorted(d.iteritems(), key=itemgetter(1))
    sorted_d.reverse()
    sorted_d = sorted_tags[:40] if len(sorted_d) > 40 else sorted_d
    return sorted_d

def top_artists(request):
    all_usersongs = UserSong.objects.filter()
    song_counts = {}
    artist_counts = {}
    for usersong in all_usersongs:
        song = usersong.song
        artist = usersong.song.artist
        song_counts[song] = song_counts.setdefault(song, 0) + 1
        artist_counts[artist] = artist_counts.setdefault(artist, 0) + 1
    sorted_artists = sort_dict(artist_counts)
    return render_to_response_context("top_artists.html",
                              {"top_artists": sorted_artists, },
                              request)


def view_artist(request, artist_name):
    song_counts = {}
    tag_counts = {}
    user_counts = {}
    users = []
    artist_songs = Song.objects.filter(artist=artist_name)
    for song in artist_songs:
        user_songs = UserSong.objects.filter(song=song).all()
        song_counts[song] = len(user_songs)
        for user_song in user_songs:
            user_counts[user_song.user] = user_counts.setdefault(
                                            user_song.user, 0) + 1
            for tag in user_song.tags.all():
                tag_counts[tag] = tag_counts.setdefault(
                                                tag, 0) + 1
    sorted_songs = sort_dict(song_counts)
    sorted_tags = sort_dict(tag_counts)
    sorted_users = sort_dict(user_counts)
    return render_to_response_context("view_artist.html",
            { "top_tags": sorted_tags, "top_songs": sorted_songs,
              "top_users": sorted_users, "artist": artist_name},
            request)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
