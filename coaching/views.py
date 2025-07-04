from django.shortcuts import render

def home(request):
    """
    Afficher la page d'accueil du site de coaching.
    :param request:
    :return:
    """
    return render(request, 'coaching/accueil.html')