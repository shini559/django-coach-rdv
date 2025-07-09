
from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm



class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On supprime simplement le texte d'aide, sans toucher aux champs
        self.fields['username'].help_text = ''

    class Meta(UserCreationForm.Meta):
        # On hérite de la classe Meta parente, y compris de ses champs
        # (username, password, password2)
        fields = UserCreationForm.Meta.fields

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['telephone']