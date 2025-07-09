from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SeanceForm, SeanceNotesForm, ContactForm
from .models import Seance
from datetime import datetime, timedelta, time
from django.http import JsonResponse

def home(request):
    """
    Affiche un contenu différent sur l'accueil si l'utilisateur est connecté.
    """
    context = {}
    return render(request, 'coaching/accueil.html', context)


# coaching/views.py

@login_required
def prise_rdv(request):
    try:
        coach = User.objects.get(groups__name='Coach')
    except User.DoesNotExist:
        messages.error(request, "Le coach n'est pas configuré.")
        return redirect('home')

    # On détermine la date sélectionnée, que ce soit en GET ou en POST
    date_selectionnee_str = request.GET.get('date') if request.method == 'GET' else request.POST.get('date')

    creneaux_disponibles = []
    if date_selectionnee_str:
        try:
            date_obj = datetime.strptime(date_selectionnee_str, '%Y-%m-%d').date()
            heure_debut_journee = time(9, 0)
            heure_fin_journee = time(18, 0)
            duree_seance = timedelta(minutes=30)
            tous_les_creneaux = []
            creneau_actuel = datetime.combine(date_obj, heure_debut_journee)
            heure_fin_datetime = datetime.combine(date_obj, heure_fin_journee)
            while creneau_actuel < heure_fin_datetime:
                tous_les_creneaux.append(creneau_actuel.time())
                creneau_actuel += duree_seance
            seances_reservees = Seance.objects.filter(date=date_obj, coach=coach)
            creneaux_reserves = [s.heure_debut for s in seances_reservees]
            creneaux_disponibles_obj = [t for t in tous_les_creneaux if t not in creneaux_reserves]
            creneaux_disponibles = [(t.strftime('%H:%M'), f"{t.strftime('%Hh%M')}") for t in creneaux_disponibles_obj]
        except (ValueError, TypeError):
            messages.error(request, "Format de date invalide.")
            date_selectionnee_str = None

    if request.method == 'POST':
        form = SeanceForm(request.POST, creneaux=creneaux_disponibles)
        if form.is_valid():
            seance = form.save(commit=False)
            seance.client = request.user
            seance.coach = coach
            seance.save() # Le formulaire gère déjà la conversion des champs
            messages.success(request, 'Votre rendez-vous a été pris avec succès !')
            return redirect('dashboard')
    else:
        # Gérer la logique de déplacement pour pré-remplir le sujet
        reschedule_id = request.GET.get('reschedule_id')
        initial_data = {}
        if reschedule_id:
            seance_a_deplacer = get_object_or_404(Seance, pk=reschedule_id, client=request.user)
            initial_data['sujet'] = seance_a_deplacer.sujet
        if date_selectionnee_str:
            initial_data['date'] = date_selectionnee_str
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

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Pour l'instant, on affiche les données dans la console.
            # Plus tard, on pourrait envoyer un email ici.
            print("Nouveau message de contact :")
            print(f"Nom: {form.cleaned_data['nom']}")
            print(f"Email: {form.cleaned_data['email']}")
            print(f"Message: {form.cleaned_data['message']}")
            messages.success(request, 'Votre message a bien été envoyé ! Nous vous répondrons bientôt.')
            return redirect('home')
    else:
        form = ContactForm()

    return render(request, 'coaching/contact.html', {'form': form})