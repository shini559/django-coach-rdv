from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class UserAuthTestCase(TestCase):
    def setUp(self):
        """Prépare les données nécessaires pour les tests."""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password': 'complexpassword123'
        }
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')

    def test_user_signup_and_login_successfully(self):
        """
        Teste le processus complet : inscription, puis connexion.
        """
        # --- Partie 1: Test de l'inscription ---

        # On envoie une requête POST pour créer un nouvel utilisateur
        response_signup = self.client.post(self.signup_url, {
            'username': self.user_data['username'],
            'password1': self.user_data['password'],
            'password2': self.user_data['password'],
        })

        # On vérifie que l'utilisateur a bien été créé dans la base de données
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())

        # Après l'inscription, l'utilisateur est automatiquement connecté et redirigé vers le dashboard
        self.assertRedirects(response_signup, self.dashboard_url)

        # --- Partie 2: Test de la connexion ---

        # D'abord, on se déconnecte pour pouvoir tester la connexion
        self.client.logout()

        # On envoie une requête POST pour se connecter avec les identifiants créés
        response_login = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        })

        # On vérifie que la connexion a réussi et qu'on est redirigé vers le dashboard
        self.assertRedirects(response_login, self.dashboard_url)

        # On vérifie que l'utilisateur est bien connecté dans la session
        self.assertTrue('_auth_user_id' in self.client.session)