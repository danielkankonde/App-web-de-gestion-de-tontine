from django.contrib import admin
from .models import Utilisateur


# Register your models here.

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')

admin.site.register(Utilisateur, UtilisateurAdmin)