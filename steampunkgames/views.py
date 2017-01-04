from django.shortcuts import render
from django.shortcuts import get_object_or_404 as go4
from steampg.steampunkgames.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from datetime import datetime
from django.conf import settings
import random

ENTRIES_PER_PAGE = 10
OUR_GAMES_PER_PAGE = 3

def secure(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def shuffled(l):
    l = list(l)
    random.shuffle(l)
    return l

def home(request):
    return page(request, 1)

def page(request, page):
    return render(request, "home.html", {"entries": Entry.objects.filter(state="pu").order_by("-posted")[(int(page) - 1) * ENTRIES_PER_PAGE:int(page) * ENTRIES_PER_PAGE], "games": shuffled([g for g in Game.objects.all() if g.onList])[:OUR_GAMES_PER_PAGE], "page": page, "prevIndex": int(page) - 1, "nextIndex": int(page) + 1, "hasPrev": int(page) > 1, "hasNext": len(Entry.objects.filter(state="pu").order_by("-posted")[int(page) * ENTRIES_PER_PAGE:]) > 0})

def authors(request):
    return render(request, "authors.html", {"authors": [u for u in User.objects.all() if u.profile.active]})

def author(request, accountName):
    author = go4(User, username=accountName)
    return render(request, "author.html", {"author": author, "entries": Entry.objects.filter(state="pu", owner=author).order_by("-posted")})

def games(request):
    return render(request, "games.html", {"games": Game.objects.order_by("owner", "name").all()})

def game(request, slug):
    game = go4(Game, slug=slug)
    return render(request, "game.html", {"game": game, "entries": Entry.objects.filter(state="pu", game=game).order_by("-posted")})

def entry(request, slug):
    return render(request, "entry.html", {"entry": go4(Entry, activeSlug=slug, state="pu")})

def entryDraft(request, slug, secret):
    entry = go4(Entry, slug=slug)
    if entry.secret != secret:
        return HttpResponseForbidden()
    return render(request, "entryDraft.html", {"entry": entry})

@secure
def doLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('dashboard'))
        return HttpResponseRedirect(reverse('home'))
    return render(request, "login.html")

@secure
def doLogout(request):
    if request.method == 'POST':
        logout(request)
    return HttpResponseRedirect(reverse('home'))

@secure
def dashboard(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method == 'POST':
        entry = Entry(owner=request.user, state=Entry.UNPUBLISHED)
        entry.save()
        return HttpResponseRedirect(reverse('editEntry', args=[entry.id]))
    return render(request, "dashboard.html", {"entries": Entry.objects.filter(owner=request.user).order_by("-state", "-posted")})
    
class ProfileForm(ModelForm):
    class Meta:
        model=Profile
        fields=["name", "bio", "website", "twitter", "image"]

@secure
def profile(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    form = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profile'))
    return render(request, "profile.html", {"form": form})

class ProfileGameForm(ModelForm):
    class Meta:
        model=Game
        fields=["name", "link", "description", "image"]

@secure
def profileGame(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    form = ProfileGameForm(instance=request.user.game)
    if request.method == 'POST':
        form = ProfileGameForm(request.POST, request.FILES, instance=request.user.game)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profileGame'))
    return render(request, "profileGame.html", {"form": form})

class EntryForm(ModelForm):
    class Meta:
        model=Entry
        fields=["game", "title", "slug", "lede", "text"]

@secure
def editEntry(request, entryID):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    entry = go4(Entry, id=entryID, owner=request.user)
    form = EntryForm(instance=entry)
    commandErrors = []
    if request.method == "POST":
        if "command" in request.POST:
            cmd = request.POST["command"]
            if cmd == "publish" or cmd == "update":
                # check slug uniqueness and everything having content
                otherSlugs = Entry.objects.filter(activeSlug=entry.slug)
                if len(entry.title) == 0:
                    commandErrors.append("Please specify a title.")
                if len(entry.slug) == 0:
                    commandErrors.append("Please specify a slug.")
                elif len(otherSlugs) > 0 and not otherSlugs.all()[0].id == entry.id:
                    commandErrors.append("Slug is already taken by another post!")
                if len(entry.lede) == 0:
                    commandErrors.append("Please specify a lede.")
                if len(entry.text) == 0:
                    commandErrors.append("Please specify a text.")
                if len(commandErrors) == 0:
                    entry.activeTitle = entry.title
                    entry.activeSlug = entry.slug
                    entry.activeLede = entry.lede
                    entry.activeText = entry.text
                    entry.state = Entry.PUBLISHED
                    if cmd == "publish":
                        entry.posted = datetime.now()
                    entry.save()
                    return HttpResponseRedirect(reverse('editEntry', args=[entry.id]))
            if cmd == "unpublish":
                entry.state = Entry.UNPUBLISHED
                entry.save()
                return HttpResponseRedirect(reverse('editEntry', args=[entry.id]))
            if cmd == "revert":
                entry.title = entry.activeTitle
                entry.slug = entry.activeSlug
                entry.lede = entry.activeLede
                entry.text = entry.activeText
                entry.save()
                form = EntryForm(instance=entry)
                return HttpResponseRedirect(reverse('editEntry', args=[entry.id]))
            if cmd == "delete":
                entry.delete()
                return HttpResponseRedirect(reverse('steampg.steampunkgames.views.dashboard'))
        else:
            form = EntryForm(request.POST, instance=entry)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('editEntry', args=[entry.id]))
    return render(request, "editEntry.html", {"entry": entry, "form": form, "commandErrors": commandErrors})

class ImageForm(ModelForm):
    class Meta:
        model=Image
        fields=["image"]

@secure
def images(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    img = Image(owner=request.user)
    form = ImageForm(instance=img)
    if request.method == "POST":
        if "delete" in request.POST:
            go4(Image, id=int(request.POST["delete"], owner=request.user)).delete()
        else:
            form = ImageForm(request.POST, request.FILES, instance=img)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('images'))
    return render(request, "images.html", {"form": form, "images": request.user.images.order_by("-posted")})

class GameForm(ModelForm):
    class Meta:
        model=Game
        fields=["name", "slug", "link", "description", "image"]

@secure
def manageGames(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    game = Game()
    form = GameForm(instance=game)
    if request.method == "POST":
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('manageGames'))
    return render(request, "manageGames.html", {"form": form, "games": Game.objects.filter(owner=None).order_by("name").all()})

@secure
def editGame(request, gameID):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    game = go4(Game, id=gameID)
    if game.owner:
        return HttpResponseForbidden()
    form = GameForm(instance=game)
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('editGame', args=[slug]))
    return render(request, "editGame.html", {"game": game, "form": form})
