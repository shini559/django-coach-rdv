# coaching/models.py

from django.db import models
from django.contrib.auth.models import User

class Seance(models.Model):
    """
    Représente un rendez-vous entre un client et un coach.
    """
    STATUS_CHOICES = [
        ('A_VENIR', 'À venir'),
        ('PASSEE', 'Passée'),
        ('ANNULEE', 'Annulée'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seances_client')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seances_coach')
    date = models.DateField()
    heure_debut = models.TimeField()
    sujet = models.CharField(max_length=200)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='A_VENIR')
    notes_coach = models.TextField(blank=True, null=True) # Pour la fonctionnalité bonus

    class Meta:
        # Assure qu'un coach ne peut pas avoir deux rendez-vous en même temps
        unique_together = ('coach', 'date', 'heure_debut')

    def __str__(self):
        return f"Séance de {self.client.username} avec {self.coach.username} le {self.date} à {self.heure_debut}"