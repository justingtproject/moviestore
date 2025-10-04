from django import forms
from .models import MovieRequest, MoviePetition

class MovieRequestForm(forms.ModelForm):
    class Meta:
        model = MovieRequest
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Movie name"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Movie description"}),
        }

class MoviePetitionForm(forms.ModelForm):
    class Meta:
        model = MoviePetition
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Movie name"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Movie description"}),
        }
