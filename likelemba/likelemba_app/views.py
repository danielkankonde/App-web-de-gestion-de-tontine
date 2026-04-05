from django.shortcuts import redirect, render
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import GroupeForm

# Create your views here.
@login_required(login_url="login")
def dashboard(request):

    context = {
        'total_utilisateurs': Utilisateur.objects.count(),
        'total_groupes': Groupe.objects.count(),
        'total_paiements': Paiement.objects.count(),
        'total_tours': Tour.objects.count(),
    }
    return render(request, 'pages/dashboard.html', context)

@login_required
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

@login_required
def dashboard_membre(request):

    if request.user.role != 'MEMBRE':
        return redirect('dashboard_admin')

    return render(request, 'pages/dashboard_membre.html')

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

def liste_groupes_view(request):

    if request.user.role != 'ADMIN':
        return redirect("dashboard_membre")
    
    groupes = Groupe.objects.filter(admin=request.user)
    return render(request, "groupes/liste_groupes.html", {'groupes': groupes})