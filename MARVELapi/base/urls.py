from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name = "home"),
    path('characters/', views.characters, name = "characters"),
    path('character/<str:name>/', views.character_detail, name="character_detail"),
    path('comics/', views.comics_list, name = "comics"),
    path('comic_detail/', views.comic_detail, name="comic_detail"),
]