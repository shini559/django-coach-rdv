from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SeanceForm

def home(request):
    """
    Afficher la page d'accueil du site de coaching.
    :param request:
    :return:
    """
    return render(request, 'coaching/accueil.html')

@login_required
def prise_rdv(request):
    # On cherche le coach (on suppose qu'il n'y en a qu'un pour l'instant)
    try:
        coach = User.objects.get(groups__name='Coach')
    except User.DoesNotExist:
        messages.error(request, "Le coach n'est pas configuré. Prise de RDV impossible.")
        return redirect('home')

    if request.method == 'POST':
        form = SeanceForm(request.POST)
        if form.is_valid():
            # Ne sauvegarde pas encore en base de données
            seance = form.save(commit=False)
            # Ajoute le client (l'utilisateur connecté) et le coach
            seance.client = request.user
            seance.coach = coach
            # Sauvegarde l'objet complet
            seance.save()
            messages.success(request, 'Votre rendez-vous a été pris avec succès !')
            return redirect('dashboard')
    else:
        form = SeanceForm()

    return render(request, 'coaching/prise_rdv.html', {'form': form})