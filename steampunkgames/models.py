from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date

class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    name = models.CharField(max_length=1000, default="", blank=True)
    created = models.DateField(auto_now_add=True)
    website = models.CharField(max_length=1000, default="", blank=True)
    twitter = models.CharField(max_length=1000, default="", blank=True)
    bio = models.TextField(default="", blank=True)
    image = models.FileField(upload_to='profile_images/', blank=True)
    
    @property
    def displayName(self):
        if len(self.name) > 0:
            return self.name
        return self.user.username
    
    @property
    def active(self):
        if self.created > date.today() - timedelta(weeks=5):
            return True
        return self.game and len(Entry.objects.filter(state='pu', posted__gte=datetime.now() - timedelta(weeks=5)).exclude(game=self.game)) > 0
    
    def __str__(self):
        return self.user.username

class Game(models.Model):
    owner = models.OneToOneField(User, related_name="game", blank=True, null=True)
    name = models.CharField(max_length=1000)
    slug = models.CharField(max_length=1000)
    link = models.CharField(default="", max_length=1000, blank=True)
    description = models.TextField(default="", blank=True)
    image = models.FileField(upload_to='game_images/', blank=True)
    
    @property
    def onList(self):
        return self.owner and self.owner.profile.active
    
    def __str__(self):
        if self.owner:
            return self.name + " by " + self.owner.profile.displayName
        else:
            return self.name

class Entry(models.Model):
    UNPUBLISHED = 'un'
    PUBLISHED = 'pu'
    STATES = (
        ('un', 'Unpublished'),
        ('pu', 'Published')
    )
    posted = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(User, related_name="games")
    game = models.ForeignKey(Game, related_name="entries", blank=True, null=True)
    state = models.CharField(max_length=2, choices=STATES)
    title = models.CharField(max_length=1000, default="", blank=True)
    slug = models.CharField(max_length=1000, default="", blank=True)
    lede = models.TextField(default="", blank=True)
    text = models.TextField(default="", blank=True)
    activeTitle = models.CharField(max_length=1000, default="", blank=True)
    activeSlug = models.CharField(max_length=1000, default="", blank=True)
    activeLede = models.TextField(default="", blank=True)
    activeText = models.TextField(default="", blank=True)
    
    @property
    def displayTitle(self):
        if len(self.activeTitle) > 0:
            return self.activeTitle
        if len(self.title) > 0:
            return self.title
        return "Untitled Article"
    
    @property
    def published(self):
        return self.state == Entry.PUBLISHED
    
    @property
    def displayState(self):
        return {'un': 'Unpublished', 'pu': 'Published'}[self.state]
    
    def __str__(self):
        return self.activeTitle + " by " + self.owner.username + " (" + self.state + ")"

class Image(models.Model):
    owner = models.ForeignKey(User, related_name="images")
    image = models.FileField(upload_to='entry_images/')
    posted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.image
