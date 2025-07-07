from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from coaching.models import Seance
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import login
from django.utils import timezone


def signup(request):
    """
    Gère l'inscription et la connexion automatique d'un nouvel utilisateur.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # La méthode form.save() renvoie l'objet utilisateur nouvellement créé
            user = form.save()

            # 2. Connecter l'utilisateur nouvellement créé
            login(request, user)

            messages.success(request,
                             f"Bienvenue, {user.username} ! Votre compte a été créé et vous êtes maintenant connecté.")

            # 3. Rediriger vers le tableau de bord
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'users/signup.html', {'form': form})


@login_required
def dashboard(request):
    is_coach = request.user.groups.filter(name='Coach').exists()

    if is_coach:
        seances = Seance.objects.all()
    else:
        seances = Seance.objects.filter(client=request.user)

    # 2. On récupère la date du jour
    today = timezone.now().date()

    # 3. On filtre les séances en se basant sur la date
    seances_a_venir = seances.filter(date__gte=today).order_by('date', 'heure_debut')
    seances_passees = seances.filter(date__lt=today).order_by('-date', '-heure_debut')

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