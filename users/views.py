from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from coaching.models import Seance

def signup(request):
    """
    Gère l'inscription d'un nouvel utilisateur.
    """
    if request.method == 'POST':
        # Le formulaire est soumis avec des données
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Crée et sauvegarde le nouvel utilisateur
            username = form.cleaned_data.get('username')
            messages.success(request, f"Votre compte a été créé avec succès, {username} ! Vous pouvez maintenant vous connecter.")
            return redirect('home') # Redirige vers la page d'accueil après inscription
    else:
        # La page est accédée via une requête GET, on affiche un formulaire vide
        form = UserCreationForm()

    # Passe le formulaire au template pour l'affichage
    return render(request, 'users/signup.html', {'form': form})


@login_required
def dashboard(request):
    """
    Affiche un tableau de bord différent pour le coach et pour le client,
    avec la liste des séances appropriées.
    """
    is_coach = request.user.groups.filter(name='Coach').exists()

    if is_coach:
        # Le coach voit toutes les séances, triées par date et heure
        seances = Seance.objects.all().order_by('date', 'heure_debut')
    else:
        # Le client ne voit que ses propres séances
        seances = Seance.objects.filter(client=request.user).order_by('date', 'heure_debut')

    context = {
        'is_coach': is_coach,
        'seances': seances,  # 2. Ajouter les séances au contexte
    }
    return render(request, 'users/dashboard.html', context)