# Book My Coach - Application de Prise de Rendez-vous

Book My Coach est une application web complète développée avec Django, permettant à un coach sportif de gérer ses rendez-vous et à ses clients de réserver des séances en ligne.

## Fonctionnalités

* **Pour les visiteurs :**
    * Page d'accueil de présentation des services, témoignages et tarifs.
    * Formulaire de contact.
* **Pour les utilisateurs (clients) :**
    * Inscription et connexion sécurisées.
    * Tableau de bord personnel avec un design en "cartes" et un panneau latéral de détails.
    * Prise de rendez-vous via un formulaire dynamique affichant les créneaux disponibles.
    * Possibilité d'annuler ou de déplacer un rendez-vous.
    * Gestion de leur profil (nom, prénom, email, téléphone).
* **Pour le coach :**
    * Tableau de bord avec une vue **calendrier interactive** (FullCalendar) affichant tous les rendez-vous.
    * Possibilité de voir les détails de chaque séance (informations client, sujet).
    * Possibilité d'ajouter des notes privées à chaque séance et de mettre à jour son statut.

---

## Technologies utilisées

* **Back-End :** Python, Django
* **Front-End :** HTML, CSS, JavaScript
* **Framework CSS :** Bootstrap 5
* **Base de données :** SQLite (par défaut en développement)
* **Librairies Python notables :** `django-crispy-forms`, `crispy-bootstrap5`
* **Librairies JavaScript notables :** `FullCalendar`

---

## Installation et Lancement

Suivez ces étapes pour lancer le projet sur votre machine locale.

### Prérequis

* Python 3.x
* pip

### Étapes d'installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/shini559/django-coach-rdv.git
    cd django-coach-rdv
    ```

2.  **Créez et activez un environnement virtuel :**
    ```bash
    # Sur macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # Sur Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Installez les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Appliquez les migrations de la base de données :**
    ```bash
    python manage.py migrate
    ```

5.  **Créez un super-utilisateur** pour accéder à l'interface d'administration :
    ```bash
    python manage.py createsuperuser
    ```
    *Suivez les instructions pour créer votre compte administrateur.*

6.  **(Optionnel) Créez le groupe "Coach"** via l'interface d'administration (`/admin/`) et assignez-y un utilisateur pour tester les fonctionnalités du coach.

### Lancer l'application

Une fois l'installation terminée, lancez le serveur de développement :
```bash
python manage.py runserver