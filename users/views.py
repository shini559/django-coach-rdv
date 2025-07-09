from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from datetime import datetime  # <-- L'import qui manquait

from coaching.models import Seance
from .forms import UserUpdateForm, ProfileUpdateForm, CustomUserCreationForm


def signup(request):
    """
    Gère l'inscription et la connexion automatique d'un nouvel utilisateur.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request,
                             f"Bienvenue, {user.username} ! Votre compte a été créé et vous êtes maintenant connecté.")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/signup.html', {'form': form})


@login_required
def dashboard(request):
    """
    Affiche un tableau de bord différent pour le coach et pour le client,
    avec la liste des séances séparées par heure exacte.
    """
    is_coach = request.user.groups.filter(name='Coach').exists()

    # On récupère toutes les séances pertinentes pour l'utilisateur
    if is_coach:
        all_user_seances = Seance.objects.all().order_by('date', 'heure_debut')
    else:
        all_user_seances = Seance.objects.filter(client=request.user).order_by('date', 'heure_debut')

    # On prépare les listes vides
    seances_a_venir = []
    seances_passees = []

    # On récupère la date et l'heure actuelles
    now = timezone.now()

    # On trie les séances en Python en comparant l'heure exacte
    for seance in all_user_seances:
        seance_datetime = timezone.make_aware(datetime.combine(seance.date, seance.heure_debut))

        if seance_datetime >= now:
            seances_a_venir.append(seance)
        else:
            seances_passees.append(seance)

    # On inverse la liste des séances passées pour avoir les plus récentes en premier
    seances_passees.reverse()

    context = {
        'is_coach': is_coach,
        'seances_a_venir': seances_a_venir,
        'seances_passees': seances_passees,
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/edit_profile.html', context)