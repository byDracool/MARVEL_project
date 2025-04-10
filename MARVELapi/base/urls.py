from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name = "home"),
    path('characters/', views.characters, name = "characters"),
    path('character/<str:name>/', views.character_detail, name="character_detail"),
    path('comics/', views.comics_list, name = "comics"),
    path('comic_detail/', views.comic_detail, name="comic_detail"),
    path('creators/', views.creators_list, name = "creators"),
    path('creator_detail/', views.creator_detail, name="creator_detail"),
    path('creator_comics/', views.creator_detail, name="creator_comics"),
    path('creator_series/', views.creator_detail, name="creator_series"),
    path('creator_stories/', views.creator_detail, name="creator_stories"),
    path('events/', views.events_list, name = "events"),
    path('event/<str:title>/', views.event_detail, name="event_detail"),
    path('series/', views.series_list, name = "series"),
    path('serie/', views.serie_detail, name='serie_detail'),
]