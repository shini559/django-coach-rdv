from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SeanceForm, SeanceNotesForm
from .models import Seance
from datetime import datetime, timedelta, time
from django.http import JsonResponse

def home(request):
    """
    Affiche un contenu différent sur l'accueil si l'utilisateur est connecté.
    """
    context = {}
    return render(request, 'coaching/accueil.html', context)


@login_required
def prise_rdv(request):
    try:
        coach = User.objects.get(groups__name='Coach')
    except User.DoesNotExist:
        messages.error(request, "Le coach n'est pas configuré.")
        return redirect('home')

    creneaux_disponibles = []
    date_selectionnee = request.GET.get('date')

    if date_selectionnee:
        date_obj = datetime.strptime(date_selectionnee, '%Y-%m-%d').date()

        # Générer tous les créneaux possibles pour la journée
        heure_debut_journee = time(9, 0)
        heure_fin_journee = time(18, 0)
        duree_seance = timedelta(minutes=30)

        tous_les_creneaux = []
        creneau_actuel = datetime.combine(date_obj, heure_debut_journee)
        heure_fin_datetime = datetime.combine(date_obj, heure_fin_journee)

        while creneau_actuel < heure_fin_datetime:
            tous_les_creneaux.append(creneau_actuel.time())
            creneau_actuel += duree_seance

        # Récupérer les créneaux déjà réservés
        seances_reservees = Seance.objects.filter(date=date_obj, coach=coach)
        creneaux_reserves = [s.heure_debut for s in seances_reservees]

        # Filtrer pour ne garder que les créneaux disponibles
        creneaux_disponibles_obj = [t for t in tous_les_creneaux if t not in creneaux_reserves]

        # Formatter pour le menu déroulant
        creneaux_disponibles = [(t.strftime('%H:%M'), f"{t.strftime('%Hh%M')}") for t in creneaux_disponibles_obj]

    if request.method == 'POST':
        form = SeanceForm(request.POST, creneaux=creneaux_disponibles)
        if form.is_valid():
            seance = form.save(commit=False)
            seance.client = request.user
            seance.coach = coach
            seance.date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
            seance.heure_debut = datetime.strptime(request.POST.get('heure_debut'), '%H:%M').time()
            seance.save()
            messages.success(request, 'Votre rendez-vous a été pris avec succès !')
            return redirect('dashboard')
    else:
        # Initialise le formulaire avec la date si elle est dans l'URL
        initial_data = {'date': date_selectionnee} if date_selectionnee else {}
        form = SeanceForm(initial=initial_data, creneaux=creneaux_disponibles)

    return render(request, 'coaching/prise_rdv.html', {'form': form})


@login_required
def seance_edit(request, pk):
    seance = get_object_or_404(Seance, pk=pk)

    # Vérifie que seul le coach peut modifier
    if not request.user.groups.filter(name='Coach').exists():
        messages.error(request, "Vous n'avez pas l'autorisation de faire cela.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SeanceNotesForm(request.POST, instance=seance)
        if form.is_valid():
            form.save()
            messages.success(request, 'La séance a été mise à jour.')
            return redirect('dashboard')
    else:
        form = SeanceNotesForm(instance=seance)

    context = {
        'form': form,
        'seance': seance
    }
    return render(request, 'coaching/seance_edit.html', context)


@login_required
def seance_detail(request, pk):
    seance = get_object_or_404(Seance, pk=pk)

    # Vérifie que l'utilisateur a le droit de voir cette séance
    is_coach = request.user.groups.filter(name='Coach').exists()
    if not is_coach and seance.client != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette séance.")
        return redirect('dashboard')

    context = {
        'seance': seance,
        'is_coach': is_coach,
    }
    return render(request, 'coaching/seance_detail.html', context)


@login_required
def all_seances_api(request):
    # On s'assure que seul le coach peut voir toutes les séances
    if not request.user.groups.filter(name='Coach').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    seances = Seance.objects.all()

    # On formate les données pour FullCalendar
    events = []
    for seance in seances:
        events.append({
            'title': f"{seance.sujet} - {seance.client.first_name or seance.client.username}",
            'start': datetime.combine(seance.date, seance.heure_debut).isoformat(),
            'end': (datetime.combine(seance.date, seance.heure_debut) + timedelta(minutes=30)).isoformat(),
            'url': f"/seance/{seance.pk}/",  # Lien vers la page de détail
        })

    return JsonResponse(events, safe=False)