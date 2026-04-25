from django.contrib import admin
from .models import *
from django.contrib import admin


class GroupeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'montant_cotisation', 'frequence', 'date_debut', 'statut', 'date_creation', 'admin']

admin.site.register(Groupe, GroupeAdmin)

class MembreAdmin(admin.ModelAdmin):
    list_display = ['nom_affiche', 'utilisateur', 'groupe', 'ordre_reception']

admin.site.register(MembreGroupe, MembreAdmin)

class PaiementAdmin(admin.ModelAdmin):
    list_display = ['membre', 'montant', 'date_paiement', 'statut']
admin.site.register(Paiement, PaiementAdmin)

class TourAdmin(admin.ModelAdmin):
    list_display = ['groupe', 'numero_tour', 'beneficiaire', 'date_tour', 'completed']

admin.site.register(Tour, TourAdmin)
