from django.test import TestCase, Client
from django.urls import reverse

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