from django import forms
from django.forms import ModelForm
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

class ArtistForm(ModelForm):
    class Meta:
        model = Artist
        fields = "__all__"
        widgets = {
            'artistName': forms.TextInput(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),
            'bio': forms.Textarea(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),
            'hometown': forms.TextInput(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),
            'birthDate': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Select Date','type': 'date'}),
            'genre': forms.Select(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'})
    }
        
class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['albumName', 'releaseDate', 'genre', 'description', 'artistID']
        widgets = {
        'albumName': forms.TextInput(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),
        'length': forms.TextInput(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),        
        'genre': forms.Select(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),
        'releaseDate': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date', 'style': 'width:50%'}),
        'description': forms.TextInput(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),
        'artistID': forms.Select(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'})
        }

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['songName', 'releaseDate', 'streams', 'albumID']
        widgets = {
            'songName': forms.TextInput(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),
            'length': forms.TextInput(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'}),        
            'releaseDate': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date', 'style': 'width:50%'}),
            'streams': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 50%'}),
            'albumID': forms.Select(attrs={'class':'form-control', 'placeholder':"", 'style': 'width:50%'})        
        }

    def save(self, commit=True):
        # Get the album associated with this song
        album = self.cleaned_data['albumID']

        # Set the artistID of the song to the artistID of the album
        self.instance.artistID = album.artistID
        self.instance.genre = album.genre

        # Call the original save method to save the form
        return super().save(commit=commit)
    
class SearchForm(forms.Form):
    query = forms.CharField(label='Search')
    
