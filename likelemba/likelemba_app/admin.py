from django.contrib import admin
from .models import *

admin.site.register(Utilisateur)
admin.site.register(Groupe)
admin.site.register(MembreGroupe)
admin.site.register(Paiement)
admin.site.register(Tour)