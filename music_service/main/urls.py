from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('register_client/', views.register_client, name='register_client'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('add_playlist/', Playlist_CreateView.as_view(), name='add_playlist'),
    path('delete_playlist/', DeletePlaylistView.as_view(), name='delete_playlist'),
    path('playlists/', Playlists_ListView.as_view(), name='playlists'),
    path('playlist_songs/<int:playlist_id>/', Playlist_Song.as_view(), name='playlist_songs'),

    path('add_song/', Song_CreateView.as_view(), name='add_song'),
    path('delete_song/', DeleteSongsView.as_view(), name='delete_song'),
    path('song_list/', Song_ListView.as_view(), name='song_list'),

    path('key/', Key_ListView.as_view(), name='key'),
    path('key/get_key/', views.get_key, name='get_key'),
    path('bmp/', BPM_ListView.as_view(), name='bpm'),
    path('key/get_bpm/', views.get_bpm, name='get_bpm')
  ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
