import http.client
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, CreateView, DeleteView, TemplateView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from .forms import *
from .models import *
from .utils.Detector import *
from django.core import serializers
from django.http import JsonResponse
import json


class HomeView(TemplateView):
    template_name = 'main/home.html'


def register_client(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            return redirect('home')
        else:
            return redirect('register_client')

    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'main/login.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('home')
        else:
            return self.form_invalid(form)


class CustomLogoutView(LogoutView):
    template_name = 'main/home.html'


class Playlists_ListView(ListView):
    template_name = 'main/playlists.html'
    context_object_name = 'playlists'

    def dispatch(self, request, *args, **kwargs):  # определяет, какой метод должен быть вызван для обработки запроса
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):   # возвращает запрос к базе данных для получения объектов модели
        playlists_ = Playlist.objects.filter(user_id=self.request.user.id)
        return playlists_


class Playlist_CreateView(CreateView):
    model = Playlist
    template_name = 'main/add_playlist.html'
    form_class = PlaylistForm
    success_url = reverse_lazy('playlists')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Устанавливаем текущего пользователя как создателя плейлиста
        form.instance.user = self.request.user
        return super().form_valid(form)


class DeletePlaylistView(FormView):
    template_name = 'main/delete_playlist.html'
    form_class = DeletePlaylistForm
    success_url = reverse_lazy('playlists')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        playlists = form.cleaned_data['playlist']
        for playlist in playlists:
            songs = playlist.songs.all()
            for song in songs:
                song.delete()
            playlist.delete()
            return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):  # получения контекста, который будет передан в шаблон
        context = super().get_context_data(**kwargs)
        playlists = Playlist.objects.filter(user=self.request.user)
        context['playlists'] = playlists
        return context


class Playlist_Song(DetailView):
    model = Playlist
    template_name = 'main/song_list.html'
    context_object_name = 'songs'
    pk_url_kwarg = 'playlist_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist = self.get_object()
        playlist_json = serializers.serialize('json', playlist.songs.all(), fields=('title', 'audio_file'))
        songs_with_index = {}
        for i, song in enumerate(playlist.songs.all()):
            songs_with_index[i] = song

        context['songs'] = songs_with_index
        context['playlist_json'] = playlist_json
        return context


class Song_CreateView(CreateView):
    model = Song
    template_name = 'main/add_song.html'
    form_class = SongForm
    success_url = reverse_lazy('song_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        song = form.save(commit=False)
        song.user = self.request.user
        song.save()
        playlist_id = self.request.POST.get('playlist')
        playlist = Playlist.objects.get(id=playlist_id)
        playlist.songs.add(song)
        return redirect(self.success_url)

    def get_context_data(self, *, object_list=None, **kwargs):  # получения контекста, который будет передан в шаблон
        context = super().get_context_data(**kwargs)
        playlists = Playlist.objects.filter(user=self.request.user)
        context['playlists'] = playlists
        return context


class DeleteSongsView(FormView):
    template_name = 'main/delete_song.html'
    form_class = DeleteSongForm
    success_url = reverse_lazy('song_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        songs = form.cleaned_data['songs']
        for song in songs:
            playlists = song.playlists.all()
            for playlist in playlists:
                playlist.songs.remove(song)
            song.delete()
        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):  # получения контекста, который будет передан в шаблон
        context = super().get_context_data(**kwargs)
        songs = Song.objects.filter(user=self.request.user)
        context['songs'] = songs
        return context


class Song_ListView(ListView):
    template_name = 'main/song_list.html'
    context_object_name = 'songs'

    def dispatch(self, request, *args, **kwargs):  # определяет, какой метод должен быть вызван для обработки запроса
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):  # возвращает запрос к базе данных для получения объектов модели
        songs = Song.objects.filter(user_id=self.request.user.id)
        songs_with_index = {}
        for i, song in enumerate(songs):
            songs_with_index[i] = song
        return songs_with_index

    def get_context_data(self, *, object_list=None, **kwargs):  # получения контекста, который будет передан в шаблон
        context = super().get_context_data(**kwargs)
        songs = Song.objects.filter(user_id=self.request.user.id)
        playlist_json = serializers.serialize('json', songs, fields=('title', 'audio_file'))
        context['playlist_json'] = playlist_json
        return context


class Key_ListView(ListView):
    template_name = 'main/key.html'
    context_object_name = 'songs'

    def dispatch(self, request, *args, **kwargs):  # определяет, какой метод должен быть вызван для обработки запроса
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):  # возвращает запрос к базе данных для получения объектов модели
        songs = Song.objects.filter(user_id=self.request.user.id)
        songs_with_index = {}
        for i, song in enumerate(songs):
            songs_with_index[i] = song
        return songs_with_index


def get_key(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        file_path = body_data.get('file_path')
        key_, mode = Detector.get_key('.'+file_path)
        key_ = str(key_)
        mode = str(mode)
        print(key_, mode)
        return JsonResponse({'key': key_, 'mode': mode})
    return JsonResponse({'error': 'Invalid request method'})


class BPM_ListView(ListView):
    template_name = 'main/bpm.html'
    context_object_name = 'songs'

    def dispatch(self, request, *args, **kwargs):  # определяет, какой метод должен быть вызван для обработки запроса
        if not request.user.is_authenticated:
            return redirect('register_client')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):  # возвращает запрос к базе данных для получения объектов модели
        songs = Song.objects.filter(user_id=self.request.user.id)
        songs_with_index = {}
        for i, song in enumerate(songs):
            songs_with_index[i] = song
        return songs_with_index


def get_bpm(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        file_path = body_data.get('file_path')
        bpm_ = Detector.get_tempo('.'+file_path)
        return JsonResponse({'bpm': bpm_})
    return JsonResponse({'error': 'Invalid request method'})
