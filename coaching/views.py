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
    """
    Gère la prise de rendez-vous, le calcul des créneaux disponibles
    et la logique de déplacement d'un rendez-vous existant.
    """
    # Étape 1 : Récupérer le coach
    try:
        coach = User.objects.get(groups__name='Coach')
    except User.DoesNotExist:
        messages.error(request, "Le coach n'est pas configuré. Prise de RDV impossible.")
        return redirect('home')

    # Étape 2 : Gérer un éventuel déplacement de RDV
    reschedule_id = request.GET.get('reschedule_id')
    initial_data = {}
    if reschedule_id:
        seance_a_deplacer = get_object_or_404(Seance, pk=reschedule_id, client=request.user)
        initial_data['sujet'] = seance_a_deplacer.sujet
        request.session['seance_a_deplacer_id'] = seance_a_deplacer.id

    # Étape 3 : Calculer les créneaux disponibles en fonction de la date choisie
    creneaux_disponibles = []
    date_selectionnee = request.GET.get('date')

    if date_selectionnee:
        try:
            date_obj = datetime.strptime(date_selectionnee, '%Y-%m-%d').date()

            # Définir les heures de travail et la durée des séances
            heure_debut_journee = time(9, 0)
            heure_fin_journee = time(18, 0)
            duree_seance = timedelta(minutes=30)

            # Générer tous les créneaux théoriques de la journée
            tous_les_creneaux = []
            creneau_actuel = datetime.combine(date_obj, heure_debut_journee)
            heure_fin_datetime = datetime.combine(date_obj, heure_fin_journee)
            while creneau_actuel < heure_fin_datetime:
                tous_les_creneaux.append(creneau_actuel.time())
                creneau_actuel += duree_seance

            # Récupérer les créneaux déjà réservés pour ce jour
            seances_reservees = Seance.objects.filter(date=date_obj, coach=coach)
            creneaux_reserves = [s.heure_debut for s in seances_reservees]

            # Filtrer pour ne garder que les créneaux où il n'y a pas de réservation
            creneaux_disponibles_obj = [t for t in tous_les_creneaux if t not in creneaux_reserves]

            # Formatter la liste pour le menu déroulant du formulaire
            creneaux_disponibles = [(t.strftime('%H:%M'), f"{t.strftime('%Hh%M')}") for t in creneaux_disponibles_obj]
        except ValueError:
            # Gère le cas où la date dans l'URL est mal formée
            messages.error(request, "Format de date invalide.")
            date_selectionnee = None

    # Étape 4 : Gérer la soumission du formulaire (méthode POST)
    if request.method == 'POST':
        form = SeanceForm(request.POST, creneaux=creneaux_disponibles)
        if form.is_valid():
            seance = form.save(commit=False)
            seance.client = request.user
            seance.coach = coach
            # On s'assure que les données de date et heure sont correctement formatées
            seance.date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
            seance.heure_debut = datetime.strptime(request.POST.get('heure_debut'), '%H:%M').time()
            seance.save()

            # Gérer la suppression de l'ancien RDV si c'était un déplacement
            old_seance_id = request.session.get('seance_a_deplacer_id')
            if old_seance_id:
                try:
                    Seance.objects.get(pk=old_seance_id).delete()
                    del request.session['seance_a_deplacer_id']
                    messages.success(request, 'Votre rendez-vous a été déplacé avec succès !')
                except Seance.DoesNotExist:
                    pass
            else:
                messages.success(request, 'Votre rendez-vous a été pris avec succès !')

            return redirect('dashboard')
    else:
        # Étape 5 : Gérer l'affichage initial du formulaire (méthode GET)
        if date_selectionnee:
            initial_data['date'] = date_selectionnee
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
    if not request.user.groups.filter(name='Coach').exists():
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    seances = Seance.objects.all()

    events = []
    for seance in seances:
        events.append({
            'title': f"{seance.get_sujet_display()} - {seance.client.first_name or seance.client.username}",
            'start': datetime.combine(seance.date, seance.heure_debut).isoformat(),
            'end': (datetime.combine(seance.date, seance.heure_debut) + timedelta(minutes=30)).isoformat(),
            'url': f"/seance/{seance.pk}/",
        })

    return JsonResponse(events, safe=False)

@login_required
def seance_detail_api(request, pk):
    try:
        seance = Seance.objects.get(pk=pk)
    except Seance.DoesNotExist:
        return JsonResponse({'error': 'Rendez-vous non trouvé'}, status=404)

    # Vérification des permissions
    is_coach = request.user.groups.filter(name='Coach').exists()
    if not is_coach and seance.client != request.user:
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    # Formater les données pour les renvoyer en JSON
    data = {
        'id': seance.id,
        'date': seance.date.strftime('%A %d %B %Y'),
        'heure_debut': seance.heure_debut.strftime('%Hh%M'),
        'sujet': seance.get_sujet_display(),

    }
    return JsonResponse(data)


@login_required
def cancel_seance(request, pk):
    # On accepte uniquement les requêtes POST pour la sécurité
    if request.method == 'POST':
        seance = get_object_or_404(Seance, pk=pk)

        # On vérifie que seul le client concerné ou un coach peut annuler
        is_coach = request.user.groups.filter(name='Coach').exists()
        if seance.client == request.user or is_coach:
            seance.delete()
            return JsonResponse({'success': True, 'message': 'Le rendez-vous a été annulé.'})
        else:
            return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)

    return JsonResponse({'success': False, 'error': 'Requête invalide'}, status=400)