# coaching/models.py

from django.db import models
from django.contrib.auth.models import User

class Seance(models.Model):
    """
    Représente un rendez-vous entre un client et un coach.
    """


    SUJET_CHOICES = [
        ('PERTE POIDS', '🔥 Perte de poids / sèche'),
        ('PRISE MASSE', '💪 Prise de masse / hypertrophie'),
        ('SOUPLESSE', '🧘 Souplesse et mobilité'),
        ('REMISE FORME', '🏃 Remise en forme / reprise du sport'),
        ('RENFORCEMENT', '🧍‍♂️ Renforcement musculaire général'),
        ('PREPA PHYSIQUE', '⚽ Préparation physique spécifique (sport en particulier)'),
        ('EQUILIBRE', '♻️ Équilibre sport / récupération / sommeil'),
        ('TRAVAIL CIBLE', '🦵 Travail ciblé (abdos, fessiers, bras, jambes…)'),
        ('MOTIVATION', '🧠 Motivation et discipline dans l\'entraînement'),
        ('POST BLESSURE', '👩‍⚕️ Accompagnement post-blessure / réathlétisation'),
        ('ENDURANCE', '⏱️ Coaching pour améliorer l’endurance / cardio'),
        ('PROGRAMME', '📅 Création de programme personnalisé'),
        ('AUTRE', '❓ Autre (à préciser)'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seances_client')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seances_coach')
    date = models.DateField()
    heure_debut = models.TimeField()
    sujet = models.CharField(max_length=100, choices=SUJET_CHOICES)
    notes_coach = models.TextField(blank=True, null=True)



    class Meta:
        # Assure qu'un coach ne peut pas avoir deux rendez-vous en même temps
        unique_together = ('coach', 'date', 'heure_debut')

    def __str__(self):
        return f"Séance de {self.client.username} avec {self.coach.username} le {self.date} à {self.heure_debut}"