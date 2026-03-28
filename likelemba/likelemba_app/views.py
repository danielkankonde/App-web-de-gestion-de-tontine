from django.shortcuts import redirect, render
from .models import *
from django.contrib.auth.decorators import login_required

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