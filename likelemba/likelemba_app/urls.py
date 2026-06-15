from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),

    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/membre/', dashboard_membre, name='dashboard_membre'),

    path('groupes/', liste_groupes_view, name="liste_groupes"),
    path('groupes/create_groupe/', create_groupe, name='create_groupe'),
    path('groupes/<int:id>/update/', update_groupe, name='update_groupe'),
    path('groupes/<int:id>/delete/', delete_groupe, name='delete_groupe'),
    path('groupes/<int:id>/', detail_groupe, name='detail_groupe'),
    path('groupes/<int:groupe_id>/dashboard/', dashboard_financier_view,name='dashboard_financier'),

    path('membres/', liste_membres_view, name='liste_membres'),
    path('groupes/<int:groupe_id>/membres/', membres_groupe_view, name='membres_groupe'),
    path('groupes/<int:groupe_id>/membres/add/', ajouter_membre, name='ajouter_membre'),
    path('membres/<int:id>/delete/', supprimer_membre, name='supprimer_membre'),
    path('membres/<int:id>/ordre/', modifier_ordre_membre, name='modifier_ordre_membre'),

    path('paiements/', liste_paiements_groupes_view, name='liste_groupes_paiements'),
    path('groupes/<int:groupe_id>/paiements/', paiements_groupe_view, name='paiements_groupe'),
    path('groupes/<int:groupe_id>/paiements/add/', ajouter_paiement, name='ajouter_paiement'),

    path('tours/', liste_tours_groupes_view, name='liste_groupes_tours'),
    path('groupes/<int:groupe_id>/tours/', liste_tours_view, name='liste_tours'),
    path('groupes/<int:groupe_id>/tours/generer/', lancer_tours, name='lancer_tours'),

]
