from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<id>", views.listing, name="listing"),
    path("listing/<id>/bid", views.bid, name="bid"),
    path("listing/<id>/close", views.close_auction, name="close"),
    path("listing/<id>/comment", views.comment, name="comment"),
    path("category/<id>", views.category, name="category"),
]
