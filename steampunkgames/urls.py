from django.conf.urls import url, include
from steampg.steampunkgames import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^page/([0-9]+)/?$', views.page, name="page"),
    url(r'^authors/?$', views.authors, name="authors"),
    url(r'^authors/([a-zA-Z0-9_-]+)/?$', views.author, name="author"),
    url(r'^games/?$', views.games, name="games"),
    url(r'^games/([a-zA-Z0-9_-]+)/?$', views.game, name="game"),
    url(r'^login/?$', views.doLogin, name="login"),
    url(r'^logout/?$', views.doLogout, name="logout"),
    url(r'^dashboard/?$', views.dashboard, name="dashboard"),
    url(r'^dashboard/profile/?$', views.profile, name="profile"),
    url(r'^dashboard/game/?$', views.profileGame, name="profileGame"),
    url(r'^dashboard/images/?$', views.images, name="images"),
    url(r'^dashboard/edit/([0-9]+)/?$', views.editEntry, name="editEntry"),
    url(r'^([a-zA-Z0-9_-]+)/?$', views.entry, name="entry")
]
