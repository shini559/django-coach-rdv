from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('prendre-rdv/', views.prise_rdv, name='prendre-rdv'),
    path('seance/<int:pk>/edit/', views.seance_edit, name='seance-edit'),
    path('seance/<int:pk>/', views.seance_detail, name='seance-detail'),
]