from django import forms
from .models import Seance
from datetime import time, timedelta, datetime
class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['date', 'heure_debut', 'sujet']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
        }

class SeanceNotesForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['notes_coach']


class SeanceForm(forms.ModelForm):
    # On définit le champ heure_debut ici pour en faire un menu déroulant
    heure_debut = forms.ChoiceField(label="Heure du rendez-vous")

    class Meta:
        model = Seance
        fields = ['date', 'heure_debut', 'sujet']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # On récupère les créneaux passés par la vue (on fera ça à l'étape suivante)
        creneaux_disponibles = kwargs.pop('creneaux', [])
        super(SeanceForm, self).__init__(*args, **kwargs)

        # On met à jour les choix du champ heure_debut avec la liste des créneaux
        self.fields['heure_debut'].choices = creneaux_disponibles
class ContactForm(forms.Form):
    nom = forms.CharField(max_length=100, label="Votre nom")
    email = forms.EmailField(label="Votre email")
    message = forms.CharField(widget=forms.Textarea, label="Votre message")