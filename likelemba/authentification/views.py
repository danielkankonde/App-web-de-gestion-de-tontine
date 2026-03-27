from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from .models import Utilisateur, OTP

# Fonction pour se connecter
def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html')

# Fonction pour la créer un compte
def register_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        telephone = request.POST.get('telephone')
        photo = request.FILES.get('photo')

        # 🔴 Validation mot de passe
        if password != confirm_password:
            return render(request, 'register.html', {
                'error': "Les mots de passe ne correspondent pas"
            })

        # 🔴 Vérifier username déjà existant
        if Utilisateur.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': "Nom d'utilisateur déjà utilisé"
            })

        # 🔴 Vérifier email déjà existant
        if Utilisateur.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': "Email déjà utilisé"
            })

        # ✅ Création utilisateur
        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.telephone = telephone
        user.photo = photo
        user.is_active = False
        user.save()

        # 🔐 OTP
        otp = OTP.objects.create(user=user)
        otp.generate_code()

        send_mail(
            'Code de vérification',
            f'Votre code est : {otp.code}',
            'test@gmail.com',
            [email],
        )

        request.session['user_id'] = user.id

        return redirect('verify')

    return render(request, 'register.html')

# Fonction pour la verification du code OTP
def verify_view(request):

    user_id = request.session.get('user_id')

    if request.method == 'POST':

        code = request.POST.get('code')

        otp = OTP.objects.filter(user_id=user_id, code=code).last()

        if otp:
            user = otp.user
            user.is_active = True
            user.is_verified = True
            user.save()

            return redirect('login')
        else:
            return render(request, 'verify.html', {
                'error': 'Code invalide'
            })

    return render(request, 'verify.html')