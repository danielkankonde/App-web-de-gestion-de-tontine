from django.shortcuts import render
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
