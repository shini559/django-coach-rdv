from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('prendre-rdv/', views.prise_rdv, name='prendre-rdv'),
]