from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Song, Playlist, User


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='username')
    password = forms.CharField(label='password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'TextInput'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'TextInput'}))


class SongForm(forms.ModelForm):
    playlist = forms.ModelChoiceField(queryset=Playlist.objects.none(), empty_label=None, required=True)

    class Meta:
        model = Song
        fields = ['title', 'audio_file', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': True}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['playlist'].queryset = Playlist.objects.filter(user=user)


class PlaylistForm(forms.ModelForm):

    class Meta:
        model = Playlist
        fields = ['title', 'image']

    widgets = {
        'image': forms.ClearableFileInput(attrs={'required': True}),
    }


class DeleteSongForm(forms.Form):
    songs = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['songs'].queryset = Song.objects.filter(user=user)
        self.fields['songs'].empty_label = None


class DeletePlaylistForm(forms.Form):
    playlist = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['playlist'].queryset = Playlist.objects.filter(user=user)
        self.fields['playlist'].empty_label = None
