from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Seance
from datetime import date, time


class CoachingViewsTestCase(TestCase):
    def setUp(self):
        """Cette méthode est appelée avant chaque test."""
        self.client = Client()

    def test_home_page_loads_correctly(self):
        """Teste si la page d'accueil renvoie un statut 200."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page_loads_correctly(self):
        """Teste si la page de contact renvoie un statut 200."""
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)


class SeanceCreationTestCase(TestCase):
    def setUp(self):
        """Prépare l'environnement pour le test de création de séance."""
        self.client = Client()

        # Crée un utilisateur client
        self.client_user = User.objects.create_user(
            username='testclient',
            password='complexpassword123'
        )

        # Crée un groupe "Coach" et un utilisateur coach
        coach_group = Group.objects.create(name='Coach')
        self.coach_user = User.objects.create_user(
            username='testcoach',
            password='coachpassword123'
        )
        self.coach_user.groups.add(coach_group)

        # Connecte le client
        self.client.login(username='testclient', password='complexpassword123')

        self.booking_url = reverse('prendre-rdv')

    def test_client_can_book_seance(self):
        """Teste si un client connecté peut prendre un rendez-vous."""

        seance_data = {
            'date': '2025-10-15',
            'heure_debut': '14:30',
            'sujet': 'PERTE POIDS'
        }

        # On envoie la requête
        response = self.client.post(self.booking_url, seance_data)

        if response.status_code == 200:
            form = response.context.get('form')
            if form:
                print("\n--- ERREURS DU FORMULAIRE DANS LE TEST ---")
                print(form.errors.as_json())
                print("------------------------------------------\n")

        self.assertRedirects(response, reverse('dashboard'))