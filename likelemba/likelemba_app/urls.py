from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),

    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/membre/', dashboard_membre, name='dashboard_membre'),

    path('groupes/', liste_groupes_view, name="liste_groupes"),
    path('groupes/create_groupe/', create_groupe, name='create_groupe'),
]
