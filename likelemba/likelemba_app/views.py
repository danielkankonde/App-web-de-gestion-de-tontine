from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .forms import GroupeForm, MembreGroupeForm, OrdreMembreForm


# Create your views here.
@login_required
def dashboard(request):

    context = {
        'total_utilisateurs': Utilisateur.objects.count(),
        'total_groupes': Groupe.objects.count(),
        'total_paiements': Paiement.objects.count(),
        'total_tours': Tour.objects.count(),
    }
    return render(request, 'pages/dashboard.html', context)

@login_required(login_url="login")
def dashboard_admin(request):

    if request.user.role != 'ADMIN':
        return redirect('dashboard_membre')
    
    context = {
            'membres': MembreGroupe.objects.count(),
            'total_groupes': Groupe.objects.count(),
            'total_paiements': Paiement.objects.count(),
            'total_tours': Tour.objects.count(),
    }

    return render(request, 'pages/dashboard_admin.html', context)

@login_required(login_url="login")
def dashboard_membre(request):

    if request.user.role != 'MEMBRE':
        return redirect('dashboard_admin')

    return render(request, 'pages/dashboard_membre.html')

# Fonction pour afficher la liste de groupes
@login_required
def liste_groupes_view(request):

    if request.user.role != 'ADMIN':
        return redirect("dashboard_membre")
    
    groupes = Groupe.objects.filter(admin=request.user)
    return render(request, "groupes/liste_groupes.html", {'groupes': groupes})

#Fonction pour ajouter un groupe
@login_required(login_url="login")
def create_groupe(request):

    # Vérification ADMIN pour la sécurité 
    if request.user.role != 'ADMIN':
        return redirect('dashboard_membre')

    form = GroupeForm()

    if request.method == 'POST':
        form = GroupeForm(request.POST)

        if form.is_valid():

            groupe = form.save(commit=False)

            # Pour éviter que le groupe soit créé sans admin, on assigne l'admin avant de sauvegarder
            groupe.admin = request.user

            groupe.save()

            messages.success(request, "Groupe créé avec succès ✅")

            return redirect('liste_groupes')

        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire")

    return render(request, 'groupes/create_groupe.html', {
        'form': form
    })

# Fonction pour modifier un groupe
@login_required(login_url="login")
def update_groupe(request, id):

    groupe = get_object_or_404(Groupe, id=id, admin=request.user)

    form = GroupeForm(instance=groupe)

    if request.method == 'POST':
        form = GroupeForm(request.POST, instance=groupe)

        if form.is_valid():
            form.save()
            messages.success(request, "Groupe modifié avec succès ✅")
            return redirect('liste_groupes')
        else:
            messages.error(request, "Erreur lors de la modification ❌")

    return render(request, 'groupes/update_groupe.html', {
        'form': form
    })
# Fonction pour supprimer un groupe
@login_required(login_url="login")
def delete_groupe(request, id):

    groupe = get_object_or_404(Groupe, id=id, admin=request.user)

    if request.method == 'POST':
        groupe.delete()
        messages.success(request, "Groupe supprimé avec succès 🗑")
        return redirect('liste_groupes')

    return redirect('liste_groupes')

# Fonction pour voir detail d'un groupe
@login_required(login_url="login")
def detail_groupe(request, id):

    groupe = get_object_or_404(Groupe, id=id, admin=request.user)

    return render(request, 'groupes/detail_groupe.html', {
        'groupe': groupe
    })
@login_required(login_url="login")
def ajouter_membre(request, groupe_id):
    groupe = get_object_or_404(Groupe, id=groupe_id, admin=request.user)

    if request.method == 'POST':
        form = MembreGroupeForm(request.POST, groupe=groupe)

        if form.is_valid():
            membre = form.save(commit=False)
            membre.groupe = groupe

            # 🔐 éviter doublon
            if membre.utilisateur and MembreGroupe.objects.filter(utilisateur=membre.utilisateur, groupe=groupe).exists():
                messages.error(request, "Ce membre est déjà dans le groupe")
                return redirect('ajouter_membre', groupe_id=groupe.id)

            membre.save()
            messages.success(request, "Membre ajouté avec succès")
            return redirect('membres_groupe', groupe_id=groupe.id)
    else:
        form = MembreGroupeForm(groupe=groupe)

    return render(request, 'membres/ajouter.html', {
        'form': form,
        'groupe': groupe
    })

@login_required(login_url="login")
def liste_membres_view(request):
    if request.user.role != 'ADMIN':
        return redirect('dashboard_membre')
    
    groupes = Groupe.objects.filter(admin=request.user).annotate(
        total_membres=Count('membregroupe')
    )

    return render(request, 'membres/liste_membres.html', {
        'groupes': groupes
    })

@login_required(login_url="login")
def membres_groupe_view(request, groupe_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard_membre')

    groupe = get_object_or_404(Groupe, id=groupe_id, admin=request.user)
    membres = MembreGroupe.objects.filter(groupe=groupe).order_by('ordre_reception', 'id')

    return render(request, 'membres/membres_groupe.html', {
        'groupe': groupe,
        'membres': membres
    })

@login_required(login_url="login")
def supprimer_membre(request, id):
    membre = get_object_or_404(
        MembreGroupe,
        id=id,
        groupe__admin=request.user  # 🔐 sécurité
    )

    if request.method == 'POST':
        groupe_id = membre.groupe.id
        membre.delete()
        messages.success(request, "Membre supprimé")
        return redirect('membres_groupe', groupe_id=groupe_id)

@login_required(login_url="login")
def modifier_ordre_membre(request, id):
    membre = get_object_or_404(
        MembreGroupe,
        id=id,
        groupe__admin=request.user  # 🔐 sécurité
    )

    if request.method == 'POST':
        form = OrdreMembreForm(request.POST, instance=membre, groupe=membre.groupe)

        if form.is_valid():
            form.save()
            messages.success(request, "Ordre modifié avec succès")
            return redirect('membres_groupe', groupe_id=membre.groupe.id)
    else:
        form = OrdreMembreForm(instance=membre, groupe=membre.groupe)

    return render(request, 'membres/modifier_ordre.html', {
        'form': form,
        'membre': membre
    })
